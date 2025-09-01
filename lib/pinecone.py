from typing import List, Dict
from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_KEY"))
vdb = pc.Index(host=os.getenv("PINECONE_HOST"))

def upsert(fingerprints: Dict[str, List[float]], metadata = None) -> None:
    vectors = [{"id": fid, "values": fingerprint} for fid, fingerprint in fingerprints.items()]

    vdb.upsert(
        vectors=vectors,
        namespace="wwmp",
        metadata=metadata
    )

def query(fingerprint: List[float], top_k=100):
    results = vdb.query_namespaces(
        vector=fingerprint,
        namespaces=['wwmp'],
        metric="cosine",
        top_k=top_k,
        include_values=False,
        include_metadata=True,
        # filter={"genre": { "$eq": "comedy" }},
        show_progress=False,
    )
    return results