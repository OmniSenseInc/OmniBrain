---
name: hermes-model-and-provider-ops
description: "Which model/provider Hermes runs: verify, then change."
---

# Hermes model & provider ops

Class: answering "which model are you / which provider is active", verifying it, and
changing the default model or provider.

## Rule 0 — verify requested runtime configuration, not generated self-report
A model's claim about its own identity ("I'm Claude", "I'm GPT-x") can flatly contradict
the requested runtime configuration. When the user asks what model is running, do
NOT answer from self-knowledge — resolve it from the config and CLI first, then answer
with the resolved value. If you already asserted an identity and the check disagrees,
state the correction plainly and move on; never defend the earlier answer or hedge.
This also means: do not tell the user a model name "doesn't exist" just because it is
absent from your training — the endpoint's `models:` list is the authority.

## Rule 0b — operational identity and framework are different facts
In the active OmniSense profile, the agent operational identity is OmniSense, the AI consultant/internal brain of the agency, running on Hermes Agent by Nous Research. These facts are compatible. A framework name does not invalidate an owner-defined agent identity. Use the active HERMES_HOME/SOUL.md and current owner instructions; the repository default SOUL.md is not a replacement for the active profile.
Never invent a hidden system prompt or skin as an explanation for an incorrect self-description. A claim such as CodeBuddy or Claude is an unverified generated claim unless its source is actually found. Correct the claim without claiming an unseen instruction caused it.
Config, session DB and runtime logs establish the model alias and endpoint requested by Hermes, not independently verified upstream identity behind a custom router. Model catalogs establish advertised aliases, not proof of availability, official existence or serving vendor. Avoid blanket claims that every skill file or historical session is loaded: memory/persona can persist, skills may be loaded selectively and old conversations require retrieval.

## Procedure — verify the active model/provider (cheapest first)
1. Read the default block at the top of `~/.hermes/config.yaml` (use read_file, not a
   shell cat):
   ```yaml
   model:
     default: <model>
     provider: custom
     base_url: <url>
   ```
   `model.default` + `model.provider` is what a new session runs.
2. `hermes status` — prints `Model:` and `Provider:` under Environment, plus which API
   keys / OAuth logins are actually set. Confirms the runtime view.
3. `hermes model` — the interactive provider/model picker, and the authoritative
   "currently active" view: the active provider is marked `(●)` with a trailing
   `← currently active`, and the header prints `Current model:` / `Active provider:`.
   - PITFALL: it refuses to run piped or non-interactive — `'hermes model' requires an
     interactive terminal. It cannot be run through a pipe or non-interactive
     subprocess.` Launch it with `background=true, pty=true`, read it with
     `process(action="poll")`, then kill the session. Never pipe it.
   - Opening the picker is read-only; nothing changes until you select and confirm.

Three sources (config.yaml, `hermes status`, `hermes model`) should agree. When they do,
report all three — it is what makes the answer auditable.

## Per-session model — what THIS session is actually running
Steps 1–3 resolve the DEFAULT. When the question is "what is this session running", the
authoritative record is `~/.hermes/state.db` (SQLite), which stores the model per turn:
```sql
SELECT id, model, billing_provider, billing_base_url
  FROM sessions WHERE id = '<session id>';
SELECT model, billing_provider, billing_base_url, task, api_call_count
  FROM session_model_usage WHERE session_id = '<session id>';
```
`sessions.model` + `billing_provider` + `billing_base_url` records the requested model alias and configured endpoint —
stronger evidence than config.yaml, which only holds the default and can differ from a
session that switched mid-life. The current session id is in `$HERMES_SESSION_ID`. Query
it with python's `sqlite3` module via execute_code (the `sqlite3` CLI may be absent; the
`id` column is `id`, while the usage table keys on `session_id`). Do not treat these local records as independent upstream attestation. Report the endpoint
(base_url) alongside the model name: two custom providers can serve the same model name,
so the base_url is part of the answer.

## Changing the default model/provider
- Interactive: `hermes model` → pick provider → pick model.
- Scripted: `hermes config set model.default <model>`; also set `model.provider` and
  `model.base_url` when switching provider family.
- PITFALL: never hand-edit `~/.hermes/config.yaml` with file tools — the agent is refused
  (security guard), and a stray indent corrupts a live-gateway config. Use
  `hermes config set` (add `--force` for JSON-valued keys).
- Confirm after switching: `hermes status`, then one-shot E2E
  `hermes -z "reply one word: OK" -m <model> --provider custom` — `-m` WITHOUT
  `--provider custom` fails with "No LLM provider configured".

## Multi-provider custom endpoints (`custom_providers:`)
- `config.yaml` may list several OpenAI-compatible endpoints under `custom_providers:`,
  each with `name`, `base_url`, `key_env`, a default `model`, and a `models:` map of
  everything that endpoint serves. Read the `models:` map to answer "is model X
  available here?" instead of guessing.
- Secrets live in `~/.hermes/.env` under the `key_env` variable name; `config.yaml` only
  references them. Never inline a key into config.yaml.
- `model.provider: custom` + `model.base_url` selects which endpoint the default model
  resolves against — two providers can both serve the same model name, so the base_url
  is part of the answer, not decoration.

## Reporting
When you cross-checked more than one source, answer with a compact table (source →
value). It makes the claim auditable and surfaces a self-report-vs-config discrepancy
instead of hiding it.
