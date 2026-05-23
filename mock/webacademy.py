import dataclasses
from dataclasses import dataclass
from mock import Mock, Response
import pprint
from typing import List

pp = pprint.PrettyPrinter(indent=4)


class Mock(Mock):
    def __init__(self, domain: str):
        super().__init__(domain)
        self.cart: List[CartItem] = []
        self.store_credit = 10000


@dataclass
class CartItem:
    productId: int
    quantity: int
    price: int


PRODUCTS = [
    {
        "productId": 1,
        "image": "/image/productcatalog/specialproducts/LeetLeatherJacket.jpg",
        "name": "Lightweight 'l33t' Leather Jacket",
        "ratingImage": "/resources/images/rating5.png",
        "price": 133700,
    },
    {
        "productId": 2,
        "image": "/image/productcatalog/products/72.jpg",
        "name": "Baby Minding Shoes",
        "ratingImage": "/resources/images/rating2.png",
        "price": 6047,
    },
    {
        "productId": 3,
        "image": "/image/productcatalog/products/2.jpg",
        "name": "All-in-One Typewriter",
        "ratingImage": "/resources/images/rating2.png",
        "price": 9078,
    },
    {
        "productId": 4,
        "image": "/image/productcatalog/products/40.jpg",
        "name": "Sarcastic 9 Ball",
        "ratingImage": "/resources/images/rating5.png",
        "price": 9070,
    },
    {
        "productId": 5,
        "image": "/image/productcatalog/products/53.jpg",
        "name": "High-End Gift Wrapping",
        "ratingImage": "/resources/images/rating4.png",
        "price": 6018,
    },
    {
        "productId": 6,
        "image": "/image/productcatalog/products/58.jpg",
        "name": "There is No 'I' in Team",
        "ratingImage": "/resources/images/rating1.png",
        "price": 7467,
    },
    {
        "productId": 7,
        "image": "/image/productcatalog/products/12.jpg",
        "name": "Hologram Stand In",
        "ratingImage": "/resources/images/rating2.png",
        "price": 8513,
    },
    {
        "productId": 8,
        "image": "/image/productcatalog/products/16.jpg",
        "name": "Photobomb Backdrops",
        "ratingImage": "/resources/images/rating5.png",
        "price": 9316,
    },
    {
        "productId": 9,
        "image": "/image/productcatalog/products/49.jpg",
        "name": "Roulette Drinking Game",
        "ratingImage": "/resources/images/rating4.png",
        "price": 7615,
    },
    {
        "productId": 10,
        "image": "/image/productcatalog/products/21.jpg",
        "name": "Snow Delivered To Your Door",
        "ratingImage": "/resources/images/rating5.png",
        "price": 3846,
    },
    {
        "productId": 11,
        "image": "/image/productcatalog/products/8.jpg",
        "name": "Folding Gadgets",
        "ratingImage": "/resources/images/rating2.png",
        "price": 1988,
    },
    {
        "productId": 12,
        "image": "/image/productcatalog/products/28.jpg",
        "name": "Vintage Neck Defender",
        "ratingImage": "/resources/images/rating2.png",
        "price": 8059,
    },
    {
        "productId": 13,
        "image": "/image/productcatalog/products/70.jpg",
        "name": "Eye Projectors",
        "ratingImage": "/resources/images/rating3.png",
        "price": 4873,
    },
    {
        "productId": 14,
        "image": "/image/productcatalog/products/68.jpg",
        "name": "What Do You Meme?",
        "ratingImage": "/resources/images/rating5.png",
        "price": 8391,
    },
    {
        "productId": 15,
        "image": "/image/productcatalog/products/7.jpg",
        "name": "Conversation Controlling Lemon",
        "ratingImage": "/resources/images/rating5.png",
        "price": 9627,
    },
    {
        "productId": 16,
        "image": "/image/productcatalog/products/37.jpg",
        "name": "The Giant Enter Key",
        "ratingImage": "/resources/images/rating2.png",
        "price": 7281,
    },
    {
        "productId": 17,
        "image": "/image/productcatalog/products/24.jpg",
        "name": "The Alternative Christmas Tree",
        "ratingImage": "/resources/images/rating4.png",
        "price": 7838,
    },
    {
        "productId": 18,
        "image": "/image/productcatalog/products/47.jpg",
        "name": "3D Voice Assistants",
        "ratingImage": "/resources/images/rating4.png",
        "price": 6982,
    },
    {
        "productId": 19,
        "image": "/image/productcatalog/products/63.jpg",
        "name": "Laser Tag",
        "ratingImage": "/resources/images/rating2.png",
        "price": 6406,
    },
    {
        "productId": 20,
        "image": "/image/productcatalog/products/31.jpg",
        "name": "Couple's Umbrella",
        "ratingImage": "/resources/images/rating3.png",
        "price": 2710,
    },
]


