#!/usr/bin/env python3
"""Import a Hermes session from JSON export into state.db.

Usage: python import_session.py <path_to_export.json> [--db <state.db_path>]

The script:
1. Reads the JSON export (hermes sessions export format)
2. Inserts the session record into sessions table
3. Inserts all messages into messages table
4. Commits data FIRST (safety)
5. Rebuilds FTS indexes separately
"""
import sqlite3, json, os, sys, argparse


def find_db():
    """Locate state.db in common paths."""
    candidates = [
        os.path.expanduser('~/AppData/Local/hermes/state.db'),
        os.path.expanduser('~/.hermes/state.db'),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def import_session(json_path, db_path):
    if not os.path.exists(json_path):
        print(f"ERROR: File not found: {json_path}")
        sys.exit(1)
    if not os.path.exists(db_path):
        print(f"ERROR: Database not found: {db_path}")
        sys.exit(1)

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    session_id = data['session_id']
    title = data['title']
    messages = data['messages']

    print(f"Session: {session_id}")
    print(f"Title: {title}")
    print(f"Messages: {len(messages)}")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Check if already exists
    cur.execute("SELECT id FROM sessions WHERE id = ?", (session_id,))
    if cur.fetchone():
        print("Session exists — deleting to re-import...")
        cur.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        cur.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()

    # Timestamps
    first_ts = messages[0]['timestamp'] if messages else 0
    last_ts = messages[-1]['timestamp'] if messages else 0
    tool_call_count = sum(1 for m in messages if m.get('tool_calls'))

    # Insert session (columns: id, source, title, started_at, ended_at, message_count, tool_call_count)
    cur.execute("""
        INSERT INTO sessions (id, source, title, started_at, ended_at, message_count, tool_call_count)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session_id, 'cli', title, first_ts, last_ts, len(messages), tool_call_count))
    print("Inserted session")

    # Insert messages (let SQLite assign id — do NOT copy exported id)
    inserted = 0
    for msg in messages:
        tc = json.dumps(msg['tool_calls']) if msg.get('tool_calls') else None
        rd = json.dumps(msg['reasoning_details']) if msg.get('reasoning_details') else None
        cr = json.dumps(msg['codex_reasoning_items']) if msg.get('codex_reasoning_items') else None
        cm = json.dumps(msg['codex_message_items']) if msg.get('codex_message_items') else None

        cur.execute("""
            INSERT INTO messages (session_id, role, content, tool_call_id, tool_calls, tool_name,
                                  timestamp, token_count, finish_reason, reasoning, reasoning_content,
                                  reasoning_details, codex_reasoning_items, codex_message_items,
                                  platform_message_id, observed, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            msg.get('role', ''),
            msg.get('content', ''),
            msg.get('tool_call_id'),
            tc,
            msg.get('tool_name'),
            msg.get('timestamp', 0),
            msg.get('token_count'),
            msg.get('finish_reason'),
            msg.get('reasoning'),
            msg.get('reasoning_content'),
            rd, cr, cm,
            msg.get('platform_message_id'),
            msg.get('observed', 0),
            msg.get('active', 1),
        ))
        inserted += 1

    # COMMIT DATA FIRST — before FTS rebuild
    conn.commit()
    print(f"Committed {inserted} messages")

    # Rebuild FTS indexes (separate transaction)
    fts_ok = 0
    cur.execute("SELECT id, content FROM messages WHERE session_id = ?", (session_id,))
    for rowid, content in cur.fetchall():
        if content:
            try:
                cur.execute("INSERT INTO messages_fts(rowid, content) VALUES (?, ?)", (rowid, content))
                fts_ok += 1
            except:
                pass
            try:
                cur.execute("INSERT INTO messages_fts_trigram(rowid, content) VALUES (?, ?)", (rowid, content))
            except:
                pass

    conn.commit()
    conn.close()
    print(f"FTS indexed: {fts_ok}")
    print(f"\nResume with: hermes --resume {session_id}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import Hermes session from JSON export')
    parser.add_argument('json_path', help='Path to the exported JSON file')
    parser.add_argument('--db', default=find_db(), help='Path to state.db')
    args = parser.parse_args()
    if not args.db:
        print("ERROR: Could not find state.db. Use --db to specify path.")
        sys.exit(1)
    import_session(args.json_path, args.db)
