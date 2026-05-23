#!/usr/bin/env python

import re
import functools

from attr import dataclass
from typing import List
from urllib.parse import parse_qs
import siteclient


@dataclass
class Response:
    content: dict
    status_code: int = 200

    def __str__(self):
        return f"Response(status_code={self.status_code}, data={self.content})"

    def __repr__(self) -> str:
        return f"Response(status_code={self.status_code}, data={self.content})"

    def __eq__(self, other) -> bool:
        return self.status_code == other.status_code and self.content == other.content


@dataclass
class Request:
    method: str
    path: str
    query: dict
    postData: dict


@dataclass
class Entry:
    request: Request
    response: Response


class Mock(siteclient.WebsiteClient):
    routes = []

    def __init__(self, domain: str):
        self.domain = domain
        self.entries: List[Entry] = []

    @classmethod
    def route(cls, path, method):
        def decorator(func):
            assert path.startswith("/")

            name = re.sub(r"\W|^(?=\d)", "_", path + "_" + method).lower()
            func.__name__ = name
            path_regex = re.sub(r"<str:(\w+)>", r"(?P<\1>[^/]+)", path)
            cls.routes.append((re.compile(f"^{path_regex}$"), method, func))

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    @classmethod
    def delete_route(cls, path, method):
        """
        Delete a route based on its path and method.

        :param path: The path of the route to delete
        :param method: The HTTP method of the route to delete
        :return: True if a route was deleted, False otherwise
        """
        path_regex = re.sub(r"<str:(\w+)>", r"(?P<\1>[^/]+)", path)
        compiled_regex = re.compile(f"^{path_regex}$")

        for i, (existing_regex, existing_method, func) in enumerate(cls.routes):
            if (
                existing_regex.pattern == compiled_regex.pattern
                and existing_method == method
            ):
                del cls.routes[i]
                return True

        return False

    def make_request(self, method: str, path: str, data: dict = {}) -> Response:
        assert path.startswith("/")

        query = _get_query_object(path)
        endpoint = path.split("?", 1)[0]
        response: Response | None = None

        for path_regex, m, func in self.routes:
            match = path_regex.match(endpoint)

            if match and m == method:
                kwargs = match.groupdict()
                response = func(self, query, data, **kwargs)

        if not response:
            response = Response({"message": "route not found"}, 404)

        url = f"https://{self.domain}{path}"
        print(f"📤 {method} {url}")
        self.entries.append(Entry(Request(method, path, query, data), response))
        print(f"   📥 {response.status_code}\n")
        return response

    def har(self) -> dict:
        return {
            "log": {
                "entries": [
                    {
                        "id": entry_id,
                        "request": {
                            "method": entry.request.method,
                            "path": entry.request.path,
                            "query": entry.request.query,
                            "postData": entry.request.postData,
                        },
                        "response": {
                            "status": entry.response.status_code,
                            "content": entry.response.content,
                        },
                    }
                    for entry_id, entry in enumerate(self.entries)
                ]
            }
        }


def _get_query_object(path: str) -> dict:
    parts = path.split("?", 1)
    query_string = parts[1] if len(parts) > 1 else ""
    query_params = parse_qs(query_string)
    query_object = {k: v[0] for k, v in query_params.items()}
    return query_object
