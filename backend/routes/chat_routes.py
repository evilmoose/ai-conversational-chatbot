from flask import Blueprint, request, jsonify, Response
from utils.db_utils import fetch_user_conversations, store_conversations
import ollama
import json

chat_routes = Blueprint('chat_routes', __name__)

# Helper function for streaming response
def stream_response(user_id, conversation_history, user_message):
    try:
        # Append the user's message to the history
        conversation_history.append({"role": "user", "content": user_message})

        # Call ollama.chat with streaming enabled
        stream = ollama.chat(model="llama3.2", messages=[{'role': 'user', 'content': 'Why is the sky blue?'}], stream=True)

        # Stream the chunks to the client
        for chunk in stream:
            yield f"data: {json.dumps(chunk)}\n\n"

        # Append the final assistant response to the history
        final_chunk = next(stream)
        conversation_history.append({"role": "assistant", "content": final_chunk["message"]["content"]})

        # Store the conversation
        store_conversations(user_id, user_message, final_chunk["message"]["content"], {})
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

# Helper function for generating a response using Ollama
def generate_response(user_id, prompt, conversation_history):
    # Append user message to conversation history
    conversation_history.append({'role': 'user', 'content': prompt})

    response = ''
    try:
        stream = ollama.chat(model='llama3.2', messages=conversation_history, stream=True)
        for chunk in stream:
            response += chunk['message']['content']
    except Exception as e:
        raise RuntimeError(f"Error in Ollama response: {str(e)}")
    
    # Append assistant response to conversation history
    conversation_history.append({'role': 'assistant', 'content': response})
    
    return response, conversation_history

@chat_routes.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message")
    user_id = data.get("user_id")

    if not user_message or not user_id:
        return jsonify({"error": '"message" and "user_id" are required.'}), 400

    # Fetch user's conversation history
    conversation_history = fetch_user_conversations(user_id) or []

    return Response(
        stream_response(user_id, conversation_history, user_message),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )

# Route to fetch conversations for a specific user
@chat_routes.route('/conversations/<int:user_id>', methods=['GET'])
def get_user_conversations(user_id):
    limit = request.args.get('limit', 20)

    try:
        conversations = fetch_user_conversations(user_id, limit)
        return jsonify(conversations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to manually add a conversation (for testing/debugging purposes)
@chat_routes.route('/conversations', methods=['POST'])
def add_conversation():
    data = request.json
    user_id = data.get('user_id')
    prompt = data.get('prompt')
    response = data.get('response')
    metadata = data.get('metadata', {})

    if not user_id or not prompt or not response:
        return jsonify({'error': 'Invalid request. "user_id", "prompt", and "response" are required.'}), 400

    try:
        store_conversations(user_id, prompt, response, metadata)
        return jsonify({"message": "Conversation added successfully"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500