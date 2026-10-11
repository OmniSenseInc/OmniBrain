#!/usr/bin/env python3
"""One-shot triage dump for a Hermes cron job.

Usage:
    python3 cron_diagnose.py [job_id]

Prints the durable record the scheduler itself reads: job fields, recent
attempts, grouped incidents, the newest run output's error section, the newest
request dumps, and delivery-queue rows. Secret-looking keys are redacted; the
Authorization header value is never printed.

Read-only: SQLite files are opened with mode=ro, nothing is written.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME") or Path.home() / ".hermes")
SECRET_HINTS = ("key", "token", "secret", "password", "authorization", "credential")


def scrub(value, depth=0):
    """Recursively replace secret-looking values; keep structure readable."""
    if depth > 4:
        return "..."
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if isinstance(v, str) and any(h in str(k).lower() for h in SECRET_HINTS):
                out[k] = "[REDACTED]" if v else ""
            else:
                out[k] = scrub(v, depth + 1)
        return out
    if isinstance(value, list):
        return [scrub(v, depth + 1) for v in value[:5]]
    return value


def short(value, limit=110):
    text = " ".join(str(value).split())
    return text[:limit] + (" ..." if len(text) > limit else "")


def section(title):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:  # missing / malformed must not kill the dump
        print(f"  ! cannot read {path}: {type(exc).__name__}: {exc}")
        return None


def connect_ro(path):
    if not Path(path).exists():
        print(f"  ! missing {path}")
        return None
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as exc:
        print(f"  ! cannot open {path}: {type(exc).__name__}: {exc}")
        return None


JOB_FIELDS = (
    "id", "name", "enabled", "state", "schedule", "deliver", "skills",
    "model", "provider", "model_snapshot", "provider_snapshot", "drift_alerted",
    "failure_streak", "last_status", "last_error", "last_delivery_error",
    "last_delivery_unverified", "last_run_at", "next_run_at", "workdir",
    "no_agent", "script", "base_url",
)


def dump_jobs(job_id):
    section("JOBS (jobs.json)")
    data = read_json(HERMES_HOME / "cron" / "jobs.json")
    if not data:
        return
    jobs = data.get("jobs", data) if isinstance(data, dict) else data
    for job in jobs or []:
        if job_id and job.get("id") != job_id:
            continue
        print(f"-- job {job.get('id')} | {job.get('name')}")
        for field in JOB_FIELDS:
            if field in job:
                print(f"   {field}: {short(scrub(job[field]), 160)}")
        origin = scrub(job.get("origin"))
        if origin:
            print(f"   origin: {short(origin, 160)}")


def dump_executions(job_id):
    section("EXECUTIONS (cron/executions.db, newest first)")
    conn = connect_ro(HERMES_HOME / "cron" / "executions.db")
    if conn is None:
        return
    with conn:
        rows = conn.execute(
            "SELECT id, job_id, source, status, started_at, finished_at, "
            "substr(coalesce(error,''),1,150) AS err FROM executions "
            + ("WHERE job_id=? " if job_id else "")
            + "ORDER BY started_at DESC LIMIT 12",
            (job_id,) if job_id else (),
        ).fetchall()
        for row in rows:
            print(f"  {row['started_at']}  {row['status']:<9} {row['source']:<8} {short(row['err'])}")
        counts = conn.execute(
            "SELECT status, count(*) n, max(started_at) last FROM executions "
            + ("WHERE job_id=? " if job_id else "")
            + "GROUP BY status",
            (job_id,) if job_id else (),
        ).fetchall()
        print("  -- totals:", {r["status"]: f"{r['n']} (last {r['last']})" for r in counts})
    conn.close()


def dump_incidents(job_id):
    section("INCIDENTS (cron/executions.db, newest first)")
    conn = connect_ro(HERMES_HOME / "cron" / "executions.db")
    if conn is None:
        return
    with conn:
        rows = conn.execute(
            "SELECT id, error_sig, state, failure_type, first_seen_at, last_seen_at, closed_at, "
            "substr(coalesce(error,''),1,140) AS err FROM cron_incidents "
            + ("WHERE job_id=? " if job_id else "")
            + "ORDER BY last_seen_at DESC LIMIT 12",
            (job_id,) if job_id else (),
        ).fetchall()
        for row in rows:
            state = row["state"] or "?"
            flag = "OPEN" if state != "closed" else "closed"
            print(f"  [{flag}] {row['id']} {row['failure_type']} last={row['last_seen_at']}")
            print(f"          {short(row['err'], 150)}")
        open_n = conn.execute(
            "SELECT count(*) FROM cron_incidents WHERE state != 'closed'"
            + (" AND job_id=?" if job_id else ""),
            (job_id,) if job_id else (),
        ).fetchone()[0]
        print(f"  -- open incidents: {open_n}  (close stale ones: hermes cron incidents ack <id>)")
    conn.close()


def dump_output(job_id):
    section("LATEST RUN OUTPUT (cron/output/<job>/<ts>.md)")
    base = HERMES_HOME / "cron" / "output"
    files = []
    if job_id:
        files = sorted((base / job_id).glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        files = sorted(base.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        print(f"  ! no output files under {base}")
        return
    newest = files[0]
    print(f"  file: {newest}")
    text = newest.read_text(encoding="utf-8", errors="replace")
    idx = text.find("## Error")
    if idx == -1:
        print("  no '## Error' section -> the run did not report a failure")
    else:
        print("  --- error section (tail) ---")
        print("\n".join("  " + line for line in text[idx:].strip().splitlines()[-25:]))


def dump_request_dumps(job_id):
    section("REQUEST DUMPS (~/.hermes/sessions/request_dump_cron_*.json)")
    pattern = f"request_dump_cron_{job_id}*" if job_id else "request_dump_cron_*"
    files = sorted((HERMES_HOME / "sessions").glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        print("  (none)")
        return
    for path in files[:3]:
        data = read_json(path)
        if not isinstance(data, dict):
            continue
        request = data.get("request") or {}
        body = request.get("body") or {}
        if not isinstance(body, dict):
            body = {}
        messages = body.get("messages") or []
        print(f"  {path.name}")
        print(f"    reason: {short(data.get('reason'), 80)}")
        print(f"    error : {short(data.get('error'), 160)}")
        print(f"    url   : {request.get('url')}")
        print(f"    header names: {sorted((request.get('headers') or {}).keys())}   <- names only, never values")
        print(f"    model : {body.get('model')} | messages: {len(messages)} "
              f"| payload chars: {len(json.dumps(body))}")
        print("    replay: curl -s <url> -H \"Authorization: Bearer $KEY\" "
              "-H 'Content-Type: application/json' --data-binary @<body-as-json>")


def dump_deliveries(job_id):
    section("DELIVERY QUEUE (cron/deliveries.db)")
    conn = connect_ro(HERMES_HOME / "cron" / "deliveries.db")
    if conn is None:
        return
    with conn:
        try:
            rows = conn.execute(
                "SELECT execution_id, status, for_failure, created_at, finished_at, "
                "length(coalesce(content,'')) clen, substr(coalesce(error,''),1,140) err "
                "FROM deliveries ORDER BY created_at DESC LIMIT 8"
            ).fetchall()
        except Exception as exc:
            print(f"  ! query failed: {exc}")
            rows = []
        if not rows:
            print("  (no queue rows — a manual 'hermes cron run' uses the standalone lane,")
            print("   which may not be recorded here; the live lane writes message_id instead)")
        for row in rows:
            print(f"  {row['created_at']} {row['status']:<10} failure={row['for_failure']} "
                  f"chars={row['clen']} {short(row['err'])}")
    conn.close()


def dump_obligations(job_id):
    section("DELIVERY OBLIGATIONS (state.db)")
    conn = connect_ro(HERMES_HOME / "state.db")
    if conn is None:
        return
    with conn:
        try:
            rows = conn.execute(
                "SELECT obligation_id, platform, chat_id, state, attempts, last_error, updated_at "
                "FROM delivery_obligations ORDER BY updated_at DESC LIMIT 6"
            ).fetchall()
        except Exception as exc:
            print(f"  ! query failed: {exc}")
            rows = []
        for row in rows:
            print(f"  {row['platform']} {row['chat_id']} state={row['state']} "
                  f"attempts={row['attempts']} {short(row['last_error'], 80)}")
    conn.close()


def main():
    job_id = sys.argv[1] if len(sys.argv) > 1 else ""
    print(f"HERMES_HOME = {HERMES_HOME}")
    if not job_id:
        print("(no job_id given — dumping all jobs)")
    dump_jobs(job_id)
    dump_executions(job_id)
    dump_incidents(job_id)
    dump_output(job_id)
    dump_request_dumps(job_id)
    dump_deliveries(job_id)
    dump_obligations(job_id)
    section("NEXT STEPS")
    print("  1. classify the failure signature (drift-skip / preflight / real run)")
    print("  2. fix the config, never the guard")
    print("  3. hermes cron run <id>  (queues for next tick; run in background and poll)")
    print("  4. read the record back: last_status ok, failure_streak 0, doctor clean")
    print("  5. hermes cron incidents ack <id> for every stale incident")


if __name__ == "__main__":
    main()
