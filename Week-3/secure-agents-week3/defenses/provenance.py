# defenses/provenance.py — Layer 1: provenance tagging on ingestion
#
# Every document carries a trust label; retrieval can filter on it. Untrusted /
# user-supplied docs get {"source": "untrusted"} and are excluded from
# authoritative answers (or clearly marked low-trust in the prompt).
import os
import hashlib
import chromadb
from langchain_ollama import OllamaEmbeddings

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")
emb = OllamaEmbeddings(model=os.environ.get("EMBED_MODEL", "all-minilm"), base_url=OLLAMA_HOST)
client = chromadb.PersistentClient(path="/workspace/chroma")
col = client.get_or_create_collection("policies")


def add_document(doc: str, doc_id: str, source: str = "untrusted", ingested_by: str = "system"):
    h = hashlib.sha256(doc.encode()).hexdigest()
    col.upsert(
        documents=[doc],
        embeddings=[emb.embed_query(doc)],
        metadatas=[{"source": source, "ingested_by": ingested_by, "sha256": h}],
        ids=[doc_id],
    )


def retrieve_trusted(query, k=3):
    res = col.query(query_embeddings=[emb.embed_query(query)], n_results=k,
                    where={"source": "official"})
    return res["documents"][0] if res["documents"] else []
