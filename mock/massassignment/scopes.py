import pprint
import mock.brokencrystals as brokencrystals
from mock.brokencrystals import Mock, Response
from typing import List

pp = pprint.PrettyPrinter(indent=4)


class User(brokencrystals.User):
    def __init__(
        self,
        email: str,
        firstName: str,
        lastName: str,
        company: str,
        phoneNumber: str,
        password: str,
        op: str,
        scopes: List[str] = ["user:read", "user:write"],
    ):
        super().__init__(
            email,
            firstName,
            lastName,
            company,
            phoneNumber,
            password,
            op,
            False,
        )
        self.scopes = scopes


Mock.delete_route("/api/users/one/<str:email>/adminpermission", method="GET")

Mock.delete_route("/api/users/basic", method="POST")


@Mock.route("/api/users/basic", method="POST")
def _(self, query: dict, data: dict):
    try:
        user = User(**data)
    except TypeError:
        return Response({"error": "Wrong fields"}, 500)

    self.last_user = user
    return Response({}, 201)


@Mock.route("/api/users/me", method="GET")
def _(self, query: dict, data: dict):
    if not self.authorized:
        return Response(
            {"error": "Unauthorized", "line": "/var/www/dist/auth/auth.guard.js"},
            401,
        )

    if self.last_user:
        found_user = self.last_user
    else:
        return Response({}, 404)

    if found_user:
        return Response(
            {
                "email": found_user.email,
                "firstName": found_user.firstName,
                "lastName": found_user.lastName,
                "company": found_user.company,
                "phoneNumber": found_user.phoneNumber,
                "scopes": found_user.scopes,
            },
            200,
        )

    return Response({}, 404)


def har() -> dict:
    mock = Mock("brokencrystals.com")

    assert (
        mock.make_request(
            "POST",
            "/api/users/basic",
            {
                "email": "robo.ruckus@brightsec.com",
                "firstName": "",
                "lastName": "",
                "company": "",
                "phoneNumber": "",
                "password": "000",
                "op": "basic",
            },
        ).status_code
        == 201
    )
    assert (
        mock.make_request(
            "POST",
            "/api/auth/login",
            {"user": "robo.ruckus@brightsec.com", "password": "000"},
        ).status_code
        == 201
    )

    assert mock.make_request("GET", "/api/users/me").status_code == 200
    assert mock.make_request("GET", "/api/users/me").content["scopes"] == [
        "user:read",
        "user:write",
    ]

    return mock.har()


def main():
    har()


if __name__ == "__main__":
    main()
