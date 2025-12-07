import weaviate
from datasets import load_dataset
from weaviate.classes.config import Configure, Property, DataType

client = weaviate.connect_to_local(port=8080)
ds = load_dataset("mt0rm0/movie_descriptors")


collection_name = "Movies"
if client.collections.exists(collection_name):
    client.collections.delete(collection_name)

articles = client.collections.create(
    name= collection_name,
    vector_config=Configure.Vectors.text2vec_openai(),
    properties=[
        Property(name="title", data_type=DataType.TEXT),
        Property(name="description", data_type=DataType.TEXT),

    ],
)

with articles.batch.dynamic() as batch:
    for i in ds['train']:
       item = {"title": i['title'], "description": i['overview']}
       batch.add_object(properties=item)
       print(i['title'])

