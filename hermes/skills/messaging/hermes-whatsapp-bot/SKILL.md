---
name: hermes-whatsapp-bot
description: "Use for Hermes WhatsApp bot: pairing, policies, tag-only."
---

# Hermes WhatsApp bot (Baileys bridge) — setup & operate

Class: standing up and running a Hermes gateway bot on WhatsApp WITHOUT an official
Meta/WhatsApp Cloud API key: pair a number, set access policy, control group
behavior, keep output professional.

## Pairing (no API key)
1. Run `hermes whatsapp` and pick mode "separate bot number" with a DEDICATED
   number (WhatsApp Business app on a second SIM) for anything client-facing.
2. The QR must be scanned by the user from their OWN terminal screen. PITFALL:
   never relay a QR from a background-process log into chat — monospace spacing is
   fragile and the QR expires in ~1-2 min; start the wizard foreground on a visible
   terminal and let the user scan there.
3. Session is saved under ~/.hermes/whatsapp/session/ (creds.json with `me` present
   = paired). Verify the bridge: `curl -s localhost:3000/health` ->
   {"status":"connected",...}.

## Access policy (env in ~/.hermes/.env; gateway restart applies)
- WHATSAPP_ALLOWED_USERS=62xxx,62xxx — DM allowlist (who may DM the bot).
- WHATSAPP_GROUP_POLICY=open + WHATSAPP_ALLOW_ALL_USERS=true — REQUIRED for group
  replies. PITFALL: default "pairing" silently drops ALL group messages (even
  tagged ones, with no log line) — symptom "bot ignores the group" => check
  group_policy first.
- WHATSAPP_DM_POLICY — the ONLY switch that decides inbound DMs: `allowlist` (only
  WHATSAPP_ALLOWED_USERS), `pairing` (handshake path), `open`. PITFALL:
  WHATSAPP_ALLOW_ALL_USERS=true is read ONLY when dm_policy=open — with
  dm_policy=allowlist the bot silently drops every DM from a non-allowlisted number,
  no log line, so a public lead-capture link pointing at the bot (wa.me/<bot number>)
  delivers into a void. Diagnose with `_is_dm_intake_allowed` in
  gateway/platforms/whatsapp_common.py before blaming the link or the bridge.
  Before changing policy, back the file up: `cp -p ~/.hermes/.env ~/.hermes/.env.bak`
  and state the restart requirement — policy is env-seeded and needs a gateway
  restart (unlike WHATSAPP_FREE_RESPONSE_CHATS, which is re-read per message).
- Opening DMs to strangers does NOT require a second number: gate the exception in
  the AGENT ROLE instead (the persona skill answers only DMs whose body starts with a
  marker the public surface always emits, and stays silent otherwise). Then
  dm_policy=open + a marker rule gives public intake while the bot still ignores
  ordinary DMs — the bot number stays the single public entry point.
- WHATSAPP_REQUIRE_MENTION — true = tag-only (hard gate), false = free response.
  PITFALL: with require_mention=true, unmentioned group messages are DROPPED
  entirely, so the bot cannot "silently observe" group context; observing requires
  free intake (false), which then relies on agent discipline not to reply to
  irrelevant chat. Choose hard silence (no context) vs context (risk of unwanted
  replies) — do not claim you can have both.
- Free response for SPECIFIC groups only: WHATSAPP_FREE_RESPONSE_CHATS=<jid>@g.us,...
  — re-read from env per message, so it applies WITHOUT a gateway restart.
- Quote-reply detection ("reply to the bot's message") depends on WhatsApp
  quotedParticipant metadata that Baileys often fails to surface — never promise
  it; @mention is the dependable trigger.

## Outbound @mentions are NOT supported (bridge sends text only)
- `POST /send` accepts only `{chatId, message, replyTo}`; `buildTextSendPayload`
  returns `{text}` and never sets Baileys' `mentions` field. So a message
  containing "@62xxxx" leaves as PLAIN TEXT — no highlight, no mention
  notification (only Signal has mention rendering in this codebase).
