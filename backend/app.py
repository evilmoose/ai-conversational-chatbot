from flask import Flask, send_from_directory, request, jsonify
from routes.auth_routes import auth_routes
from routes.chat_routes import chat_routes
from flask_cors import CORS
from utils.db_utils import connect_db
from dotenv import load_dotenv
import jwt
import os

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
CORS(app)

load_dotenv()

SECREY_KEY = os.getenv('SECRET_KEY')

# middleware to connect to the database
@app.before_request
def check_jwt():
    if request.path.startswith('/auth'):
        return
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"error": "Token is missing..."}), 401
    try:
        jwt.decode(token, SECREY_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired..."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token..."}), 401

# Register blueprints
app.register_blueprint(auth_routes, url_prefix='/auth')
app.register_blueprint(chat_routes, url_prefix='/chat')

# Serve React static files
@app.route('/')
@app.route('/<path:path>')
def serve_react_app(path=''):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)