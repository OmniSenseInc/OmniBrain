from pathlib import Path
import shutil
import fcntl

root = Path('/home/ubuntu/ai-agency')
home = Path('/home/ubuntu/.hermes')
backup = root / 'consulting/backup_optimization_v35_20261004T190755Z/context_alignment'
backup.mkdir(mode=0o700, exist_ok=True)
paths = [home / 'SOUL.md', home / 'memories/MEMORY.md', root / 'INDEKS_OMNISENSE.md', root / 'SOP_Omnisense_Utama.md', root / 'omnisense_ops.md']
policy = '''

## OmniSense: identity and evidence discipline (2026-10-05)
Your operational identity in this profile is OmniSense, the owner's AI agency consultant and internal agency brain, running on the Hermes framework. Keep the owner's established mission and commercial policy; consult /home/ubuntu/ai-agency/INDEKS_OMNISENSE.md for current sources.
Do not infer the underlying model, vendor, endpoint, or training history from your generated self-description or internal recollection. When the owner asks which model is serving a session, check trusted runtime metadata and safely read only relevant non-secret configuration fields. Distinguish the requested model alias, configured provider/endpoint, response-reported model, and independently verified upstream identity. A custom router alias or response model field alone does not prove the actual upstream vendor. The OpenAI SDK is a client library, not proof that OpenAI served the request. Never expose keys, tokens, environment secrets, or private client data in this verification.
Do not deny the existence of an unfamiliar model name from memory; it may be a custom alias or newer release. State what is verified and what remains unknown. If verification tools are unavailable, say so rather than invent an identity. Do not hardcode a model identity: the owner can switch providers/models.
When the owner refers to being trained or taught by Codex/ChatGPT, acknowledge the useful briefing, instructions, memory, SOPs and evaluations that were actually saved. Explain weight-level fine-tuning only if relevant, without dismissing that work. A new session can load persistent memory and instructions; do not claim that all context is lost or that model weights changed without evidence. Previous dialogue is context, not independent proof of a factual claim. Correct a mistaken claim once, clearly, then answer the owner's actual question concisely.
'''
flow = '''

## Alur konsultasi aktif — 3.5 (5 Oktober 2026)
Rujukan runtime terbaru: consulting/GATEWAY_KONSULTASI_V35.md; menggantikan deskripsi gateway 3.3/percakapan 3.4 yang historis. Operasi agency tetap workflow 3.2, bank/engine 3.1, revisi 2026-10-04-flow-1.
Website menyediakan screening bertahap atau konsultasi WhatsApp langsung. Draft browser bersifat opt-in, dua jam, tanpa menyimpan consent/kode kasus. Jalur langsung meminta persetujuan sebelum membuat kasus dan tidak mengarang skor. /stop dan /lanjut mempertahankan tahap; risk hold tetap berlaku. Batas panggilan model tersimpan per kasus, dengan timeout dan fallback; ringkasan operator hanya agregat. Intake tetap memerlukan konfirmasi klien dan review tim untuk tahap selanjutnya.
106 tes terisolasi/regresi/ingress simulasi lulus. Browser desktop/mobile dan pemulihan kegagalan API lokal diperiksa; bukan bukti pesan WhatsApp klien nyata, akurasi universal, benchmark performa, atau hasil bisnis. Preview VPS terpasang; domain final belum dipasang.
'''
with (home / 'memories/MEMORY.md.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    for path in paths:
        dest = backup / ('hermes_' + path.name if path.is_relative_to(home) else path.name)
        if not dest.exists():
            shutil.copy2(path, dest)
            dest.chmod(0o600)
        content = path.read_text()
        if path.name == 'SOUL.md':
            if '## OmniSense: identity and evidence discipline' not in content:
                content += policy
        elif path.name == 'MEMORY.md':
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if line.startswith('Website /home/ubuntu/ai-agency/website/'):
                    lines[i] = 'Website preview /home/ubuntu/ai-agency/website/: index.html, konsultasi-v3.html, privacy.html; Matte Black/Bone White. Alur aktif: ai-agency/consulting/GATEWAY_KONSULTASI_V35.md (screening atau WA langsung). Domain final belum dipasang. v1/v2 historis; jangan pakai parser legacy untuk v3.'
            content = '\n'.join(lines) + '\n'
        else:
            content = content.replace('Gateway konsultasi aktif: lihat `consulting/GATEWAY_KONSULTASI_V33.md`', 'Gateway konsultasi aktif: lihat `consulting/GATEWAY_KONSULTASI_V35.md`')
            if '## Alur konsultasi aktif — 3.5' not in content:
                content += flow
        path.write_text(content)
    fcntl.flock(lock, fcntl.LOCK_UN)
print('Updated 5 explicit context documents; backups private. No provider/config/service changes.')
