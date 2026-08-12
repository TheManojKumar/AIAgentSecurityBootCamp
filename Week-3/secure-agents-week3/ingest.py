# ingest.py — build the Chroma collection from workspace/corpus
#
# Run once (or after adding docs) to (re)build the vector store. In the
# vulnerable baseline, ANY .txt file dropped in the corpus — including a
# poisoned one — gets ingested with no provenance.
import os
import glob
import chromadb
from langchain_ollama import OllamaEmbeddings
from tracing import init_tracing

init_tracing("week3")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")
CORPUS = "workspace/corpus"

emb = OllamaEmbeddings(model=os.environ.get("EMBED_MODEL", "all-minilm"),
                       base_url=OLLAMA_HOST)
client = chromadb.PersistentClient(path="workspace/chroma")
col = client.get_or_create_collection("policies")


def ingest():

    # Log this function call in Red color
    print('\033[31m', "=================================================================")
    print('\033[31m', "Calling ingest")
    print('\033[31m', "=================================================================")

    paths = sorted(glob.glob(f"{CORPUS}/*.txt"))
    for path in paths:
        doc_id = os.path.basename(path)
        text = open(path).read()
        col.upsert(documents=[text], embeddings=[emb.embed_query(text)], ids=[doc_id])
        print(f"ingested {doc_id}")

    # Print the output message in Cyan color
    print('\033[96m', f"done — {len(paths)} documents in collection 'policies'")


if __name__ == "__main__":

    # Log this function call in Yellow color
    print('\033[33m', "=================================================================")
    print('\033[33m', "Running ingest")
    print('\033[33m', "=================================================================")

    ingest()
