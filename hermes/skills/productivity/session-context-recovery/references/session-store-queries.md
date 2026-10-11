# Querying the session store directly

Use when you need recency-ordered sessions, per-turn role/tool detail, or a time
window — cases where `session_search` (FTS over message content) is the wrong
instrument because the thing you want is metadata, not text.

Store: `~/.hermes/state.db` (SQLite). `~/.hermes/sessions/sessions.json` is only
a legacy mirror of the gateway routing index — it is **not** the session list.

## Tables

`sessions` — one row per session:

| column | use |
|---|---|
| `id` | primary key (`20261003_204119_b6bd0b`, `cron_<jobid>_<ts>`) |
| `source` | `cli` / `whatsapp` / `cron` — the transport |
| `profile_name` | owning profile |
| `model` | model that ran the session |
| `title` | auto-title from the first turns |
| `started_at`, `last_activity_at` | epoch floats — the window |
| `cwd`, `message_count`, `tool_call_count` | context and size |

`messages` — one row per turn, keyed by `session_id` (not `id`), carrying
`role`, `tool_name`, `content`, `timestamp`. `content` is large: always
`substr(content, 1, N)` rather than pulling whole rows.

## Recipes

```python
import sqlite3
c = sqlite3.connect('/home/ubuntu/.hermes/state.db')
c.row_factory = sqlite3.Row
cur = c.cursor()

# Recent sessions, newest first (attribution / "what happened lately")
cur.execute("""SELECT id, source, profile_name, model, title, cwd, message_count
               FROM sessions ORDER BY started_at DESC LIMIT 20""")

# Turn skeleton for one session — who spoke, what tool ran
cur.execute("""SELECT id, role, tool_name, substr(content,1,200) c, timestamp
               FROM messages WHERE session_id=? ORDER BY id""", (sid,))

# Cross-session content hit
cur.execute("""SELECT session_id, role, substr(content,1,200)
               FROM messages WHERE content LIKE ? LIMIT 50""", (f'%{term}%',))
```

## Reading the turns

`session_search(session_id=...)` is the friendlier path for a single session;
when its output exceeds the inline budget it spills to
`~/.hermes/cache/spillover/call_*.txt`, which `read_file` renders line-numbered
(`N|content`) — not valid JSON. Either `json.load` the raw path and walk
`d["messages"]`, or strip the `N|` prefix first.

## Log correlation

`~/.hermes/logs/agent.log` carries one `agent.turn_context: conversation turn:
session=... model=... provider=... platform=... msg='...'` line per user turn —
the cheapest way to see what a session actually was without loading it. Grep by
session id. Pair with `who` / `last` (source IPs, login times) when the question
is whether the interaction came from the user or elsewhere.
