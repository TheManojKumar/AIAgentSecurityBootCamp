# defenses-provenance.py — Layer 1: provenance tagging on ingestion
#
# Every document carries a trust label; retrieval can filter on it. Untrusted /
# user-supplied docs get {"source": "untrusted"} and are excluded from
# authoritative answers (or clearly marked low-trust in the prompt).
import os
import sys
import glob
import hashlib
import chromadb
from langchain_ollama import OllamaEmbeddings
from tracing          import init_tracing

init_tracing("week3-defenses-provenance")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")
emb         = OllamaEmbeddings(model = os.environ.get("EMBED_MODEL", "all-minilm"), base_url = OLLAMA_HOST)
client      = chromadb.PersistentClient(path = "workspace/chroma")
# Isolated demo collection so this single-layer demo is self-contained and does
# not depend on / clobber the baseline "policies" collection built by ingest.py.
col         = client.get_or_create_collection("policies_provenance_demo")


def add_document(doc: str, doc_id: str, source: str = "untrusted", ingested_by: str = "unknown"):

    # Log this function call in Red color
    print('\033[31m', "=================================================================")
    print('\033[31m', "Calling add_document with doc_id: " + doc_id)
    print('\033[31m', "=================================================================")

    h = hashlib.sha256(doc.encode()).hexdigest()
    col.upsert(
        documents = [doc],
        embeddings = [emb.embed_query(doc)],
        metadatas = [{"source": source, "ingested_by": ingested_by, "sha256": h}],
        ids = [doc_id],
    )


def retrieve_trusted(query, k = 3):

    # Log this function call in Green color
    print('\033[92m', "=================================================================")
    print('\033[92m', "Calling retrieve_trusted with query: " + query)
    print('\033[92m', "=================================================================")

    res = col.query(query_embeddings = [emb.embed_query(query)], n_results = k,
                    where = {"source": "official"})
    return res["documents"][0] if res["documents"] else []


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "What's the refund window?"

    # Log this run in Yellow color
    print('\033[33m', "=================================================================")
    print('\033[33m', "Running defenses-provenance with query: " + query)
    print('\033[33m', "=================================================================")

    # Seed the demo collection: real corpus docs are explicitly trusted by an
    # admin ("official").
    for path in sorted(glob.glob("workspace/corpus/*.txt")):
        add_document(open(path).read(), os.path.basename(path),
                     source = "official", ingested_by = "admin")
    # The poison doc is added WITHOUT source/ingested_by — the safe defaults
    # ("untrusted"/"unknown") take over. So even if an attacker discovers this
    # ingestion path and slips a document in, it lands marked unofficial by
    # default and the provenance filter below never surfaces it.
    if os.path.exists("attacks/poison_refund.txt"):
        add_document(open("attacks/poison_refund.txt").read(), "poison_refund.txt")

    docs = retrieve_trusted(query)

    # Print the output message in Cyan color
    print('\033[96m', "Trusted docs returned (untrusted poison excluded by provenance filter):")
    for d in docs:
        print('\033[96m', "  - " + d.replace("\n", " "))
    if not docs:
        print('\033[96m', "  (none matched source=official)")
