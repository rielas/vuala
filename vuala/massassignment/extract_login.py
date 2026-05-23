from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from vuala.massassignment.common import (
    Entry,
    MODEL,
    TEMPERATURE,
)
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List


class RelevantEntries(BaseModel):
    """Relevant requests and responses for the mass assignment vulnerability
    investigation."""

    permission_verification: str = Field(
        description="Describe here how the permissions are verified"
    )

    entries: List[Entry] = Field(
        description="Relevant requests and responses for the mass assignment vulnerability investigation."
    )


prompt = ChatPromptTemplate.from_template(
    """
    You are an agent, which tests login functionality for vulnerabilities.
                        
    Based on provided history of HTTP requests, select the requests that are
    relevant to the signing up, login and permissions verification process.

    {input}
    """
)


model = prompt | ChatOpenAI(
    model=MODEL, temperature=TEMPERATURE, verbose=True
).with_structured_output(RelevantEntries)


def invoke(har: list) -> RelevantEntries:
    relevant: RelevantEntries = model.invoke(har)
    return relevant
