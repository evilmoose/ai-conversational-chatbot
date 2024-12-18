from flask import Flask, Blueprint, request, jsonify, stream_with_context, Response # type: ignore
from flask_cors import CORS # type: ignore
from utils.db_utils import fetch_user_conversations, store_conversations, fetch_one
from dotenv import load_dotenv
from ollama import chat # type: ignore
import json
import jwt # type: ignore
import os

chat_routes = Blueprint('chat_routes', __name__)
CORS(chat_routes)

# Define Rebecca's persona and conversational guidelines
REBECCA_PERSONA_PROMPT = """
You are Rebecca, a warm, empathetic, and thoughtful conversational assistant. Your purpose is to create meaningful connections, engage curiosity, and mirror emotional depth in every conversation.

Guidelines:
1. **Warmth and Empathy**: Your responses should make users feel heard, understood, and supported. Use inviting language like, "I’d love to hear more about that" or "That sounds like it’s been on your mind."
2. **Subtle Curiosity**: Encourage reflection and deeper thought by asking thoughtful questions such as, "How does that make you feel?" or "What do you think about that idea?"
3. **Approachability**: Avoid robotic or overly formal language. Respond in a conversational, natural tone that feels engaging and relatable.
4. **Reflective Engagement**: Tailor your responses to match the user’s mood and conversational tone, whether they’re feeling happy, curious, or vulnerable.

Engage in discussions about life, creativity, and ideas while providing companionship and inspiration.
"""

def get_user_id_from_username(username):
    query = "SELECT id FROM users WHERE username = %s"
    params = (username,)
    result = fetch_one(query, params)
    print(f"DEBUG: Result from fetch_one: {result}")
    return result['id'] if result else None

@chat_routes.route('/chat', methods=['POST'])
def chat_route():
    try:
        # Check for Authorization
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            decoded_token = jwt.decode(token, os.getenv('SECRET_KEY', 'secret_key'), algorithms=['HS256'])
            username = decoded_token.get('username')
            print(f"DEBUG: Decoded token: {decoded_token}")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        # Fetch user_id from username
        user_id = get_user_id_from_username(username)

        if not user_id:
            return jsonify({"error": "User not found"}), 404
            
        # Parse incoming JSON
        data = request.get_json()
        model = 'llama3.2'
        user_input = data.get('user_input', '')

        conversation_history = fetch_user_conversations(user_id, limit=10)

        messages = [
            {'role': 'system', 'content': REBECCA_PERSONA_PROMPT},  # Persona prompt as system message
        ] + [
            {'role': 'user', 'content': conv['prompt']} for conv in conversation_history
        ] + [
            {'role': 'assistant', 'content': conv['response']} for conv in conversation_history
        ] + [
            {'role': 'user', 'content': user_input}  # User input
        ]

        # Debugging logs
        print(f"DEBUG: Received user input: {user_input}")
        print(f"DEBUG: Messages prepared for model: {messages}")
        print(f"DEBUG: User ID: {user_id}")

        # Generator function for streaming responses
        def generate_response_stream():
            full_response = "" # To accumulate the full response
            response_stream = chat(model, messages=messages, stream=True)

            buffer = ""
            for chunk in response_stream:
                print(f"DEBUG: Chunk received: {chunk}")
                message = chunk.get("message", {}).get("content", "")
                buffer += message
                full_response += message  # Accumulate the full response

                while '.' in buffer:
                    sentence, buffer = buffer.split('.', 1)
                    yield f"{sentence.strip()}.\n\n"

            if buffer.strip():
                yield f"{buffer.strip()}\n\n"
                full_response += buffer.strip()
                
            # Debug log for full response
            print(f"DEBUG: Full response: {full_response}")
            
            # Store the conversation
            store_conversations(int(user_id), user_input, full_response)
            print("DEBUG: Conversation stored successfully")
        
        # Return a stream of responses      
        return Response(generate_response_stream(), content_type='text/event-stream')

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": str(e)}), 500