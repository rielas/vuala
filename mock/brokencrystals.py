from mock import Mock, Response
import pprint

pp = pprint.PrettyPrinter(indent=4)


class Mock(Mock):
    def __init__(self, domain: str):
        super().__init__(domain)
        self.last_user = None
        self.authorized = False


class User:
    def __init__(
        self,
        email: str,
        firstName: str,
        lastName: str,
        company: str,
        phoneNumber: str,
        password: str,
        op: str,
        isAdmin: bool = False,
    ):
        self.email = email
        self.firstName = firstName
        self.lastName = lastName
        self.company = company
        self.phoneNumber = phoneNumber
        self.password = password
        self.op = op
        self.isAdmin = isAdmin


@Mock.route("/api/users/basic", method="POST")
def _(self, query: dict, data: dict):
    user = User(**data)
    self.last_user = user
    return Response({}, 201)


@Mock.route("/api/auth/login", method="POST")
def _(self, query: dict, data: dict):
    self.authorized = False

    try:
        email = data["user"]
    except KeyError:
        return Response(
            {
                "error": "User not found",
            },
            500,
        )

    password = data["password"]

    if set(data.keys()) != {"user", "password"}:
        return Response(
            {
                "error": "Invalid request data",
            },
            500,
        )

    if self.last_user:
        user = self.last_user

        if user.email == email and user.password == password:
            self.authorized = True
            return Response(
                {"email": user.email},
                201,
            )

    return Response(
        {
            "error": "User not found",
            "location": "/var/www/dist/auth/auth.controller.js",
        },
        500,
    )


@Mock.route("/api/users/one/<str:email>", method="GET")
def _(self, query: dict, data: dict, email: str):
    user = self.last_user

    if user.email == email:
        return Response(
            {
                "id": len(user.email),
                "email": user.email,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "company": user.company,
                "phoneNumber": user.phoneNumber,
            },
            200,
        )

    return Response(
        {
            "error": "User not found",
            "location": "/var/www/dist/auth/auth.controller.js",
        },
        500,
    )


@Mock.route("/api/users/me", method="GET")
def _(self, query: dict, data: dict):
    if not self.authorized:
        return Response(
            {"error": "Unauthorized", "line": "/var/www/dist/auth/auth.guard.js"},
            401,
        )

    user = self.last_user
    return Response(
        {
            "email": user.email,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "company": user.company,
            "phoneNumber": user.phoneNumber,
            "op": user.op,
            "isAdmin": user.isAdmin,
        },
        200,
    )


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
            {
                "user": "robo.ruckus@brightsec.com",
                "password": "000",
            },
        ).status_code
        == 201
    )

    assert (
        mock.make_request("GET", "/api/users/one/robo.ruckus@brightsec.com").status_code
        == 200
    )

    assert mock.make_request("GET", "/api/users/me").content["isAdmin"] is False

    return mock.har()


def main():
    har()


if __name__ == "__main__":
    main()
