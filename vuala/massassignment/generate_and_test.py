from attr import dataclass
from vuala.massassignment.common import _get_unique_email
from typing import List
from enum import Enum
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from vuala.massassignment.common import (
    Request,
    MODEL,
    TEMPERATURE,
    Client,
    Entry,
    Response,
    Resource,
)
from langchain_core.pydantic_v1 import BaseModel, Field
import json


class Scenario(BaseModel):
    modification: str = Field(
        description="""
Description of which request and how to be modified in format. Provide only one
field in JSON
POST /endpoint ("only_single_key": "value")
"""
    )
    expected_result: str
    requests: List[Request]


scenario_prompt = ChatPromptTemplate.from_template(
    """
You are an agent tasked with researching mass assignment vulnerabilities. Mass
assignment vulnerabilities occur when an API or application allows an attacker
to modify object properties that they shouldn't have access to by including
them in a request payload.

Given the following example of a successful login process:

{reproduced}

It presumably contains following REST API resources:

{resources}

Permissions are verified during the login process:

{permission_verification}

Previous attempts were unsuccessful in demonstrating a mass assignment. Don't
repeat them.

---

# Failed scenarios

{failed_attempts}

---

Compose a scenario that demonstrates a mass assignment vulnerability. Make sure,
that all this requests present in the composed scenario. Provide a sequence of
HTTP requests that exploit this vulnerability, focusing on:

- Identifying hidden or sensitive fields that could be manipulated (e.g., user
roles, permissions, or any fields not intended for user modification).

- Don't use fields and values, which already failed in failed scenarios.

- Don't use fields which are already present in the same request in baseline.

- Put your attention to the fields, which present in the same resource, but
aren't present in the request. Also, you can use fields from other resources, if
they are related.

- Demonstrating how an attacker could escalate privileges or gain unauthorized
access.

Consider focusing on fields or any other properties that might grant elevated
permissions or access. Add only one field at a time. Provide this field in
`modification` and use it in the request.

Use unique email address for the session: {unique_email}
"""
)

scenario_model = scenario_prompt | ChatOpenAI(
    model=MODEL, temperature=TEMPERATURE, verbose=True
).with_structured_output(Scenario)

reasoning_prompt = ChatPromptTemplate.from_template(
    """
You are an agent tasked with researching mass assignment vulnerabilities. Mass
assignment vulnerabilities occur when an API or application allows an attacker
to modify object properties that they shouldn't have access to by including
them in a request payload.

### Baseline requests and responses

{baseline}

### Requests and responses from the current session

{entries}

Analize this session to understand if the vulnerability was successfully
demonstrated. Provide reasoning for your conclusion. Take into account:

- Vulnerability is present only if you can demonstrate additional permissions,
which are not present in the baseline.

- Vulnerability is present only if the field was accepted by the server.

- Vulnerability is present only if the patched field key was not present in the
baseline request baseline and was introduced in the current session.
"""
)


class MassAssignmentPresence(str, Enum):
    present = "present"
    not_present = "not_present"


class ReasoningMassAssignmentPresence(BaseModel):
    description: str = Field(
        description='How attempt looked like. Provide which field was modified \
        in format {{"field":"value"}}.'
    )
    reasoning: str
    presence: MassAssignmentPresence


reasoning_model = reasoning_prompt | ChatOpenAI(
    model=MODEL, temperature=TEMPERATURE, verbose=True
).with_structured_output(ReasoningMassAssignmentPresence)


@dataclass
class Exploit:
    description: str
    entries: List[Entry]

    def markdown(self) -> str:
        markdown_str = f"{self.description}\n"

        for entry in self.entries:
            markdown_str += entry.markdown()

        return markdown_str


def invoke(
    client: Client,
    reproduced: List[Entry],
    permission_verification: str,
    resources: list[Resource],
) -> Exploit:
    failed_attempts = []

    while True:
        scenario: Scenario = scenario_model.invoke(
            input={
                "reproduced": reproduced,
                "unique_email": _get_unique_email(),
                "failed_attempts": failed_attempts,
                "permission_verification": permission_verification,
                "resources": resources,
            }
        )

        entries = []

        for request in scenario.requests:
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
            entries.append(entry)

            if response.status_code in [400, 500]:
                break

        reasoning: ReasoningMassAssignmentPresence = reasoning_model.invoke(
            input={"entries": entries, "baseline": reproduced}
        )

        if reasoning.presence == MassAssignmentPresence.present:
            break
        else:
            failed_attempts.append(scenario.modification)

    return Exploit(description=reasoning.description, entries=entries)
