import os
from typing import Any
from .workflow import Workflow, Workflows
from .test_plan import TestPlan, TestPlans
from .exchange import Exchange, Request
from .conclusion import Conclusion, ConclusionEnum
from langchain_openai import ChatOpenAI
import siteclient
import langfuse.callback
from .output import write_markdown, to_markdown

MODEL = "gpt-4o"
TEMPERATURE = 0


langfuse_handler = langfuse.callback.CallbackHandler(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
    host=os.environ.get("LANGFUSE_HOST", "http://localhost:3000"),
)

llm = ChatOpenAI(model=MODEL, temperature=TEMPERATURE)


def get_workflows(har: dict) -> Workflows:
    print(har)
    content = har
    structured_llm = llm.with_structured_output(Workflows)
    workflows = structured_llm.invoke(
        f"You are a security analyst tasked with identifying business logic workflows in a web application. You have access to the history of HTTP requests and responses for the application. Identify business logic identify that can potentially be vulnerable to exploitation.\n{content}\n. Provide a list of business logic workflows",
        config={"callbacks": [langfuse_handler]},
    )
    return workflows  # type: ignore


def get_history_entry(har: dict, id: int) -> Any:
    return next((entry for entry in har["log"]["entries"] if entry["id"] == id), None)


def get_test_plans(scenario: Workflow, har: dict) -> TestPlans:
    structured_llm = llm.with_structured_output(TestPlans)
    history = har
    relevant_requests_ids = (
        scenario.preceding_requests_ids + scenario.relevant_requests_ids
    )
    relevant_requests = [get_history_entry(har, id_) for id_ in relevant_requests_ids]

    test_plans = structured_llm.invoke(
        f"""
You are an agent for recognizing business logic vulnerabilities, based on history of HTTP requests/responses.

History of HTTP requests/responses which already were executed:
---

{history}

---
There is a business logic scenario: "{scenario.title}" with description:
"{scenario.description}".

Relevant HTTP requests. Use them as a reference for test plans:
---

{relevant_requests}.

---
Provide test plans for business logic vulnerabilities for this scenario. Steps must include verification. Test plan requires description of what kind of request is needed, what is expected result and how to verify vulnerability. After each step, you should provide a conclusion if vulnerability was found or not and provide next request if needed.
You aren't able capture or intercept requests, but you have history of requests/responses for this scenario.

Rules:
- If server accepts malformed requests, it's a vulnerability.
- Avoid testing for vulnerabilities that are not related to business logic.
""",
        config={"callbacks": [langfuse_handler]},
    )
    # print(test_plans)
    write_markdown(test_plans.markdown())

    return test_plans  # type: ignore


class TooManyRequests(Exception):
    pass


class Agent:
    def __init__(
        self,
        scenario: Workflow,
        test_plan: TestPlan,
        har: dict,
        client: siteclient.WebsiteClient,
    ):
        self.scenario = scenario
        self.test_plan = test_plan
        self.exchanges = []
        self.har = har
        self.client = client

    def _make_openai_api_call(self, messages: str, type=Conclusion):
        """
        Make a call to the OpenAI API with the provided messages.
        """

        structured_llm = llm.with_structured_output(type)
        try:
            conclusion = structured_llm.invoke(
                messages, config={"callbacks": [langfuse_handler]}
            )
            return conclusion
        except Exception as e:
            raise RuntimeError(f"Error making OpenAI API call: {e}")

    def _construct_messages(self, intro: str, prompt: str) -> str:
        """
        Construct messages for the OpenAI API call.
        """
        return f"{self._agent_prompt()} {intro}\n{prompt}"

    def _agent_prompt(self) -> str:
        return "You are an agent for recognizing business logic vulnerabilities, based on history of HTTP requests/responses"

    def _intro(self) -> str:
        relevant_requests = self._get_relevant_requests()
        intro_message = f"""
Business logic scenario: "{self.scenario.title}" with description:
"{self.scenario.description}".

---
Relevant HTTP requests/responses from the workflow are:
{relevant_requests}.\n
These requests aren't related to the current session. Use them as a reference\n
---\n
"""
        intro_message += f"\nNow we test workflow according to the following test plan:\n{self.test_plan}."

        if self.exchanges:
            formatted_exchanges = "\n".join(
                [
                    self._format_exchange_for_display(exchange)
                    for exchange in self.exchanges
                ]
            )
            intro_message += "\n---"

            intro_message += f"\nAlready executed HTTP requests and responses in this session:\n{formatted_exchanges}\n"
            intro_message += "\n---\n"

        return intro_message

    def _format_exchange_for_display(self, exchange: Exchange) -> str:
        """
        Format an exchange for display in the introduction message.

        :param exchange: The exchange to format.
        :return: A string representation of the exchange.
        """
        # Implement the logic to format the exchange object into a readable string
        # This is a placeholder implementation
        return f"Request: {exchange.request}\nResponse: {exchange.response}"

    def _first_request_prompt(self) -> str:
        return """
We start testing. There were no requests before.
"""

    def _get_relevant_requests(self) -> list[Any]:
        entries = self.har["log"]["entries"]
        return [entry for entry in entries]

    def first_request(self) -> Request:
        intro = self._intro()
        prompt = self._first_request_prompt()
        messages = self._construct_messages(intro, prompt)
        new_request = self._make_openai_api_call(messages, Request)
        return new_request  # type: ignore

    def _get_reason_prompt(self) -> str:
        return """
Check if already executed requests in this session have achieved the goal of test
case and vulnerability was demonstrated. If you think, that another request is needed,
provide NEXT_REQUEST. If you think, that vulnerability doesn't exist return VULNERABILITY_NOT_FOUND.
If vulnerability was demonstrated, return VULNERABILITY_FOUND.
"""

    def reason(self, exchange: Exchange) -> Conclusion:
        write_markdown("🤔 Reasoning...")

        self.exchanges.append(exchange)
        intro = self._intro()
        prompt = self._get_reason_prompt()

        messages = self._construct_messages(intro, prompt)
        conclusion = self._make_openai_api_call(messages, Conclusion)
        return conclusion  # type: ignore

    def print_conclusion(self, conclusion: Conclusion):
        match conclusion.enum:
            case ConclusionEnum.VULNERABILITY_FOUND:
                markdown_str = (
                    f"### 🚨 Vulnerability detected. {self.test_plan.description}\n\n"
                )
                markdown_str += "### Reasoning\n\n"
                markdown_str += f"{conclusion.reasoning}\n\n"
                markdown_str += to_markdown(self.exchanges)
                markdown_str += "\n"
                write_markdown(markdown_str)
                print("Press any key to continue...")
                input()
                pass
            case _:
                write_markdown(conclusion.markdown())

    def test(self):
        request = self.first_request()
        write_markdown(request.markdown())
        response = self.client.make_request(request.method, request.path, request.body)
        exchange = Exchange.compose(request, response)
        write_markdown(exchange.markdown())

        conclusion = self.reason(exchange)

        request_count = 1

        while conclusion.enum == ConclusionEnum.NEXT_REQUEST:
            if request_count > 3:
                conclusion.enum = ConclusionEnum.VULNERABILITY_NOT_FOUND
                conclusion.reasoning = (
                    "Too many requests were made. Infinite cycle is possible"
                )
                break

            self.print_conclusion(conclusion)
            request = conclusion.request
            response = self.client.make_request(
                request.method, request.path, data=request.body
            )
            exchange = Exchange.compose(request, response)
            write_markdown(exchange.markdown())
            conclusion = self.reason(exchange)
            request_count += 1

        self.print_conclusion(conclusion)
