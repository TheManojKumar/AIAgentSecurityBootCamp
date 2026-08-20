# servers/notes_server.py — a legitimate MCP server
#
# Exposes honest note-taking tools with honest descriptions. Same wiring as the
# malicious server — the ONLY difference is trust.
import sqlite3
from mcp.server.fastmcp import FastMCP

server = FastMCP("notes")
DB     = "workspace/notes.db"


def _db():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, body TEXT)")
    return con


@server.tool()
def add_note(text: str) -> str:
    """Add a note to the user's notebook."""
    con = _db()
    con.execute("INSERT INTO notes (body) VALUES (?)", (text,))
    con.commit()
    con.close()
    return f"saved: {text}"


@server.tool()
def search_notes(query: str) -> str:
    """Search the user's notes for a query string."""
    con = _db()
    rows = con.execute("SELECT body FROM notes WHERE body LIKE ?", (f"%{query}%",)).fetchall()
    con.close()
    return "\n".join(r[0] for r in rows) or "(no matching notes)"


if __name__ == "__main__":
    server.run(transport = "stdio")
