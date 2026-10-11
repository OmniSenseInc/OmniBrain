# Hermes WhatsApp bot — config keys (decision table)

## ~/.hermes/.env (edits apply on gateway restart unless noted)
| Key | Values | Effect |
|---|---|---|
| WHATSAPP_MODE | bot / self-chat | bot = separate bot number |
| WHATSAPP_ENABLED | true | master switch |
| WHATSAPP_ALLOWED_USERS | 62xxx,62xxx | DM allowlist |
| WHATSAPP_GROUP_POLICY | open\|pairing\|disabled\|allowlist | default pairing = group messages DROPPED silently |
| WHATSAPP_DM_POLICY | allowlist\|open\|pairing | allowlist = DMs restricted |
| WHATSAPP_ALLOW_ALL_USERS | true | required by startup validation whenever any policy is open |
| WHATSAPP_REQUIRE_MENTION | true\|false | true = tag-only (drops unmentioned group msgs); false = free intake |
| WHATSAPP_FREE_RESPONSE_CHATS | <jid>@g.us,... | groups bypass mention gate; re-read per message (NO restart) |
| WHATSAPP_SEND_READ_RECEIPTS | false | hides read receipts |
| WHATSAPP_HOME_CHANNEL / _THREAD_ID | | startup/shutdown notification target |

## config.yaml (via `hermes config set`)
| Key | Effect |
|---|---|
| display.show_reasoning | false = never prepend reasoning block |
| display.platforms.whatsapp.streaming | false = only final message sent (no streamed interim) |
| display.platforms.whatsapp.interim_assistant_messages | off/false = no interim messages |
| gateway.max_concurrent_sessions | parallel session cap (default derived per machine) |

## Diagnostics
- Bridge health: `curl -s localhost:3000/health` -> {"status":"connected",...}
- Session dir: ~/.hermes/whatsapp/session/ (creds.json field `me` present = paired)
- Current policy: `grep -E "^WHATSAPP_" ~/.hermes/.env`
- Gateway log: ~/.hermes/logs/gateway.log — inbound lines are logged for processed
  messages; DROPPED group messages (group_policy closed / not mentioned) leave NO
  log line, which is the tell for a policy problem.
