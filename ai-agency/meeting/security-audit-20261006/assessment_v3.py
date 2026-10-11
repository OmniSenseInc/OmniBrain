#!/usr/bin/env python3
"""OmniSense consulting v3: deterministic assessment, uncertainty and pilot gates.

Internal decision aid, not a validated predictor of AI success. No network/writes.
Usage: python3 assessment_v3.py input.json [--bank pertanyaan_v3.json]
       python3 assessment_v3.py --roi scenario.json
"""
import argparse
import json
import math
from pathlib import Path
from decision_v31 import VERSION, review_ok, expert_ok, consistency, decide, next_questions

EVIDENCE = {"self_reported", "reviewed", "observed"}
VERIFIED = {"reviewed", "observed"}


def number(value, name, minimum=0, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name}: angka terbatas wajib, bukan boolean/teks")
    if value < minimum or (maximum is not None and value > maximum):
        raise ValueError(f"{name}: di luar rentang")
    return value


def load_bank(path):
    bank = json.loads(Path(path).read_text(encoding="utf-8"))
    if bank.get('version') != VERSION:
        raise ValueError('Bank aktif harus version3.1; gunakan mesin legacy untuk bank lama')
    dims = bank["dimensions"]
    ids = [d["id"] for d in dims]
    if len(ids) != 8 or len(set(ids)) != 8:
        raise ValueError("Bank harus memiliki 8 dimensi unik")
    weights = [number(d["weight"], "weight", 0.001, 100) for d in dims]
    if abs(sum(weights) - 100) > 1e-8 and abs(sum(weights) - 1) > 1e-8:
        raise ValueError("Total bobot harus 100 atau 1")
    divisor = sum(weights)
    for d in dims:
        d["weight"] /= divisor
    for mode, count in (("screening", 16), ("discovery", 32)):
        qs = bank[mode]
        if len(qs) != count or len({q["id"] for q in qs}) != count:
            raise ValueError(f"{mode}: jumlah/ID soal tidak sah")
        for d in ids:
            if sum(q["dimension"] == d for q in qs) != count // 8:
                raise ValueError(f"{mode}: jumlah soal dimensi {d} tidak seimbang")
        for q in qs:
            if q["dimension"] not in ids or set(q["anchors"]) != set("12345"):
                raise ValueError(f"Rubrik tidak lengkap: {q['id']}")
            if not all(isinstance(q.get(k), str) and q[k].strip() for k in ("question", "evidence", "probe")):
                raise ValueError(f"Bukti/probe tidak lengkap: {q['id']}")
            if not isinstance(q.get("critical"), bool):
                raise ValueError(f"Penanda critical tidak sah: {q['id']}")
    actual = {q['id'] for mode in ('screening','discovery') for q in bank[mode] if q['critical']}
    if set(bank.get('critical_ids', [])) != actual:
        raise ValueError('critical_ids tidak konsisten dengan bank')
    for mode in ('screening','discovery'):
        known={q['id'] for q in bank[mode]}
        mins=bank.get('pilot_minimums',{}).get(mode)
        if not isinstance(mins,dict) or not mins or set(mins)-known:
            raise ValueError('Minimum pilot harus tersedia untuk mode aktif')
        for v in mins.values():
            number(v,'minimum pilot',1,5)
            if int(v)!=v:raise ValueError('Minimum pilot harus anchor utuh')
    return bank


def round_score(value, places=1):
    # Shared half-up convention with browser; avoid half-even drift at .25/.75.
    return round(value + 1e-9, places)

