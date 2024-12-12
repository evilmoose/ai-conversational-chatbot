from flask import Blueprint, request, jsonify
from utils.db_utils import fetch_conversations, store_conversations

chat_routes = Blueprint('chat_routes', __name__)

@chat_routes.route('/conversations', methods=['GET'])
def get_conversations():
    conversations = fetch_conversations()
    return jsonify(conversations)

@chat_routes.route('/conversations', methods=['POST'])
def add_conversation():
    data = request.json
    prompt = data.get('prompt')
    response = data.get('response')
    metadata = data.get('metadata', {})
    store_conversations(prompt, response, metadata)
    return jsonify({"message": "Conversation added successfully"})