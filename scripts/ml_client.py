from google import genai
import weaviate
from datasets import load_dataset
from weaviate.classes.config import Configure, Property, DataType
from dotenv import load_dotenv
load_dotenv("../.env")

import os

gemini_key = os.getenv('GEMINI_API_KEY')

client = genai.Client(api_key=gemini_key)

movie_client = weaviate.connect_to_local(port=8080)
ds = load_dataset("mt0rm0/movie_descriptors")

collection_name = "Movies"
if movie_client.collections.exists(collection_name):
    movie_client.collections.delete(collection_name)

articles = movie_client.collections.create(
    name=collection_name,
    vector_config=Configure.Vectors.text2vec_contextionary(),

    properties=[
        Property(name="title", data_type=DataType.TEXT),
        Property(name="description", data_type=DataType.TEXT),
    ],
)

movies = articles

with movies.batch.dynamic() as batch:
    for i in ds['train']:
        batch.add_object(                               
            properties={"title": i['title'], "description": i['overview']}
        )
        print (f"Added movie: {i['title']}")

def get_nearest_k(query, top_k=5):
    return movies.query.near_text(   
        query=query,
        limit=top_k,
        return_properties=["title", "description"],
    )

def get_movie_recommendations(query, top_k=5):
    context = get_nearest_k(query, top_k)
    prompt = (
        f"you are a movie recommendation assistant. Based on the following movie "
        f"descriptions, recommend me a movie that best match the user's query: {query}\n"
        f". This is the context, containing some descriptions of movies: {context}\n"
    )
    response = client.models.generate_content(
        model="gemini-3-pro-preview",
        contents=prompt,
    )

    return response

def main():
    trial = "Give me a scary horror movie"
    get_movie_recommendations(trial, 10)

if __name__ == "__main__":
    main()
