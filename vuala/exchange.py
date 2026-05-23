from langchain_core.pydantic_v1 import BaseModel, Field
from dataclasses import dataclass
from typing import Any

import mock as mock


class Request(BaseModel):
    expected_result: str
    path: str = Field(description="URL path with query parameters")
    method: str
    body: dict = {}

    def markdown(self, number: int | None = None) -> str:
        number_str = f"{number}. " if number is not None else ""
        markdown_str = f"```\n➡️ {number_str}{self.method} {self.path}\n"
        markdown_str += f"\n{self.body}\n```\n"
        markdown_str += f"Expected result: *{self.expected_result}*\n\n"
        return markdown_str + "\n"


@dataclass
class Response:
    status_code: int
    body: dict

    @classmethod
    def compose(cls, response: mock.Response) -> "Response":
        return Response(status_code=response.status_code, body=response.content)


@dataclass
class Exchange:
    request: Request
    response: Response

    @classmethod
    def compose(cls, request: Request, response: Any) -> "Exchange":
        response = Response.compose(response)
        return Exchange(request=request, response=response)

    def markdown(self, number: int | None = None) -> str:
        import json

        number_str = f"{number}. " if number is not None else ""
        markdown_str = f"```\n➡️ {number_str}{self.request.method} {self.request.path}\n"
        markdown_str += f"\n{self.request.body}\n```\n"

        if "<html>" in self.response.body:
            markdown_str += (
                f"```html\n⬅️ {self.response.status_code}\n{self.response.body}\n```\n"
            )
        else:
            markdown_str += f"```json\n⬅️ {self.response.status_code}\n{json.dumps(self.response.body, indent=2)}\n```\n"

        return markdown_str + "\n"
