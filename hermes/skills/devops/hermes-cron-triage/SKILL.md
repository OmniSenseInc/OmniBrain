---
name: hermes-cron-triage
description: "Use when a Hermes cron job fails or is silently skipped."
---

# Hermes Cron Triage

Repair a scheduled Hermes job that stopped working, then PROVE it runs again from the
records the scheduler itself writes — not from the CLI's own success message.

## When to use

- A job's last run is `error`, `unknown`, or stale ("it stopped N days ago").
- The job claims `ok` but the user never received anything.
- A cron-driven digest/poster/monitor stopped updating its output files.

## Triage first, guess never

Three very different failures look identical from the outside:

1. **Drift-skip** — the job never ran and spent nothing; error text contains `[drift_skip]`.
2. **Preflight block** — provider/key/base_url cannot resolve; the agent never started.
3. **Real run failure** — provider error (401/404/429), tool denial, or timeout mid-run.

Read the durable record before touching config:

```bash
python3 scripts/cron_diagnose.py <job_id>   # this skill's script: job, runs, incidents, dumps, delivery
hermes cron list                            # last status + failure streak per job
hermes cron doctor                          # config-level health
hermes cron incidents                       # grouped failures with state + failure_type
hermes cron runs <job_id>                   # per-attempt history
```

## Failure classes and their fixes

| Signature | Cause | Fix |
|---|---|---|
| `[drift_skip]` / `[drift_skip:silent]` | Job has no per-job `provider`/`model`, so it follows the global assignment; the guard fails closed when that assignment changed since the job was created | Pin both explicitly: `hermes cron edit <id> --provider <named-provider> --model <model-id>`. Never disable `cron.model_drift_guard` to "fix" this — it is spend protection |
| `HTTP 400: no price for model '<id>:free'` | The job (or the global default it follows) resolves to a `:free` variant that has no price entry. Cron must RESERVE worst-case cost before starting, so a free-tier model with no registered price is rejected outright — chat tolerates it, cron does not | Use a priced model for the job: either unpin so it follows a global default that is priced, or pin `--model <priced-id>` from the provider's `models:` map. A `:free` model in `model.default` silently kills every cron run while chat keeps working |
| `HTTP 400/402: credit insufficient balance: balance=N` but the user says they refilled | The job is pinned to a provider/account the user has since ABANDONED — not a slow top-up | Compare the job's pinned `provider`/`model` against the GLOBAL `model.provider`/`base_url`; re-point to the active provider, or unpin (see below) |
| `HTTP 404 ... model not found` | Pinning `--provider custom` resolves through the GLOBAL `model.base_url`, so the model id must exist on that endpoint — and ids differ per endpoint (`deepseek-v4.1-flash` vs `deepseek/deepseek-v4.1-flash`) | Pin a NAMED provider whose `models:` map contains that exact id |
| `HTTP 429` | Throttle vs exhausted plan quota — opposite fixes | Replay the dumped request payload against the endpoint (below). Fresh 200s = transient throttle → add retry headroom: `hermes config set agent.api_max_retries 6` (the default 3 gives up in ~9s while a cron run has ~600s of budget). A 429 whose body carries a reset window = plan quota; retries will not help |
| `HTTP 401` insufficient balance / auth | Provider account billing (top-up) or a rotated key | User-side; not a job bug
| `status: unknown`, "Scheduler restarted after this execution's owner exited" | Scheduler died mid-run; side effects unknown | Re-run the job; do not assume the work half-happened |
| The agent denies its own command during a cron run | Cron has no interactive approval channel, so any would-prompt command is auto-denied | Make the job's commands non-interactive, or move the work into a script file the job runs |

## Surviving a user who switches provider often (unpin, don't re-pin)

When the user changes the global model/provider frequently (credit exhaustion, new
router), a job PINNED to a provider name breaks on every switch and has to be
hand-edited each time. The durable fix is to **remove the per-job pin** so the job
tracks the global assignment:

```bash
hermes cron edit <id> --provider '' --model ''   # empty string clears the pin
```

- After clearing, read the job back: `provider`/`model` should be `null` in
  `jobs.json`. Then force one run and confirm `last_status: ok` before trusting the
  cadence — do not assume clearing the pin is enough.
- The trade-off: an unpinned job is exactly what `cron.model_drift_guard` protects
  against, so a job that fires `[drift_skip]` must stay pinned (pin a NAMED provider
  whose `models:` map has the exact id). Clearing the pin is for jobs the guard is
  not gating.
- An unpinned job still needs the GLOBAL model to be priced — see the `:free` row in
  the table above. So "make cron follow whatever provider the user sets" only works
  while the user sets a paid model.
- The robust complement for any job whose real work needs no LLM (publishing,
  posting, file moves): make it `no_agent: true` + a `script`. A script-only job has
  no model resolution at all, so it is immune to provider/model churn — the strongest
  answer to "can this keep running when I switch providers".

## Per-job toolset whitelist (silent capability loss)

`enabled_toolsets` is a WHITELIST, not a preference. A job carrying
`["web", "terminal"]` has no `write_file` / `read_file` / `patch` (toolset
`file`), no `vision_analyze` (`vision`) and no `search_files`. The agent does not
error — it reports "that tool isn't installed", writes files through shell
`printf`, and silently skips any step that needed vision.

- Check this FIRST when a job's SOP requires a tool it "should" have: read the
  field out of `~/.hermes/cron/jobs.json` (`enabled_toolsets`; `null` = full
  default set).
- There is NO CLI flag for it — `hermes cron create` and `hermes cron edit` both
  lack it — so edit `jobs.json` directly (back it up first). The gateway re-reads
  that file and honors the edit, and its own later rewrite of the file preserves
  your value; confirm by running the job and re-reading the field.
