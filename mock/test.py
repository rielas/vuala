import unittest
from . import Mock, Response

mock = Mock("domain.com")


@Mock.route("/account/<str:owner>/balance", method="GET")
def balance(self, query: dict, data: dict, owner: str):
    return Response({"balance": 100})


@Mock.route("/account/<str:owner>/deposit", method="POST")
def deposit(self, query: dict, data: dict, owner: str):
    return Response({"balance": data["amount"]})


@Mock.route("/account/<str:owner>/withdraw", method="POST")
def withdraw(self, query: dict, data: dict, owner: str):
    return Response({"balance": 100})


@Mock.route("/product", method="GET")
def product(self, query: dict, data: dict):
    return Response({"cost": 100})


@Mock.route("/account/transfer", method="POST")
def transfer(self, query: dict, data: dict):
    return Response({"balance": 99})


test_entries = [
    ("POST", "/account/transfer", {}, Response({"balance": 99})),
    ("POST", "/account/alice/withdraw", {}, Response({"balance": 100})),
    ("POST", "/account/12/withdraw", {}, Response({"balance": 100})),
    (
        "POST",
        "/account/bob/deposit",
        {"amount": 100},
        Response({"balance": 100}),
    ),
    ("GET", "/account/alice/balance", {}, Response({"balance": 100})),
    (
        "GET",
        "/account/alice/unknown",
        {},
        Response({"message": "route not found"}, 404),
    ),
    (
        "GET",
        "/product?productId=1",
        {},
        Response({"cost": 100}),
    ),
]


class TestMockRoutes(unittest.TestCase):
    def test_routes(self):
        for entry in test_entries:
            method, path, data, expected_response = entry
            self.assertEqual(mock.make_request(method, path, data), expected_response)

    def test_har(self):
        for entry in test_entries:
            method, path, data, _ = entry
            mock.make_request(method, path, data)

        self.assertEqual(len(mock.har()["log"]["entries"]), len(test_entries))


if __name__ == "__main__":
    unittest.main()
