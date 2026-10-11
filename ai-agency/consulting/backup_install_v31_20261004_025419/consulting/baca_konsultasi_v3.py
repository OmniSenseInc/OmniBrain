#!/usr/bin/env python3
"""Read website consultation v3 over stdin or --file; no writes/messages/network."""
import argparse
import json
import sys
from pathlib import Path
from assessment_v3 import assess, load_bank

MARKER = '[KONSULTASI-OMNISENSE v3]'


def unique(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError('Field JSON berulang: ' + k)
        out[k] = v
    return out


def parse(text, bank):
    if len(text.encode('utf-8')) > 50000:
        raise ValueError('Pesan melebihi batas 50 KB')
    if not text.startswith(MARKER + '\n'):
        raise ValueError('Penanda konsultasi v3 tidak ditemukan')
    p = json.loads(text[len(MARKER):].strip(), object_pairs_hook=unique)
    if not isinstance(p, dict) or p.get('mode') != 'screening':
        raise ValueError('Pesan situs hanya menerima mode screening')
    if not isinstance(p.get('answers'), dict):
        raise ValueError('answers harus object')
    # Website claims never prove that evidence was independently reviewed.
    for a in p['answers'].values():
        if not isinstance(a, dict):
            raise ValueError('Jawaban harus object')
        a['evidence'] = 'self_reported'
        a['source'] = ''
    r = assess(p, bank)
    r['context_reported'] = p.get('context', {})
    first = r['next_questions'][0]['probe'] if r['next_questions'] else 'Ukuran keberhasilan proses ini ingin dinilai dengan angka apa?'
    summary = f"Indeks awal Anda {r['score']}/100." if r['score'] is not None else f"Jawaban yang belum diketahui membuat indeks awal masih dalam rentang {r['range'][0]}–{r['range'][1]}/100."
    r['draft_client'] = summary + ' Ini berdasarkan jawaban Anda dan perlu dibahas bersama bukti proses. ' + first
    r['handoff'] = {'source': 'website_v3_self_report', 'context': r['context_reported'],
                    'assessment': {k: r[k] for k in ('version', 'mode', 'score', 'range', 'route', 'critical_weak', 'critical_unknown', 'context_gaps')},
                    'evidence_status': 'laporan pengunjung; belum diverifikasi',
                    'solutions': 'belum dipilih; bandingkan proses/non-AI/software siap pakai/AI setelah discovery',
                    'decision_needed': 'lengkapi bukti dan scope; tim menentukan penawaran dan pilot',
                    'sent_to_team': False}
    return r


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--file')
    a = ap.parse_args()
    try:
        text = Path(a.file).read_text(encoding='utf-8') if a.file else sys.stdin.read(50001)
        print(json.dumps(parse(text, load_bank(Path(__file__).with_name('pertanyaan_v3.json'))), ensure_ascii=False, indent=2))
    except (ValueError, TypeError, KeyError, OSError) as exc:
        ap.exit(2, 'Input ditolak: ' + str(exc) + '\n')