- Valid toolset names are defined in the Hermes source `toolsets.py` (`web`,
  `terminal`, `file`, `vision`, `skills`, `browser`, `cronjob`, `memory`,
  `session_search`, `todo`, …). Adding a toolset is the fix; dropping `terminal`
  almost never is.
- When you extend a job's prompt with a new SOP step, name the exact command AND
  its interpreter, and make sure the toolsets that step needs are on the job —
  an instruction the job cannot execute is worse than no instruction.

## Probing what a cron session can actually do

Do not guess which tools a job has; measure it.

1. `hermes cron create "<far-future ISO timestamp>" "<probe prompt>" --name PROBE … --deliver local`
   The prompt is POSITIONAL — `--prompt` is rejected with `unrecognized arguments`.
   A far-future timestamp keeps the probe from ever firing on its own.
2. Set its `enabled_toolsets` in `jobs.json` to match the job you are investigating.
3. `hermes cron run <probe-id>` in the BACKGROUND and poll — a real agent run takes
   minutes; the exit status arrives long after the first tool call.
4. Read `~/.hermes/cron/output/<probe-id>/<ts>.md`: it holds the prompt plus what the
   agent reported it had and used.
5. A one-shot probe disables itself once it has run, so create a fresh probe per
   question. `hermes cron show` does not exist — use `list`, `runs`, `incidents`,
   `doctor`. Remove probes with `hermes cron remove <id>`.

## Replaying a failed request (throttle vs quota)

Every failed API call leaves the exact payload on disk:

```
~/.hermes/sessions/request_dump_cron_<job_id>_<ts>.json
  keys: timestamp, session_id, reason, request{method,url,headers,body}, error
```

Re-POST `request.body` verbatim with curl (`--data-binary @-`) using the same provider's key,
several times in a row. A burst that returns 200 proves the endpoint is healthy and the
original 429 was transient. Print header NAMES from a dump at most — never the
`Authorization` value.

## Verify delivery — a log line is not proof

- `cron.scheduler: Job 'x': delivered to <platform>:<chat>` in `~/.hermes/logs/agent.log` is
  the scheduler's own claim. The live-lane variant also carries `message_id=`; a delivery with
  no `message_id` is **unverified**.
- Durable evidence: `~/.hermes/cron/deliveries.db` (queue rows with `status`/`error`) and
  `state.db` table `delivery_obligations` (per-target `state`, `last_error`).
- A manual `hermes cron run` executes on the **standalone lane** (`source: direct`) and that
  send may not be recorded in the delivery queue at all. Say "the log says delivered, not yet
  provable" and ask the user to confirm receipt; the next scheduled tick runs the live lane and
  records the `message_id` you can quote.
- `hermes cron run` may execute SYNCHRONOUSLY (prints `Ran now: succeeded.` and blocks for the
  whole run — minutes for a digest) or only queue for the next tick, depending on lane. Either way
  run it in the background and poll the process, the output file and the durable record. A manual
  run also shifts the next scheduled time to now + interval, so the cadence drifts — tell the user
  the new next-run time instead of letting them discover it.

## Where the record lives

- `~/.hermes/cron/jobs.json` — `model`, `provider`, `model_snapshot`, `provider_snapshot`,
  `drift_alerted`, `failure_streak`, `last_error`, `deliver`, `origin`.
- `~/.hermes/cron/executions.db` — `executions` (status/source/pid/error per attempt) and
  `cron_incidents` (deduped failures with `state`, `failure_type`, `first_seen_at`).
- `~/.hermes/cron/output/<job_id>/<timestamp>.md` — full prompt + output of each run; the
  `## Error` section holds the traceback that never reaches the chat.
- `~/.hermes/logs/agent.log` — per-attempt provider errors carrying the `base_url` and `model`
  the run ACTUALLY used; this is how you catch a job silently pointed at another endpoint.

## Close the loop

1. Force a real run and wait for it to finish.
2. Confirm `last_status: ok`, `failure_streak: 0`, `hermes cron doctor` clean.
3. `hermes cron incidents ack <incident_id>` for every stale incident — they stay `alerted`
   forever otherwise and mask new ones.
4. Report the next scheduled run time, and say plainly anything you could not verify yourself.

## Pitfalls

- Long inline `python3 -c "..."` one-liners and heredocs get refused (terminal parser limit;
  cron's non-interactive approval denies them too). Plain shell file writes are fine —
  `printf '...' > file` in a `terminal`-only job succeeds with no denial — so prefer that, or
  write the script to a file and run the file (which is why this skill ships a script instead of
  a snippet to paste).
- Pinning `--provider custom` is the trap that looks like a fix: it resolves through the global
  `model.base_url`, so changing the global default silently breaks the job later.
- **A "refilled but still failing" job is usually a provider SWITCH, not a slow top-up.** When a job fails `HTTP 400/401: credit insufficient balance: balance=N`, compare the job's pinned `provider`/`model` (in `jobs.json`) against the GLOBAL `model.provider` / `base_url` in `config.yaml`. If the user says they "ganti provider" (or refilled a different account), the job is still pinned to the old, now-unfunded provider — re-point it: `hermes cron edit <id> --provider <Nama provider aktif> --model <model default provider itu>` (model id per provider; pakai nilai `model:` di blok custom_providers). Then force one run and confirm `last_status: ok` before trusting the cadence. Don't just tell the user to refill or wait for the next tick.
- Never conclude "the provider is down" from one 429 — replay before changing config.
- `hermes cron edit` with an unknown flag keeps the old value silently; read the job back from
  `jobs.json` (or the diagnose script) to confirm the pin actually landed.