def assess(payload, bank):
    if not isinstance(payload, dict):
        raise ValueError('Payload harus object')
    if not isinstance(payload.get('consistency_resolutions', {}), dict):
        raise ValueError('consistency_resolutions harus object')
    if payload.get("version") not in ("3.0", VERSION):
        raise ValueError("version harus 3.0 atau 3.1; jawaban v1/v2 tidak dikonversi diam-diam")
    mode = payload.get("mode", "screening")
    if mode not in ("screening", "discovery"):
        raise ValueError("mode tidak dikenali")
    questions = bank[mode]
    question_map = {q["id"]: q for q in questions}
    answers = payload.get("answers", {})
    if not isinstance(answers, dict) or set(answers) - set(question_map):
        raise ValueError("answers harus object dengan ID soal dari mode yang dipilih")
    context = payload.get("context", {})
    if not isinstance(context, dict):
        raise ValueError("context harus object")
    normalized, not_applicable, evidence_gaps = {}, [], []
    for q in questions:
        a = answers.get(q["id"], {})
        if not isinstance(a, dict):
            raise ValueError(f"{q['id']}: jawaban harus object")
        value = a.get("value")
        if value is not None:
            number(value, q["id"], 1, 5)
            if int(value) != value:
                raise ValueError(f"{q['id']}: pilih anchor utuh 1-5")
        evidence = a.get("evidence", "self_reported")
        if evidence not in EVIDENCE:
            raise ValueError(f"{q['id']}: evidence tidak sah")
        source = a.get("source", "")
        if not isinstance(source, str):
            raise ValueError("source harus teks")
        if value is not None and evidence in VERIFIED and not source.strip():
            raise ValueError(f"{q['id']}: bukti terverifikasi perlu rujukan")
        na = a.get('applicability') == 'not_applicable'
        if na:
            if mode != 'discovery' or not q.get('allow_not_applicable') or q['critical'] or value is not None:
                raise ValueError(f"{q['id']}: tidak relevan tidak diizinkan pada butir ini")
            if not review_ok(a.get('review_record'), source) or not isinstance(a.get('reason'), str) or not a['reason'].strip():
                raise ValueError(f"{q['id']}: tidak relevan perlu alasan dan catatan review")
            not_applicable.append(q['id'])
        documented = evidence in VERIFIED and review_ok(a.get('review_record'), source)
        if value is not None and evidence in VERIFIED and not documented:
            evidence_gaps.append(q['id'])
        normalized[q["id"]] = {"value": value, "evidence": evidence, "source": source, 'documented': documented}

    dims, low, high, known_weight, verified_weight = [], 0, 0, 0, 0
    missing, critical_unknown, critical_weak, critical_unverified = [], [], [], []
    for d in bank["dimensions"]:
        all_qs = [q for q in questions if q["dimension"] == d["id"]]
        qs = [q for q in all_qs if q['id'] not in not_applicable]
        if len(qs) < len(all_qs) / 2:
            raise ValueError(f"{d['id']}: kurang dari separuh butir relevan, jangan hitung indeks")
        values, dl, dh = [], 0, 0
        for q in qs:
            a = normalized[q["id"]]
            value, weight = a["value"], d["weight"] / len(qs)
            if value is None:
                missing.append(q["id"])
                dl += 1
                dh += 5
                if q["critical"]:
                    critical_unknown.append(q["id"])
            else:
                values.append(value)
                dl += value
                dh += value
                known_weight += weight
                if a['documented']:
                    verified_weight += weight
                if q["critical"] and value < 3:
                    critical_weak.append(q["id"])
                if q["critical"] and not a['documented']:
                    critical_unverified.append(q["id"])
        dlo, dhi = dl / len(qs) * 20, dh / len(qs) * 20
        low += d["weight"] * dlo
        high += d["weight"] * dhi
        dims.append({"id": d["id"], "name": d["name"], "weight_percent": round_score(d["weight"] * 100, 6),
                     "score": round_score(dlo, 1) if len(values) == len(qs) else None,
                     "range": [round_score(dlo, 1), round_score(dhi, 1)], "answered": len(values), "total": len(qs),
                     'total_bank': len(all_qs)})
    score = round_score(low, 1) if not missing else None
    band = None if score is None else ("Fondasi kuat untuk ditinjau" if score >= 80 else
           "Fondasi berkembang" if score >= 60 else "Fondasi perlu diperkuat" if score >= 40 else "Fondasi awal")
    gaps = []
    for key in ("process", "problem", "process_owner"):
        if not isinstance(context.get(key), str) or not context[key].strip():
            gaps.append(key)
    baseline = context.get("baseline")
    baseline_ok = isinstance(baseline, dict) and all(isinstance(baseline.get(k), str) and baseline[k].strip()
                       for k in ("metric", "unit", "period", "source"))
    if baseline_ok:
        try:
            number(baseline.get("value"), "baseline.value")
        except ValueError:
            baseline_ok = False
    if not baseline_ok:
        gaps.append("baseline")
    for key, allowed in {"access_permission": {"confirmed", "denied", "unknown"},
                         "impact": {"low", "medium", "high", "unknown"},
                         "human_review": {"defined", "missing", "unknown"},
                         "fallback": {"defined", "missing", "unknown"}}.items():
        if context.get(key, "unknown") not in allowed:
            raise ValueError(f"context.{key}: nilai tidak sah")
    if context.get("access_permission") != "confirmed": gaps.append("access_permission")
    if context.get("impact", "unknown") == "unknown": gaps.append("impact")
    if context.get("human_review") != "defined": gaps.append("human_review")
    if context.get("fallback") != "defined": gaps.append("fallback")
    if context.get("impact") == "high" and not expert_ok(context): gaps.append("expert_review_required")
    issues = consistency(payload, normalized, bank)
    route, u_gaps, blocked = decide(payload, bank, normalized, critical_weak, critical_unverified, missing, gaps, issues)
    # Even a complete verified index cannot approve a use case or deployment.
    return {"version": VERSION, 'input_version': payload['version'], 'bank_revision': bank.get('bank_revision'),
            "mode": mode, "index_scale": "20-100; bukan probabilitas keberhasilan",
            "score": score, "band": band, "range": [round_score(low, 1), round_score(high, 1)],
            "range_meaning": "batas skenario jawaban belum diketahui, bukan confidence interval statistik",
            "answer_coverage_percent": round_score(known_weight * 100, 1),
            "verified_evidence_coverage_percent": round_score(verified_weight * 100, 1),
            'evidence_gaps': evidence_gaps, 'not_applicable': not_applicable,
            'review_meaning': 'cakupan catatan review lengkap; bukan pembuktian otomatis keaslian sumber atau otoritas penilai',
            'comparability': 'bandingkan hanya versi bank, konteks proses, dan daftar butir tidak relevan yang sama',
            "dimensions": dims, "missing": missing,
            "critical_unknown": critical_unknown, "critical_weak": critical_weak,
            "critical_unverified": critical_unverified, "context_gaps": gaps,
            'consistency_issues': issues, 'use_case_gaps': u_gaps, 'pilot_blockers': blocked,
            "route": route, "deployment_approved": False,
            "method_status": "heuristik internal; perlu kalibrasi lapangan, bukan sertifikasi",
            "next_questions": next_questions(route, gaps, issues,
                    critical_unknown + blocked + critical_weak + critical_unverified + missing, question_map, u_gaps)}


