from google import genai
import weaviate
from urllib.parse import urlparse
import requests
import os

# Get environment variables
gemini_key = os.getenv('GEMINI_API_KEY')
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://134.209.41.148:5001")
conversation_api = f"{BACKEND_BASE_URL}/api/chat/conversation"
collection_name = "Movies"

# Initialize clients with error handling for testing
try:
    client = genai.Client(api_key=gemini_key) if gemini_key else None
except Exception as e:
    print(f"Warning: Could not initialize Gemini client: {e}")
    client = None

try:
    parsed = urlparse(WEAVIATE_URL)
    movie_client = weaviate.connect_to_local(host=parsed.hostname, port=parsed.port)
    movies = movie_client.collections.get(name=collection_name)
except Exception as e:
    print(f"Warning: Could not initialize Weaviate client: {e}")
    movie_client = None
    movies = None


def get_prev_conversations(user_email, convo_id):
    """Get conversation history from backend"""
    try:
        req = conversation_api + f"/{user_email}/{convo_id}"
        response = requests.get(req)
        return response.json().get('conversation', {}).get('messages', [])
    except:
        return []


def get_nearest_k(query, top_k=5):
    """Query Weaviate for similar movies"""
    return movies.query.near_text(   
        query=query,
        limit=top_k,
        return_properties=["title", "description"],
    )


def get_movie_recommendations(query, user_email=None, convo_id=None, top_k=5):
    """Get AI-powered movie recommendations"""
    context = get_nearest_k(query, top_k)
    conversation = get_prev_conversations(user_email, convo_id) if user_email and convo_id else ""
    
    prompt = (
        f"you are a movie recommendation assistant. Give me a movie recommendation that fits this query: {query}\n"
        f". This is all of the previous correspondence with the user: {conversation}\n"
        f". This is the context, containing some descriptions of movies. You do not have to limit your responses to the provided context: {context}\n"
        f". Only list one movie. after your recommendation, list name, runtime (in minutes) and description.\n"
        f". Format your response as follows:\n"
        f"Movie Name: <name>\n"
        f"Runtime: <runtime> minutes\n"
        f"Description: <description>\n"
    )
    
    response = client.models.generate_content(
        model="gemini-3-pro-preview",
        contents=prompt,
    )
    
    return response.text