- PITFALL: never promise "aku tag X di grup". Options: (a) DM the person directly
  (works when their number is in WHATSAPP_ALLOWED_USERS — that policy gates
  inbound only), (b) plain text in the group (visible, no special notify), or
  (c) patch `/send` + `buildTextSendPayload` to pass `mentions` and restart the
  bridge — a PRODUCTION code change, get explicit approval first.
- Inbound mention detection is separate and works (`data.mentionedIds`).
- Verify a DM target BEFORE scheduling anything that depends on it: curl the
  bridge directly and send the probe to the REQUESTER's own number, never to the
  eventual recipients —
  `curl -s -X POST http://127.0.0.1:3000/send -H 'Content-Type: application/json'\
   --data-binary '{"chatId":"6281234567890@s.whatsapp.net","message":"tes"}'`
  → `{"success":true,"messageId":"..."}`. In a cron job, address DMs with
  `deliver: whatsapp:<number>@s.whatsapp.net` (comma-combine several targets).

## One-off sends from a CLI session (`hermes send`)
- `hermes send --to whatsapp "text"` delivers to the WhatsApp `home_channel` from
  `config.yaml` (bare platform name = home channel); `hermes send --to
  whatsapp:<chat_id>` targets a specific group/DM. `hermes send --list` prints every
  available target id. Named DM contacts appear by CONTACT NAME (e.g.
  `whatsapp:Vincent`), so a request to "send this to <person>" is resolved by running
  `hermes send --list` first rather than guessing a JID — never invent a target from
  the name alone. Attach a document/image by embedding `MEDIA:/abs/path` in the
  message text. No LLM call and no running agent turn required.
- Delivery is NOT independently verifiable. `hermes send` prints the chat_id it sent to,
  and it bypasses the delivery-obligation table (only agent-path responses get a row in
  `state.db` `delivery_obligations`); `whatsapp/bridge.log` logs connections and errors
  only, never send events. So report "CLI reports sent to <chat_id>" and ask the user to
  confirm in the app — do not claim the message was confirmed delivered.
- A `gateway.mirror: no session found for <chat>` warning in `logs/agent.log` right after
  a CLI send is EXPECTED (a CLI send has no session to mirror into) and does not mean the
  send failed. Do not chase it.

## Cosmetic: "url generation failed" in bridge.log (missing link-preview-js)
- An outbound message containing a link makes Baileys try to build a preview card;
the bridge then logs `level:40 ... Cannot find package 'link-preview-js' ... msg:"url generation failed"`
in `whatsapp/bridge.log`, with the msgId of the message. This is COSMETIC — the text
message still lands (the log line carries a msgId, i.e. it was processed), only the
preview card is missing. Do not report it as a failed send. Fixing it means
`npm install link-preview-js` inside
`~/.hermes/hermes-agent/scripts/whatsapp-bridge/node_modules/` — a production bridge
change, ask the owner first.
- Conversely, a send that DID work is confirmed only by the user seeing it: the log
gives no success line. Report "CLI reports sent to <chat_id>" and ask for a glance
in the app.

## Nag/reminder jobs (repeat until a human says stop)
- Build as `no_agent=True` + `script`: stdout is delivered verbatim, so repetition
  costs ZERO LLM tokens (the right call when API balance is tight), and EMPTY
  stdout sends nothing at all (watchdog pattern) — that is the lever for "go quiet
  the moment the human complies".
- The job itself has no chat context, but the SCRIPT can self-detect the stop word:
  inbound WhatsApp messages land in state.db — `messages` (session_id, role,
  content, timestamp as epoch float) joined to `sessions` (source, chat_id,
  chat_type, user_id) on session_id. Open it read-only
  (`sqlite3.connect("file:<path>?mode=ro", uri=True)`), and match
  `^\s*(stop|berhenti)\b` case-insensitively where role='user', source='whatsapp'
  and timestamp > the frozen start epoch. On match: write a flag file, then
  `sys.exit(0)` with no output for every later run. Freeze the start epoch at
  creation time (never "now") and scope the query to messages after it — otherwise
  a stale "stop" from an earlier chat pre-mutes the job.
