from langchain_core.pydantic_v1 import BaseModel
from typing import List


class TestPlan(BaseModel):
    description: str
    test_steps: List[str]
    sign_of_vulnerability_presence: str

    def markdown(self, number: int | None = None) -> str:
        number_str = f"{number}. " if number is not None else ""
        markdown_str = f"### 💡 {number_str}{self.description}\n\n"
        markdown_str += f"> {self.sign_of_vulnerability_presence}\n\n"
        markdown_str += "**Test steps:**\n\n"

        for i, test_step in enumerate(self.test_steps):
            markdown_str += f"{i + 1}. {test_step}\n\n"

        return markdown_str + "\n"


class TestPlans(BaseModel):
    test_plans: List[TestPlan]

    def markdown(self, number: int | None = None) -> str:
        number_str = f"{number}. " if number is not None else ""
        markdown_str = f"### {number_str}Test Plans\n\n"
        markdown_str += "\n".join(
            [test_plan.markdown(i + 1) for i, test_plan in enumerate(self.test_plans)]
        )
        return markdown_str + "\n"

    def __getitem__(self, key: int) -> TestPlan:
        return self.test_plans[key]
