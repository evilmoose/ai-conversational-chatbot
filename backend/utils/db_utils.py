import os
import json
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

# Load environment variables
load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

# Connect to the database
def connect_db():
    try:
        conn = psycopg.connect(**DB_PARAMS, row_factory=dict_row)
        return conn
    except psycopg.OperationalError as e:
        print(f"Database connection error: {e}")
        raise

# General utility to fetch all rows from a query
def fetch_all(query, params=None):
    conn = connect_db()
    try:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    finally:
        conn.close()

# Fetch all conversations, ordered by timestamp
def fetch_conversations(limit=10):
    query = 'SELECT * FROM conversations ORDER BY timestamp DESC LIMIT %s'
    params = (limit,)
    return fetch_all(query, params)[::-1]  # Reverse for chronological order if needed

# Fetch conversations for a specific user
def fetch_user_conversations(user_id, limit=20):
    query = """
    SELECT id, timestamp, prompt, response, metadata
    FROM conversations
    WHERE user_id = %s
    ORDER BY timestamp DESC
    LIMIT %s
    """
    params = (user_id, limit)
    return fetch_all(query, params)


# Store a conversation in the database
def store_conversations(user_id, prompt, response, metadata=None):
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO conversations (
                    user_id,
                    prompt,
                    response,
                    metadata
                ) 
                VALUES (%s, %s, %s, %s)
                ''',
                (user_id, prompt, response, json.dumps(metadata) if metadata else None)
            )
        conn.commit()
    finally:
        conn.close()

# Example utility to delete a conversation (optional)
def delete_conversation(conversation_id):
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM conversations WHERE id = %s', (conversation_id,))
        conn.commit()
    finally:
        conn.close()

# Example utility to update a conversation (optional)
def update_conversation(conversation_id, response=None, metadata=None):
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                UPDATE conversations
                SET response = COALESCE(%s, response),
                    metadata = COALESCE(%s, metadata)
                WHERE id = %s
                ''',
                (response, json.dumps(metadata) if metadata else None, conversation_id)
            )
        conn.commit()
    finally:
        conn.close()