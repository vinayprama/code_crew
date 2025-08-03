from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import uuid
from .embedding import embed_text


qdrant = QdrantClient(host="localhost", port=6333)  # Or your cloud URL

COLLECTION_NAME = "project_docs"

# Only once: initialize
def init_collection(collection_name: str):
    qdrant.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

def add_doc_to_vector_store(text_chunks, metadata_chunks):
    points = []

    for i, chunk in enumerate(text_chunks):
        vector = embed_text(chunk)  # returns List[float]
        metadata = metadata_chunks[i]

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=metadata  # Can be a dict with file info, etc.
            )
        )

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    

def search_similar_chunks(document_text: str, query: str, top_k=5):
    query_vector = embed_text(query)

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )

    return results