@Mock.route("/product", method="GET")
def _(self, query: dict, data: dict):
    if "productId" not in query:
        return Response({"products": PRODUCTS})

    try:
        productId = int(query["productId"])
    except ValueError:
        productId = 1
    except KeyError:
        return Response({"error": "Key doesn't exist"}, 500)

    product = next((p for p in PRODUCTS if p["productId"] == productId), None)

    if not product:
        return Response({"error": "Product not found"}, 404)

    return Response(product)


@Mock.route("/academyLabHeader", method="GET")
def _(self, query: dict, data: dict):
    return Response({}, 101)


@Mock.route("/cart", method="POST")
def _(self, query: dict, data: dict):
    try:
        product_id = int(query["productId"])
    except KeyError:
        return Response({"error": "Product is missed"}, 500)

    try:
        quantity = int(query["quantity"])
    except ValueError:
        return Response({"error": "Invalid quantity"}, 400)
    except KeyError:
        return Response({"error": "Internal error"}, 500)

    try:
        price = int(query["price"])
    except KeyError:
        return Response({"error": "Price is missed"}, 500)
    except ValueError:
        return Response({"error": "Invalid price"}, 400)

    product = next((p for p in PRODUCTS if p["productId"] == product_id), None)

    if not product:
        return Response({"error": "Product not found"}, 404)

    existing_item = next(
        (
            item
            for item in self.cart
            if item.productId == product_id and item.price == price
        ),
        None,
    )

    if existing_item:
        existing_item.quantity += quantity
    else:
        new_item = CartItem(productId=product_id, quantity=quantity, price=price)
        self.cart.append(new_item)

    return Response({"message": "Item added to cart successfully"}, 200)


@Mock.route("/cart", method="GET")
def _(self, query: dict, data: dict) -> Response:
    return Response({"cart": [dataclasses.asdict(item) for item in self.cart]})


@Mock.route("/cart/checkout", method="POST")
def _(self, query: dict, data: dict):
    global store_credit
    print(self.cart)
    total_price = sum(item.price * item.quantity for item in self.cart)

    if total_price > self.store_credit:
        return Response({"error": "Insufficient store credit"}, 400)

    return Response(
        {
            "cart": [dataclasses.asdict(item) for item in self.cart],
            "store_credit": self.store_credit,
        }
    )


@Mock.route("/cart/order-confirmation", method="GET")
def _(self, query: dict, data: dict):
    global store_credit
    self.store_credit -= sum(item.price * item.quantity for item in self.cart)
    self.cart.clear()
    return Response({"message": "Order confirmed successfully"})


def har() -> dict:
    mock = Mock("webacademy.com")

    assert mock.make_request("GET", "/product").status_code == 200
    assert mock.make_request("GET", "/product?productId=1").status_code == 200
    assert mock.make_request("GET", "/academyLabHeader").status_code == 101
    assert (
        mock.make_request(
            "POST", "/cart?productId=1&quantity=1&price=133700"
        ).status_code
        == 200
    )
    assert mock.make_request("GET", "/product?productId=1").status_code == 200
    assert mock.make_request("GET", "/academyLabHeader").status_code == 101
    assert mock.make_request("GET", "/product").status_code == 200
    assert mock.make_request("GET", "/academyLabHeader").status_code == 101
    assert mock.make_request("GET", "/cart").status_code == 200
    assert mock.make_request("GET", "/academyLabHeader").status_code == 101
    assert mock.make_request("POST", "/cart/checkout").status_code == 400
    assert (
        mock.make_request(
            "POST", "/cart?productId=1&quantity=-1&price=133700"
        ).status_code
        == 200
    )
    assert (
        mock.make_request("POST", "/cart?productId=2&quantity=1&price=6047").status_code
        == 200
    )
    assert mock.make_request("GET", "/academyLabHeader").status_code == 101
    assert mock.make_request("GET", "/cart").status_code == 200
    assert mock.make_request("GET", "/academyLabHeader").status_code == 101
    assert mock.make_request("GET", "/cart").status_code == 200
    assert mock.make_request("GET", "/academyLabHeader").status_code == 101
    assert mock.make_request("GET", "/cart").status_code == 200
    assert mock.make_request("GET", "/academyLabHeader").status_code == 101
    assert mock.make_request("POST", "/cart/checkout").status_code == 200
    assert mock.make_request("GET", "/cart/order-confirmation").status_code == 200
    assert mock.make_request("GET", "/academyLabHeader").status_code == 101

    return mock.har()


def main():
    har()


if __name__ == "__main__":
    main()
