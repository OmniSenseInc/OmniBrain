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
        a.pop('review_record', None)
        if a.get('applicability') == 'not_applicable':
            raise ValueError('Tidak relevan hanya pada discovery yang direview tim')
    # Untrusted website context cannot supply authoritative review/approval records.
    if isinstance(p.get('context'), dict):
        p['context'].pop('expert_review', None)
    p.pop('consistency_resolutions', None)
    p.pop('use_case', None)
    r = assess(p, bank)
    r['context_reported'] = p.get('context', {})
    first = r['next_questions'][0]['probe'] if r['next_questions'] else 'Ukuran keberhasilan proses ini ingin dinilai dengan angka apa?'
    summary = f"Indeks awal Anda {r['score']}/100." if r['score'] is not None else f"Jawaban yang belum diketahui membuat indeks awal masih dalam rentang {r['range'][0]}–{r['range'][1]}/100."
    explanations = {
        'hentikan_akses_data': 'Penggunaan data untuk tujuan ini belum diizinkan, jadi akses dan pemrosesannya dihentikan. Kita masih bisa membahas alur umum tanpa memakai data tersebut.',
        'tunda_dan_review_risiko': 'Rekomendasi ditunda karena review risiko belum mengizinkan penggunaan ini.',
        'klarifikasi_bukti': 'Ada jawaban yang perlu diselaraskan sebelum memilih solusi.',
        'perkuat_fondasi': 'Ada prasyarat proses, data atau tanggung jawab yang perlu dibenahi sebelum mencoba solusi.',
        'discovery_dan_verifikasi': 'Ini berdasarkan jawaban Anda sendiri; bukti dan konteks proses masih perlu diperiksa.',
        'pilih_dan_uji_kelayakan_solusi': 'Kesiapan saja belum menentukan solusi; penyebab masalah dan kelayakan alternatif perlu diperiksa.'}
    r['draft_client'] = summary + ' ' + explanations.get(r['route'], 'Tim perlu meninjau rencana percobaan sebelum dijalankan.')
    if r['next_questions']:
        r['draft_client'] += ' ' + first
    r['handoff'] = {'source': 'website_v3_self_report', 'context': r['context_reported'],
                    'assessment': {k: r[k] for k in ('version', 'bank_revision', 'mode', 'score', 'range', 'route', 'critical_weak', 'critical_unknown', 'context_gaps', 'consistency_issues', 'use_case_gaps', 'pilot_blockers')},
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
