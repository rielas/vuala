from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Union, List, Dict, Any
import mock
import json
from vuala.output import write_markdown


MODEL = "gpt-4o-mini"
TEMPERATURE = 0.0


class Request(BaseModel):
    method: str = Field(description="HTTP method.")
    path: str = Field(description="HTTP path.")
    query: dict = Field(description="HTTP query parameters.", default={})
    postData: str = Field(description="HTTP POST data in string format.", default="")

    def markdown(self) -> str:
        markdown_str = f"\n➡️ **{self.method}** {self.path}\n"

        if self.postData.strip():
            markdown_str += (
                f"\n```json\n{json.dumps(json.loads(self.postData), indent=2)}\n```\n"
            )
        else:
            markdown_str += "\n"

        return markdown_str + "\n"


class Response(BaseModel):
    content: str = Field(description="HTTP response content")
    status_code: int = Field(description="HTTP response status code.")


class Entry(BaseModel):
    request: Request = Field(description="HTTP request.")
    response: Response = Field(description="HTTP response.")

    def __init__(self, request: Request, response: Response):
        super().__init__(request=request, response=response)

    def markdown(self) -> str:
        markdown_str = f"```\n➡️ {self.request.method} {self.request.path}\n```\n"

        if self.request.postData.strip():
            markdown_str += f"""
```json
{json.dumps(json.loads(self.request.postData), indent=2)}
```
"""

        markdown_str += f"⬅️ {self.response.status_code}\n"
        markdown_str += f"""
```json
{json.dumps(json.loads(self.response.content), indent=2)}
```
"""

        return markdown_str + "\n"


class NextRequest(BaseModel):
    reasoning: str = Field(description="Reasoning for the next request.")
    request: Request


class Success(BaseModel):
    success_reasoning: str


class Failure(BaseModel):
    failure_reasoning: str


class NextStep(BaseModel):
    reasoning: str
    output: Union[NextRequest, Success, Failure]


class Resource(BaseModel):
    """REST API resource"""

    name: str = Field(description="Resource name.")
    fields: List[str] = Field(description="Resource fields.")


def _get_unique_email() -> str:
    import random

    adjectives = ["bold", "odd", "rich"]

    nouns = ["bird", "moth", "gecko"]

    adjective = random.choice(adjectives)
    noun = random.choice(nouns)

    return f"admin-{adjective}-{noun}@brightsec.com"


class Client:
    def __init__(self, client: mock.Mock):
        self.client = client

    def make_request(self, method: str, path: str, post_data: str) -> mock.Response:
        if post_data.strip():
            data = json.loads(post_data)
        else:
            data = {}

        markdown_data = f"```json\n{post_data}\n```" if post_data.strip() else ""

        write_markdown(
            f"""
Making a **{method}** *{path}* request
{markdown_data}
"""
        )

        response = self.client.make_request(method, path, data)
        write_markdown(
            f"""
Response status: **{response.status_code}**

```json
{json.dumps(response.content, indent=2)}
```
"""
        )
        return response


def standard_har() -> tuple[dict, Client]:
    import mock.brokencrystals as brokencrystals

    return (brokencrystals.har(), Client(brokencrystals.Mock("brokencrystals.com")))


def portuguese_har() -> tuple[dict, Client]:
    import mock.massassignment.portuguese as brokencrystals

    return (brokencrystals.har(), Client(brokencrystals.Mock("brokencrystals.com")))


def scopes_har() -> tuple[dict, Client]:
    import mock.massassignment.scopes as brokencrystals

    return (brokencrystals.har(), Client(brokencrystals.Mock("brokencrystals.com")))


def markdown_har(har: Dict[str, Any]) -> str:
    def format_json(data: Dict[str, Any]) -> str:
        return json.dumps(data, indent=2)

    markdown = ""

    for idx, entry in enumerate(har["log"]["entries"], 1):
        request = entry["request"]
        response = entry["response"]
        markdown += f"```\n➡️ {idx}. {request['method']} {request['path']}\n```\n"

        if request["postData"]:
            markdown += f"\n```json\n{json.dumps(request['postData'], indent=2)}\n```\n"

        content_type = response.get("content", {}).get("mimeType", "")

        if content_type == "text/html":
            markdown += f"```html\n⬅️ {response['status']}\n{response['content'].get('text', '')}\n```\n"
        else:
            markdown += f"```json\n⬅️ {response['status']}\n{format_json(response['content'])}\n```\n"

        markdown += "\n"

    return markdown.strip()
