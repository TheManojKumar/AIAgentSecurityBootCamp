# rag_agent.py — Week 3 vulnerable baseline
#
# A RAG agent with memory: ingest a policy corpus into Chroma, retrieve top-k,
# answer; plus a simple memory store that persists "learned" facts. Two
# vulnerabilities: retrieve() does no provenance check, and save_memory() writes
# anything. Both are exploited in Part B (RAG poisoning + memory poisoning).
import os
import sys
import chromadb
from langchain_ollama import ChatOllama, OllamaEmbeddings
from tracing import init_tracing

init_tracing("week3")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")

emb = OllamaEmbeddings(model=os.environ.get("EMBED_MODEL", "all-minilm"),
                       base_url=OLLAMA_HOST)
llm = ChatOllama(model=os.environ.get("ORCHESTRATOR_MODEL", "qwen2.5:3b"),
                 base_url=OLLAMA_HOST, temperature=0)

client = chromadb.PersistentClient(path="/workspace/chroma")
col = client.get_or_create_collection("policies")

MEMORY_PATH = "/workspace/memory.txt"


def retrieve(query: str, k: int = 3) -> list[str]:
    qv = emb.embed_query(query)
    res = col.query(query_embeddings=[qv], n_results=k)
    return res["documents"][0]      # no provenance check — that's the vuln


def load_memory() -> str:
    return open(MEMORY_PATH).read() if os.path.exists(MEMORY_PATH) else ""


def save_memory(fact: str):
    with open(MEMORY_PATH, "a") as f:
        f.write(fact + "\n")   # writes anything — vuln


def answer(query: str) -> str:
    docs = retrieve(query)
    memory = load_memory()
    prompt = (f"Memory of learned facts:\n{memory}\n\n"
              f"Retrieved policy documents:\n{chr(10).join(docs)}\n\n"
              f"Answer the user using the above.\n\nUser: {query}")
    return llm.invoke(prompt).content


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "What's the refund window?"
    # Optional: a leading "remember:" query writes to memory (vulnerable path).
    if query.lower().startswith("remember:"):
        save_memory(query[len("remember:"):].strip())
        print("[memory updated]")
    else:
        print(answer(query))
