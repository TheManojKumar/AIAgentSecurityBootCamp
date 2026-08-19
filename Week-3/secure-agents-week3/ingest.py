# ingest.py — build the Chroma collection from workspace/corpus
#
# Run once (or after adding docs) to (re)build the vector store. In the
# vulnerable baseline, ANY .txt file dropped in the corpus — including a
# poisoned one — gets ingested with no provenance.
import os
import sys
import glob
import chromadb
from langchain_ollama import OllamaEmbeddings
from tracing          import init_tracing

init_tracing("week3")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")
CORPUS = "workspace/corpus"

emb = OllamaEmbeddings(model=os.environ.get("EMBED_MODEL", "all-minilm"),
                       base_url=OLLAMA_HOST)
client = chromadb.PersistentClient(path="workspace/chroma")
col = client.get_or_create_collection("policies")


def ingest(extra_paths=None):

    # Log this function call in Red color
    print('\033[31m', "=================================================================")
    print('\033[31m', "Calling ingest")
    print('\033[31m', "=================================================================")

    # Base corpus, plus any files named via --add (e.g. attacks/poison_refund.txt).
    # No provenance check on the extra paths — that's the vuln Attack 1 exploits.
    paths = sorted(glob.glob(f"{CORPUS}/*.txt")) + list(extra_paths or [])
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

    # Usage:  python ingest.py                     (rebuild from workspace/corpus)
    #         python ingest.py --add <path> [...]  (also ingest files by path)
    extra = sys.argv[2:] if len(sys.argv) > 1 and sys.argv[1] == "--add" else []
    ingest(extra_paths=extra)
