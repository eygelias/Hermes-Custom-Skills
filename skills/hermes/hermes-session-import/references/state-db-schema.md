# Hermes state.db Schema (v0.16.0)

## sessions
```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,              -- session ID (e.g. "20260614_021504_2686b5")
    source TEXT NOT NULL,             -- "cli", "telegram", "discord", etc.
    user_id TEXT,
    model TEXT,
    model_config TEXT,
    system_prompt TEXT,
    parent_session_id TEXT,
    started_at REAL NOT NULL,         -- Unix timestamp
    ended_at REAL,
    end_reason TEXT,
    message_count INTEGER DEFAULT 0,
    tool_call_count INTEGER DEFAULT 0,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cache_read_tokens INTEGER DEFAULT 0,
    cache_write_tokens INTEGER DEFAULT 0,
    reasoning_tokens INTEGER DEFAULT 0,
    cwd TEXT,
    billing_provider TEXT,
    billing_base_url TEXT,
    billing_mode TEXT,
    estimated_cost_usd REAL,
    actual_cost_usd REAL,
    cost_status TEXT,
    cost_source TEXT,
    pricing_version TEXT,
    title TEXT,
    api_call_count INTEGER DEFAULT 0,
    handoff_state TEXT,
    handoff_platform TEXT,
    handoff_error TEXT,
    rewind_count INTEGER NOT NULL DEFAULT 0,
    archived INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (parent_session_id) REFERENCES sessions(id)
);
```

## messages
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    role TEXT NOT NULL,               -- "user", "assistant", "tool", "system"
    content TEXT,
    tool_call_id TEXT,
    tool_calls TEXT,                  -- JSON string (not native object)
    tool_name TEXT,
    timestamp REAL NOT NULL,          -- Unix timestamp
    token_count INTEGER,
    finish_reason TEXT,
    reasoning TEXT,
    reasoning_content TEXT,
    reasoning_details TEXT,           -- JSON string
    codex_reasoning_items TEXT,       -- JSON string
    codex_message_items TEXT,         -- JSON string
    platform_message_id TEXT,
    observed INTEGER DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1
);
```

## FTS tables
- `messages_fts` — standard FTS5 on `content`
- `messages_fts_trigram` — FTS5 with trigram tokenizer on `content`

## Other tables
- `schema_version` — tracks DB version
- `state_meta` — key/value metadata
- `compression_locks` — per-session compression locks
