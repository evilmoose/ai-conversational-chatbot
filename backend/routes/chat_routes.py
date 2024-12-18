from flask import Flask, Blueprint, request, jsonify, stream_with_context, Response, send_file
from flask_cors import CORS
from utils.db_utils import fetch_user_conversations, store_conversations, fetch_one
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer, set_seed
from dotenv import load_dotenv
from ollama import chat 
import torch
import soundfile as sf
import json
import jwt 
import os
import io

chat_routes = Blueprint('chat_routes', __name__)
CORS(chat_routes)

# Load Parler-TTS model and tokenizer
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"DEBUG: Device '{device}' being used for TTS...")

model = ParlerTTSForConditionalGeneration.from_pretrained(
    "parler-tts/parler-tts-mini-expresso",
    torch_dtype=torch.float32).to(device)
print(f"DEBUG: Model '{model}' loaded successfully...")

model = torch.compile(model)
print("DEBUG: Model compiled for faster float32 inference.")

tokenizer = AutoTokenizer.from_pretrained(
    "parler-tts/parler-tts-mini-expresso",
    use_fast=True)
print(f"DEBUG: Tokenizer '{tokenizer}' loaded successfully...")


print(f"DEBUG: Model '{model}' loaded successfully....")

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
    
@chat_routes.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        # Parse incoming text
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return jsonify({f"DEBUG: No text provided..."}), 400
        
        description = "Laura's voice is soft, warm, friendly, and slightly fast delivery, with normal quaity audio and a very close recording that almost has no background noise"
        print(f"DEBUG: Text to convert to speech: {text}")
        # Tokenize inputs explicitly with attention_mask
        description_tokens = tokenizer(
            description, return_tensors="pt", padding=True, truncation=False).to(device)

        text_tokens = tokenizer(
            text, return_tensors="pt", padding=True, truncation=False).to(device)

        set_seed(42)
        torch.manual_seed(42)

        if torch.cuda.is_available():
            torch.cuda.manual_seed(42)
            torch.cuda.manual_seed_all(42)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False

        generation = model.generate(
            input_ids=description_tokens['input_ids'],
            attention_mask=description_tokens['attention_mask'],
            prompt_input_ids=text_tokens['input_ids'],
            prompt_attention_mask=text_tokens['attention_mask'],
        )

        # Convert generated output to audio
        audio_arr = generation.cpu().numpy().squeeze()
        buffer = io.BytesIO()
        sf.write(buffer, audio_arr, model.config.sampling_rate, format="WAV")
        buffer.seek(0)

        return send_file(buffer, mimetype="audio/wav", as_attachment=False)

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": str(e)}), 500