def roi(p):
    """Capacity value is not automatically cash savings. All assumptions explicit."""
    if not isinstance(p, dict):
        raise ValueError('Skenario harus object')
    names = ("monthly_volume", "minutes_before", "minutes_after_including_review",
             "adoption_fraction", "loaded_hourly_cost", "cash_realization_fraction",
             "monthly_operating_cost", "implementation_cost")
    v = {k: number(p.get(k), k, 0, 1 if k.endswith("fraction") else None) for k in names}
    hours = v["monthly_volume"] * (v["minutes_before"] - v["minutes_after_including_review"]) * v["adoption_fraction"] / 60
    capacity = hours * v["loaded_hourly_cost"]
    cash = capacity * v["cash_realization_fraction"] - v["monthly_operating_cost"]
    return {"capacity_hours_per_month": round(hours, 2), "capacity_value_per_month": round(capacity, 2),
            "net_cash_per_month": round(cash, 2),
            "payback_months": round(v["implementation_cost"] / cash, 2) if cash > 0 else None,
            "assumptions": v, "note": "Skenario, bukan janji ROI. Biaya review termasuk waktu sesudah; masukkan biaya operasi lengkap. Nilai kapasitas bukan penghematan kas otomatis."}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", nargs="?")
    p.add_argument("--bank", default=str(Path(__file__).with_name("pertanyaan_v3.json")))
    p.add_argument("--roi")
    a = p.parse_args()
    try:
        path = a.roi or a.input
        if not path: p.error("input JSON diperlukan")
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        result = roi(data) if a.roi else assess(data, load_bank(a.bank))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, TypeError, KeyError, OSError) as e:
        p.exit(2, f"Input ditolak: {e}\n")


if __name__ == "__main__":
    main()
