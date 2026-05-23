from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List


class Workflow(BaseModel):
    """Workflow of the business logic scenario"""

    title: str = Field(description="Title of the workflow")
    description: str = Field(description="Description of the workflow")
    relevant_requests_ids: List[int] = Field(description="Relevant requests")
    preceding_requests_ids: List[int] = Field(
        description="Requests which have be executed before"
    )
    can_be_vulnerable: bool = Field(
        description="Flag if the workflow can be vulnerable"
    )

    def markdown(self, number: int | None = None) -> str:
        number_str = f"{number}. " if number is not None else ""
        markdown_str = f"### {number_str}{self.title}\n\n"
        markdown_str += f"{self.description}\n\n"
        markdown_str += f"- Relevant requests IDs: {self.relevant_requests_ids}\n"
        markdown_str += f"- Preceding requests IDs: {self.preceding_requests_ids}\n"
        markdown_str += f"- Can be vulnerable: *{self.can_be_vulnerable}*\n"
        return markdown_str + "\n"


class Workflows(BaseModel):
    """List of workflows of the business logic scenarios"""

    workflows: List[Workflow] = Field(description="List of business logic workflows")

    def markdown(self, number: int | None = None) -> str:
        number_str = f"{number}. " if number is not None else ""
        markdown_str = f"### {number_str}Workflows\n\n"
        markdown_str += "\n".join(
            [workflow.markdown(i + 1) for i, workflow in enumerate(self.workflows)]
        )
        return markdown_str + "\n"

    def __getitem__(self, key: int) -> Workflow:
        return self.workflows[key]
