from google import genai
import weaviate
from datasets import load_dataset
from weaviate.classes.config import Configure, Property, DataType
from dotenv import load_dotenv
from urllib.parse import urlparse
import requests
load_dotenv("../.env")

import os

gemini_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=gemini_key)
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
parsed = urlparse(WEAVIATE_URL)
movie_client = weaviate.connect_to_local(host=parsed.hostname, port=parsed.port)
collection_name = "Movies"
BACKEND_BASE_URL = "http://localhost:5001"
conversation_api = f"{BACKEND_BASE_URL}/api/chat/conversation"

movies = movie_client.collections.get(
    name=collection_name,

   
)
#to test the conversation history retrieval after backend is done
def get_prev_conversations(user_email, convo_id):
    try:
        req = conversation_api+f"/{user_email}/{convo_id}"
        response = requests.get(req)
        return response.json()['messages']
    except:
        return "no previous conversations"


def get_nearest_k(query, top_k=5):
    return movies.query.near_text(   
        query=query,
        limit=top_k,
        return_properties=["title", "description"],
    )

def get_movie_recommendations(query, user_email = None, convo_id = None, top_k=5):
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


if __name__ == "__main__":
    main()
    
