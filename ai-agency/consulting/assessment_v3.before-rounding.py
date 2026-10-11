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

VERSION = "3.0"
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
    return bank


def assess(payload, bank):
    if payload.get("version") != VERSION:
        raise ValueError("version harus 3.0; jawaban v1/v2 tidak dikonversi diam-diam")
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
    normalized = {}
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
        normalized[q["id"]] = {"value": value, "evidence": evidence, "source": source}

    dims, low, high, known_weight, verified_weight = [], 0, 0, 0, 0
    missing, critical_unknown, critical_weak, critical_unverified = [], [], [], []
    for d in bank["dimensions"]:
        qs = [q for q in questions if q["dimension"] == d["id"]]
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
                if a["evidence"] in VERIFIED:
                    verified_weight += weight
                if q["critical"] and value < 3:
                    critical_weak.append(q["id"])
                if q["critical"] and a["evidence"] not in VERIFIED:
                    critical_unverified.append(q["id"])
        dlo, dhi = dl / len(qs) * 20, dh / len(qs) * 20
        low += d["weight"] * dlo
        high += d["weight"] * dhi
        dims.append({"id": d["id"], "name": d["name"], "weight_percent": round(d["weight"] * 100, 6),
                     "score": round(dlo, 1) if len(values) == len(qs) else None,
                     "range": [round(dlo, 1), round(dhi, 1)], "answered": len(values), "total": len(qs)})
    score = round(low, 1) if not missing else None
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
    if context.get("impact") == "high": gaps.append("expert_review_required")
    if context.get("access_permission") == "denied":
        route = "hentikan_akses_data"
    elif critical_weak:
        route = "perkuat_fondasi"
    elif missing or critical_unverified or gaps:
        route = "discovery_dan_verifikasi"
    else:
        route = "rancang_pilot_terbatas"
    # Even a complete verified index cannot approve a use case or deployment.
    return {"version": VERSION, "mode": mode, "index_scale": "20-100; bukan probabilitas keberhasilan",
            "score": score, "band": band, "range": [round(low, 1), round(high, 1)],
            "range_meaning": "batas skenario jawaban belum diketahui, bukan confidence interval statistik",
            "answer_coverage_percent": round(known_weight * 100, 1),
            "verified_evidence_coverage_percent": round(verified_weight * 100, 1),
            "dimensions": dims, "missing": missing,
            "critical_unknown": critical_unknown, "critical_weak": critical_weak,
            "critical_unverified": critical_unverified, "context_gaps": gaps,
            "route": route, "deployment_approved": False,
            "method_status": "heuristik internal; perlu kalibrasi lapangan, bukan sertifikasi",
            "next_questions": [{"id": qid, "question": question_map[qid]["question"],
                                "probe": question_map[qid]["probe"]}
                               for qid in dict.fromkeys(critical_unknown + critical_weak + critical_unverified + missing)][:3]}


def roi(p):
    """Capacity value is not automatically cash savings. All assumptions explicit."""
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
