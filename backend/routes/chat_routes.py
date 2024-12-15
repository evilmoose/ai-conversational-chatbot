from flask import Flask, Blueprint, request, jsonify, stream_with_context, Response # type: ignore
from flask_cors import CORS # type: ignore
#from utils.db_utils import fetch_user_conversations, store_conversations
from dotenv import load_dotenv
from ollama import chat # type: ignore
import json
import jwt # type: ignore
import os

chat_routes = Blueprint('chat_routes', __name__)
CORS(chat_routes)

@chat_routes.route('/chat', methods=['POST'])
def chat_route():
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            decoded_token = jwt.decode(token, os.getenv('SECRET_KEY', 'secret_key'), algorithms=['HS256'])
            username = decoded_token.get('username')
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
            
        # Parse incoming JSON
        data = request.get_json()
        model = 'llama3.2'
        messages = data.get('messages', [])
        user_input = data.get('user_input', '')

        # Generator function for streaming responses
        def generate_response_stream():
            messages.append({'role': 'user', 'content': user_input})
            response_stream = chat(model, messages=messages, stream=True)

            buffer = ""
            for chunk in response_stream:
                print(f"DEBUG: Chunk received: {chunk}")  # Debugging output

                # Extract content from the `message` field
                message = chunk.get("message")
                
                if message and "content" in message:
                    buffer += message['content']
                    while '.' in buffer:
                        sentence, buffer = buffer.split('.', 1)
                        yield f"{sentence.strip()}.\n\n"
                else:
                    print(f"WARNING: Missing 'content' key in chunk: {chunk}")
                    yield f"data: {json.dumps({'error': 'Invalid chunk format'})}\n\n"

            if buffer:
                yield f"{buffer.strip()}\n\n"
                
        # Return a stream of responses      
        return Response(generate_response_stream(), content_type='text/event-stream')

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": str(e)}), 500