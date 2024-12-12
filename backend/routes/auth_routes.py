from flask import Blueprint, request, jsonify

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.json
    # Authentication logic here
    return jsonify({"message": "Login successful"})

@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.json
    # Registration logic here
    return jsonify({"message": "User registered successfully"})