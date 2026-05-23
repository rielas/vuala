from enum import Enum
from langchain_core.pydantic_v1 import BaseModel, Field
from .exchange import Request


class ConclusionEnum(Enum):
    NEXT_REQUEST = "next_request"
    VULNERABILITY_FOUND = "vulnerability_found"
    VULNERABILITY_NOT_FOUND = "vulnerability_not_found"


class Conclusion(BaseModel):
    observation: str = Field(description="Describe how test case was executed")
    reasoning: str
    enum: ConclusionEnum
    request: Request | None

    def markdown(self) -> str:
        markdown_str = ""

        if self.enum == ConclusionEnum.NEXT_REQUEST:
            markdown_str = "### ⏭️ New request is required\n\n"
            markdown_str += self.request.markdown()
        elif self.enum == ConclusionEnum.VULNERABILITY_FOUND:
            markdown_str = "### 🚨 Vulnerability detected\n\n"
        elif self.enum == ConclusionEnum.VULNERABILITY_NOT_FOUND:
            markdown_str = "### ✅ No vulnerability\n\n"

        markdown_str += "### Reasoning\n\n"
        markdown_str += f"{self.reasoning}\n\n"

        return markdown_str + "\n"
