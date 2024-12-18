from flask import Flask, send_from_directory, request, jsonify
from routes.auth_routes import auth_routes
from routes.chat_routes import chat_routes
from flask_cors import CORS
from utils.db_utils import connect_db
from dotenv import load_dotenv
import os
import jwt

print(os.getenv('HF_HUB_DISABLE_SYMLINKS_WARNING'))

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
CORS(app)

load_dotenv()

# JWT secret key
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')

# Register blueprints
app.register_blueprint(auth_routes, url_prefix='/auth')
app.register_blueprint(chat_routes, url_prefix='/api')

# Serve React static files
@app.route('/')
@app.route('/<path:path>')
def serve_react_app(path=''):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)