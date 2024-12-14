from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
import os
import jwt
import datetime
from utils.db_utils import connect_db
import bcrypt

# Load environment variables
load_dotenv()

auth_routes = Blueprint('auth_routes', __name__)
SECRET_KEY = os.getenv('SECRET_KEY')


@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.json
    # Authentication logic here

    username = data.get('username')
    password = data.get('password')

    db = connect_db()

    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        token = jwt.encode({
            'username': username, 
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, 
            SECRET_KEY, algorithm='HS256')
        
        return jsonify({"token": token})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.json

    # Registration logic here
    username = data.get('username')
    password = data.get('password')

    # Hash the password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    db = connect_db()   

    with db.cursor() as cursor:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        db.commit()

    return jsonify({"message": "User registered successfully"})