- For "remind until a human responds" (any reply counts, not just a stop word), add
  `AND platform_message_id IS NOT NULL` to that query. Without it the job mutes on the
  first compaction artifact or cron-delivery row; real inbound messages are the only
  rows that carry a platform_message_id.
- PITFALL: `WHATSAPP_REQUIRE_MENTION=true` (tag-only) means an UNTAGGED group reply is
  dropped BEFORE it is persisted — a human can answer you and the nag keeps firing
  because nothing was recorded. Put the workaround in the nag text itself ("balas sambil
  tag bot ya, biar pengingat ini berhenti sendiri") and keep the fire cap low; there is no
  way to observe untagged chat without turning the hard gate off.
- State the stop contract inside the nag text ("balas STOP di chat ini untuk
  berhenti") — the human must know the word that works.
- Author the script via a RAW-string template (`r'''...'''`) with the epoch
  substituted by `.replace()`: a normal literal expands `\n`/`\U...` escapes into a
  broken source file, and `%`-formatting collides with the `%s` already present in
  the target script — both land as SyntaxError on write.
- Start at a wall-clock hour with a cron expr (e.g. `*/10 10-23 * * *` = 09:00 WIB
  onward, since the ticker evaluates in HOST LOCAL time — UTC+8 here), not
  "every 15m" (which fires immediately). Read `next_run_at` off the create response
  to confirm the offset instead of assuming the ticker is UTC.
- A cron expr repeats DAILY, so "this once, don't set it up again" needs an
  explicit `repeat=N` cap covering one day's fires (14 h x 6 = 84 for `*/10`); the
  job then completes itself. A day-time window also keeps it from buzzing at 03:00
  — state the window out loud so the user can object.
- `failure_deliver` decides where failure notices go (no_agent alerts on non-zero
  exit/timeout); point it at a channel the OWNER reads, not the nag targets, or the
  recipients get error spam instead of reminders.

## Custom commands: never a "/" prefix
- Messages starting with "/" are consumed by the gateway slash parser FIRST;
  unregistered commands are rejected as "unknown command" before any agent sees
  them. PITFALL: do not implement custom bot commands as "/x" and do not "fix"
  rejection by adding the trigger to the agent prompt — use @mention + keyword
  ("@bot whitelist <number>") and document that trigger.

## The bot must not restart its own gateway
- An agent running inside the gateway that runs `hermes gateway restart` kills its
  own turn. Prefer changes that take effect without a restart (env re-read per
  message) or hand the restart to an admin.

## "Bot nyangkut": diagnose the model, not the gateway
- A turn that dies in ~2s with NO reply is not a bridge/queue problem: check
  `sessions.model` in `state.db` (the session may be pinned to a model the global
  config no longer uses) and the newest `~/.hermes/sessions/request_dump_<session>_*.json`
  (has `error` + the exact `request.body`). `tail logs/gateway.log` shows
  "Non-retryable client error (HTTP 4xx) … Model: <x>".
- PITFALL (b.ai custom endpoint): `glm-5.3-flash` is always-thinking and REJECTS
  `reasoning_effort: medium` with HTTP 400 "该模型始终思考…请使用 low、high 或 max" —
  only low/high/max (or omitting it) work. Global `agent.reasoning_effort: medium`
  therefore kills EVERY glm-5.3-flash turn in ~1.7s, in the group AND in the CLI.
  Restarting the gateway does NOT fix it.
- Fix per model without touching the global effort:
  `hermes config set agent.reasoning_overrides '{"glm-5.3-flash": "low"}' --force`
  (the JSON-value form is required: the dotted form splits on the dot in "5.3" and
  writes a bogus nested key `glm-5: {3-flash: low}`). Verify resolution:
  `python -c "import sys;sys.path.insert(0,'.');from hermes_constants import resolve_reasoning_config;from hermes_cli.config import load_config;print(resolve_reasoning_config(load_config(),'glm-5.3-flash'))"`
  then one-shot E2E: `hermes -z "Balas satu kata: OK" -m glm-5.3-flash --provider custom`
  (`-m` without `--provider custom` fails with "No LLM provider configured").
- Don't "fix" this by editing `~/.hermes/config.yaml` with file tools — the agent is
  refused (security guard) and must use `hermes config set`.

## Restarting the gateway from a CLI session
- Safe when the agent runs in its OWN CLI session (different PID from the systemd
  user service): `hermes gateway restart` → returns "User service restarted (PID n)".
  Verify: `hermes gateway status`, `curl -s localhost:3000/health` →
  `{"status":"connected",...}`, and `tail logs/gateway.log` for "✓ whatsapp connected".
  Never do this from inside a gateway-hosted turn (kills the turn).

## Clean professional output
- Reasoning models (e.g. deepseek-v4-pro) stream reasoning tokens that surface in
  chat as unprofessional "thinking" text. For client-facing bots use a fast
  non-reasoning model (flash) AND disable per-platform display:
    hermes config set display.platforms.whatsapp.streaming false
    hermes config set display.platforms.whatsapp.interim_assistant_messages off
  plus display.show_reasoning=false and WHATSAPP_SEND_READ_RECEIPTS=false.
- Instruct the bot: answer directly, no preamble ("Baik...", "Dari analisis
  saya..."), no narration of process or retrieval steps.

## Concurrency model (why one group per client works)
- Every chat/group is its OWN session (agent:main:whatsapp:group:<jid>:<user>)
  with isolated context — data never mixes across groups, so group-per-client is
  also a data-isolation boundary. Different sessions run in PARALLEL up to config
  `max_concurrent_sessions`; within one session messages queue while a turn runs.

## Keep controls minimal
- This user's bots got stripped repeatedly from elaborate whitelist/command systems
  down to a single composition rule (role decided by who is in the group). Favor
  1-3 simple rules the team can recite over registration/command infrastructure.

## Anti-flood layer for a client-facing consultation lane
- Ship it as a PLUGIN, not gateway config: `~/.hermes/plugins/omnisense-consultation/`
  (`omnisense_wa_security.py` = admin gate, `wa_limits.py` = limits, `__init__.py` = the lane).
  Limits: per-sender 10/min & 60/h keyed by a SALTED HASH (raw numbers never stored), global
  120/min & 1000/h, max 3 queued messages per sender, 30 concurrent jobs, 2 model slots.
- Keep the admin allowlist in a ROOT-OWNED file (e.g. `/opt/omnisense-web/whatsapp-admin-policy.json`)
  rather than `~/.hermes/.env`: the loader must reject a policy file whose owner is not root or
  whose mode is group/world-writable, so a writable env file cannot promote a new admin.
- OUTSIDE senders never reach the real agent — route them to a separate TOOL-FREE lane, so a
  jailbreak attempt in a DM cannot touch files, terminal, or the database. Verify the routing in
  `logs/gateway.log` (`pre_gateway_dispatch skip: reason=omnisense_consultation_lane`). The
  remaining exposure is the ADMIN numbers: those sessions get the full toolset, so a compromised
  admin handset is the real DB risk — the lane split does not cover it.
- Say plainly that this is anti-FLOOD only: no permanent number/IP ban, no abusive-wording filter,
  and NO alerting (nobody is told when a limit trips). Do not imply a ban exists when asked whether
  the bot is "safe from trolls".
- The limits guard the CONSULTATION lane (inbound DMs from outsiders), NOT team/admin chats.

References: references/config-keys.md (full key decision table).
