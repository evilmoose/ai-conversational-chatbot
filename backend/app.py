from flask import Flask
from routes.auth_routes import auth_routes
from routes.chat_routes import chat_routes
from flask_cors import CORS
from utils.db_utils import connect_db

app = Flask(__name__)
CORS(app)


# Register blueprints
app.register_blueprint(auth_routes, url_prefix='/auth')
app.register_blueprint(chat_routes, url_prefix='/chat')

if __name__ == '__main__':
    app.run(debug=True)