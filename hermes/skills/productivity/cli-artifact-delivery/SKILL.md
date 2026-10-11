---
name: cli-artifact-delivery
description: "Use when handing files or prompts to a user for copy-paste."
---

# Handing artifacts to a CLI user

Class: getting a file, a code block, or a prompt from the agent's filesystem into the
user's hands when the session is a plain terminal — no attachment channel exists.
Covers copy-paste delivery, where to put the file, and pushing it to a messaging home
channel.

## Copy-paste delivery: print the file verbatim
- `read_file` prefixes every line with `LINE|`. That prefix is part of the output and
  lands in the user's clipboard, corrupting code they are about to run. Never use it
  when the ask is "kirim ke sini biar bisa gw copas". Print raw instead:
  `echo "=== FILE 1/2: /abs/path ===" && cat f1 && echo "=== FILE 2/2: /abs/path ===" && cat f2`
- Do NOT wrap output in markdown fences. In a terminal the fence lines render as literal
  characters and get copied into the user's file. Blank lines and `===` separators are
  the only layout tools available.
- Print FROM DISK, never retype the content into the reply: retyping introduces silent
  transcription drift in code the user will execute.
- Close with line/byte counts, the absolute save path, and the exact run recipe (venv
  creation + dependency install), so clipboard → working file needs no follow-up.
- Also write the same text to a `.txt` beside the artifact and give that path: scrolling a
  terminal to select 5 KB of text is worse than opening a file.

## No attachment channel
- `MEDIA:/path` tags are NOT intercepted in a CLI session — they print as literal text.
  Deliver by stating the absolute path, or push the file to a messaging platform (below).

## Ask which FORM the artifact should take
- "kirim code-nya" / "kirim prompt-nya" is ambiguous between the generator script, the
  rendered output, and a paste-ready prompt for an external tool. When an artifact has
  more than one form, confirm which one before producing more of the wrong one.
- Signal that resolves it: "mau pakai AI image generator gw sendiri" / "mau gw tempel di
  Canva" means the deliverable is PROMPT TEXT for an external tool, not the local script
  that renders the asset. Send the prompt; keep the script only as the data source.

## Putting the file where the user expects it
- This user uses "home" for two different things: the agent host's home dir
  (`/home/ubuntu/`) when no platform is named, and the messaging HOME CHANNEL when a
  platform is named ("home wa" = the WhatsApp home channel). Resolve it against
  `home_channel` in `~/.hermes/config.yaml` before asking a clarifying question.
- `cp` the artifact into home; keep the canonical copy in the project directory.

## Sending to a messaging home channel
- `hermes send --to <platform> "text"` delivers to that platform's configured
  `home_channel` (bare platform name = home channel). `hermes send --list` prints every
  available target id. Attach a document/image by embedding `MEDIA:/abs/path` inside the
  message text. No LLM call and no running agent turn needed.
- Verification is limited: the CLI reports the chat_id it sent to, but there is no
  send-level log to read back. Report it as "CLI reports sent to <chat_id>" and ask the
  user to confirm in the app — never state that delivery was confirmed.
- A `gateway.mirror: no session found for <chat>` warning in `logs/agent.log` immediately
  after a CLI send is EXPECTED (there is no session to mirror into) — it is not a failure.

## Reusable artifacts vs one-off copies
- When the user asks for a regenerable artifact (a prompt, a report template), ship the
  SCRIPT that produces it alongside the output, and say which input file to edit to
  regenerate. Handing over only the output forces a rebuild next time.
