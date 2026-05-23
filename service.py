from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!

jwt = JWTManager(app)

# For simplicity, we're using the same password for all users.
users = {
    "Alice": generate_password_hash("AlicePassword"),
    "Bob": generate_password_hash("BobPassword"),
    "Charlie": generate_password_hash("CharliePassword"),
}


class Account:
    def __init__(self, owner, initial_balance=0):
        self.owner = owner
        self.balance = initial_balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            return True
        else:
            return False

    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            return True
        else:
            return False

    def get_balance(self):
        return self.balance


# we will store the accounts in a dictionary for simplicity
accounts = {user: Account(user, 500) for user in users}


@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({"ok": False, "message": "Missing Authorization Header"}), 401


@app.route("/auth", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    params = request.get_json()
    username = params.get("username", None)
    password = params.get("password", None)

    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    if username in users and check_password_hash(users.get(username), password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401


@app.route("/account/<string:owner>/balance", methods=["GET"])
@jwt_required()
def get_balance(owner):
    account = accounts.get(owner)
    if account:
        return jsonify({"balance": account.get_balance()}), 200
    else:
        return jsonify({"message": "account not found"}), 404


@app.route("/account/<string:owner>/deposit", methods=["POST"])
@jwt_required()
def deposit(owner):
    account = accounts.get(owner)
    if account:
        data = request.get_json()
        amount = data["amount"]
        if account.deposit(amount):
            return jsonify({"balance": account.get_balance()}), 200
        else:
            return jsonify({"message": "deposit failed"}), 400
    else:
        return jsonify({"message": "account not found"}), 404


@app.route("/account/<string:owner>/withdraw", methods=["POST"])
@jwt_required()
def withdraw(owner):
    account = accounts.get(owner)
    if account:
        data = request.get_json()
        amount = data["amount"]
        if account.withdraw(amount):
            return jsonify({"balance": account.get_balance()}), 200
        else:
            return jsonify({"message": "withdrawal failed"}), 400
    else:
        return jsonify({"message": "account not found"}), 404


@app.route("/account/transfer", methods=["POST"])
@jwt_required()
def transfer():
    data = request.get_json()
    from_owner = data["from"]
    to_owner = data["to"]
    amount = data["amount"]
    from_account = accounts.get(from_owner)
    to_account = accounts.get(to_owner)
    if from_account and to_account:
        if from_account.withdraw(amount):
            to_account.deposit(amount)
            return jsonify({"balance": from_account.get_balance()}), 200
        else:
            return jsonify({"message": "transfer failed"}), 400
    else:
        return jsonify({"message": "account not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
