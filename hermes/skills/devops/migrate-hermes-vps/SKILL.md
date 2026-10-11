---
name: migrate-hermes-vps
description: "Use when moving a Hermes install to another VPS or Git."
version: 1.0.0
metadata:
  hermes:
    tags: [migration, backup, vps, git, systemd, nginx, secrets]
---

# Migrating a Hermes install to a new VPS (via Git + encrypted bundle)

Git stores the brain; the VPS runs it. A new machine is restored in ~15-30 min
with one command, so reuse this pattern for every future move.

## 0. Rule of the split

| Layer | Where it goes |
|---|---|
| Code, config, skills, cron defs, website, docs | Git repo (private) |
| Secrets, client DBs, chat history, media assets | Encrypted bundle (AES-256), split <45 MB per part |
| Machine state (venv, node_modules, hermes-agent git packs, caches, logs) | Nothing — reinstall |

Never put `.env`, tokens, `*.sqlite3`, `state.db`, or `whatsapp/session/` in Git,
even in a private repo. Never send the bundle password through chat or store it in the repo.

## 1. Inventory (do this before promising anything)

```bash
ls -la ~/.hermes; du -sh ~/.hermes/*        # brain
ls -la ~/ai-agency; du -sh ~/ai-agency/*    # business data
systemctl list-units --state=running | grep -v '^  sys-'   # services
systemctl list-timers --all --no-pager     # timers
systemctl --user list-units --type=service # gateway, previews
ls /etc/nginx/sites-enabled /etc/nginx/conf.d /etc/systemd/system | grep -i <brand>
sudo ufw status verbose; ls /etc/letsencrypt/live
ls ~/.9router 2>/dev/null                  # local model router, if used
```

Also check `~/.config/systemd/user/*.service`, `crontab -l`, `/opt/<brand>-*`,
`/srv`, `/var/lib/<brand>*`, `/var/backups`. Record sizes — they decide what can be
dropped (venv, node_modules, git packs, media).

## 2. Bundle build

- `hermes backup -o <out>/01-hermes-home.zip` — covers config, `.env`, `auth.json`,
  `state.db`, sessions, skills, memories, plugins, cron, whatsapp session.
  It **excludes** `hermes-agent/`, `node/`, `__pycache__`, and **does not preserve
  file permissions** — chmod after restore.
- Business dir: `tar czf` excluding `.venv`, `__pycache__`.
- System layer: `sudo tar czf` of nginx conf, `/etc/letsencrypt`, fail2ban,
  `/etc/sudoers.d/*`, `/opt/<brand>-*`, systemd unit files.
- Also capture `ufw status numbered`, `iptables-save`, `apt-mark showmanual`,
  `pip freeze` for every venv, `npm ls -g --depth=0`, version report.
- Local patches to Hermes itself (e.g. a custom gateway authz hook) live in
  `~/.hermes/hermes-agent`: save `git diff HEAD -- gateway/` plus copies of touched files.
- Encrypt: `openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt -in f -out f.enc -pass env:PASS`
- Split: `split -b 45m -d -a 3 --additional-suffix=".part" f.enc f.enc.`
  (GitHub warns >50 MB, hard-blocks >100 MB.)
- `sha256sum *.part > SHA256SUMS` — list **only the parts**, never the plaintext
  archives, or verification reports missing files on the target.
- Generate a strong password for the owner, keep it out of the repo, tell them its path.

## 3. Repo staging

rsync the business dir into the repo excluding secrets/media/venv/caches, and copy
`hermes/{config.yaml,skills,memories,plugins,scripts,cron/jobs.json}`. Exclude
`skills/.curator_backups` and `.curator_ledger.jsonl` — they leak chat IDs and paths.
Exclude contact lists (client PII) such as `client_register.csv`.

**Pitfall:** a generic `*.part` / `*.enc` line in `.gitignore` silently drops the
bundle. Add explicit negations (`!bundel/*.part`, `!bundel/SHA256SUMS`) and verify
with `git ls-files | grep -c 'bundel/.*part'` before claiming the push is ready.

Commit gate before every push:

```bash
git ls-files | grep -E '\.env$|\.sqlite3$|state\.db|auth\.json|whatsapp/session'  # must be empty
```

## 4. Push (do not assume gh/token exists)

```bash
git push "https://x-access-token:${GITHUB_TOKEN}@github.com/${REPO}.git" main --force
git remote set-url origin "https://github.com/${REPO}.git"   # keep the token out of .git/config
```

## 5. Restore script (single entry point, staged)

Make each stage re-runnable (`bash pulihkan.sh <N>`) and abort with a non-zero exit
when a required bundle file is missing — a half-restore is worse than none. Use
`MIGRASI_HOME` / `MIGRASI_WORK` overrides so the whole thing can be rehearsed into a
temp directory without touching the live install.

Stage order: join parts + verify SHA256 + decrypt → install Hermes if absent →
unzip brain into `~/.hermes` (then rsync repo copies over it, chmod 700/600, remove
stale `*.lock`/sockets) → untar business dir → untar system layer (+`systemctl
daemon-reload`) → recreate venvs from `pip freeze` → UFW + fail2ban → optional local
router → enable services (`loginctl enable-linger <user>` for user units) → verify.

## 6. Verify with real output, not assumptions

```bash
python3 -c "import sqlite3;c=sqlite3.connect('file:.../state.db?mode=ro',uri=True);print(c.execute('pragma integrity_check').fetchone())"
ls -la ~/.hermes/whatsapp/session/creds.json   # WhatsApp session came back
python3 -c "...select count(*) from <domain table>"   # client/consultation data
curl -sS -o /dev/null -w '%{http_code}' http://127.0.0.1:8080/
hermes cron list
```

## 7. Manual steps that stay manual

- DNS A record → new IP (proxied), then `certbot renew --dry-run`.
- WhatsApp: restart the gateway; scan a new QR only if the restored session is rejected.
- Revoke the migration GitHub token; rotate API keys that travelled in the bundle.
- Delete the on-disk password file once the owner has copied it.

## Pitfalls seen in practice

- systemd units often hardcode a versioned release dir (`/opt/<brand>/security-v3-<stamp>`) —
  restore that exact path or the service will not start.
- UFW rules that allow 80/443 only from Cloudflare ranges make the site unreachable until
  DNS is switched; test locally on 127.0.0.1:8080 instead.
- A venv created with `uv` may have no `pip`; use `uv pip freeze --python <venv>/bin/python`.
- `hermes backup` skips unix sockets and prints "Backup incomplete" — normal, not a failure.
- Cloudflare-fronted nginx with `set_real_ip_from` + a `geo` guard returns 403 to
  non-Cloudflare peers: do not diagnose that as a broken restore.
