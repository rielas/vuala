from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from vuala.massassignment.common import MODEL, TEMPERATURE, Resource
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List


class RestResources(BaseModel):
    """Relevant requests and responses for the mass assignment vulnerability
    investigation."""

    resources: List[Resource] = Field(description="Supposed REST API resources.")


prompt = ChatPromptTemplate.from_template(
    """
You are an agent, for restoring REST API.

Try to restore possible REST API resources from the provided HTTP requests.

Some resourses can be used in multiple endpoints with non related paths.

Hidden fields can be present in the resources, which present in some endpoints,
but not in others.

{input}
"""
)


model = prompt | ChatOpenAI(
    model=MODEL, temperature=TEMPERATURE, verbose=True
).with_structured_output(RestResources)


def invoke(requests: list) -> RestResources:
    resources: RestResources = model.invoke(requests)
    return resources
