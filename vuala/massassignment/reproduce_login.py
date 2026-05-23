from vuala.massassignment.common import (
    MODEL,
    TEMPERATURE,
    Success,
    Failure,
    Response,
    _get_unique_email,
    Entry,
    NextStep,
    NextRequest,
    Client
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import json

no_executed_requests_prompt = ChatPromptTemplate.from_template(
    """
You are an agent that needs to reproduce the login and permissions verification process.

These are the baseline requests and responses from the previous session:
{baseline}

Use the email address: {email} for this session. No requests have been executed in this session yet. What will be the first request?
"""
)

no_executed_model = no_executed_requests_prompt | ChatOpenAI(
    model=MODEL, temperature=TEMPERATURE, verbose=True
).with_structured_output(NextStep)

executed_requests_prompt = ChatPromptTemplate.from_template(
    """
You are an agent that needs to reproduce the login and permissions verification
process.

These are the baseline requests and responses from the previous session. They
contain sign up and login requests and permissions verification. This requests
and responses aren't relevant for the current session:

{baseline}

Now you have another session. Already executed requests and responses in this
session:

{reproduced}

Check them to determine the next step.

- If permissions are verified provide the Success output. In reasoning provide
permissions description. Make sure, that all requests from the baseline were
executed.

- If the login process failed provide the Failure output.

- If additional requests are needed to complete the login and verify
permissions, provide the NextRequest output.
"""
)

executed_model = executed_requests_prompt | ChatOpenAI(
    model=MODEL, temperature=TEMPERATURE, verbose=True
).with_structured_output(NextStep)


def invoke(client: Client, baseline: list) -> list[Entry]:
    assert len(baseline), "Baseline should not be empty"

    model = None
    reproduced = []
    next_step: NextStep | None = None

    while next_step is None or isinstance(next_step.output, NextRequest):
        if len(reproduced) > 0:
            model = executed_model
        else:
            model = no_executed_model

        next_step = model.invoke(
            input={
                "baseline": baseline,
                "email": _get_unique_email(),
                "reproduced": reproduced,
            }
        )

        match next_step.output:
            case NextRequest(reasoning=reasoning, request=request):
                response = client.make_request(
                    request.method, request.path, request.postData
                )
                entry = Entry(
                    request,
                    Response(
                        content=json.dumps(response.content),
                        status_code=response.status_code,
                    ),
                )
                reproduced += [entry]

            case Failure(failure_reasoning=failure_reasoning):
                raise Exception(f"❌ Failure: {failure_reasoning=}")

            case Success():
                return reproduced
