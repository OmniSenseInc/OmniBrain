"""Documented review and use-case gates. Records are not authentication proofs."""
from datetime import date

VERSION = '3.1'
PILOT_ROUTES = {'process': 'rancang_pilot_fondasi', 'software': 'rancang_pilot_non_ai',
                'rule_automation': 'rancang_pilot_non_ai', 'ai': 'rancang_pilot_ai'}


def text(v):
    return isinstance(v, str) and bool(v.strip())


def review_ok(r, source=None):
    if not isinstance(r, dict) or not all(text(r.get(k)) for k in
            ('reviewer', 'reviewed_at', 'source_ref', 'scope')) or r.get('finding') != 'supports':
        return False
    try:
        if date.fromisoformat(r['reviewed_at']).isoformat() != r['reviewed_at']:
            return False
    except (ValueError, TypeError):
        return False
    return source is None or r['source_ref'] == source


def expert_ok(context):
    r = context.get('expert_review', {})
    return (isinstance(r, dict) and r.get('status') == 'approved_with_conditions'
            and review_ok(r) and isinstance(r.get('conditions'), list)
            and bool(r['conditions']) and all(text(x) for x in r['conditions'])
            and r.get('conditions_met') is True)


def consistency(payload, normalized, bank):
    issues = []
    for rule in bank.get('consistency_rules', []):
        if rule['mode'] != payload.get('mode', 'screening'):
            continue
        a, b = (normalized.get(k, {}).get('value') for k in rule['questions'])
        if a is not None and b is not None and a <= rule['low_max'] and b >= rule['high_min']:
            resolution = payload.get('consistency_resolutions', {}).get(rule['id'])
            if not review_ok(resolution):
                issues.append({'id': rule['id'], 'questions': rule['questions'], 'description': rule['description']})
    declared = payload.get('consistency_issues', [])
    if not isinstance(declared, list):
        raise ValueError('consistency_issues harus list')
    for issue in declared:
        if not isinstance(issue, dict) or not text(issue.get('description')):
            raise ValueError('Issue konsistensi perlu deskripsi')
        if issue.get('status') != 'resolved' or not review_ok(issue.get('resolution')):
            issues.append({'id': issue.get('id', 'reported_conflict'), 'questions': [], 'description': issue['description']})
    return issues


def use_case_gaps(u):
    if not isinstance(u, dict) or u.get('solution_type') not in PILOT_ROUTES:
        return ['solution_type']
    gaps = []
    for k in ('objective', 'selection_reason'):
        if not text(u.get(k)):
            gaps.append(k)
    options = u.get('alternatives', [])
    if not isinstance(options, list) or len(options) < 2 or not all(
            isinstance(x, dict) and text(x.get('option')) and text(x.get('reason')) for x in options):
        gaps.append('alternatives')
    diagnosis = u.get('diagnosis', {})
    if not isinstance(diagnosis, dict) or not text(diagnosis.get('selected_cause')) or not text(diagnosis.get('evidence_ref')):
        gaps.append('diagnosis')
    for k in ('value_case', 'feasibility'):
        item = u.get(k, {})
        if not isinstance(item, dict) or item.get('status') != 'supported' or not text(item.get('source_ref')):
            gaps.append(k)
    pilot = u.get('pilot_plan', {})
    if not isinstance(pilot, dict) or not all(text(pilot.get(k)) for k in
            ('owner', 'scope', 'success_metric', 'period', 'stop_condition', 'rollback', 'review_owner')):
        gaps.append('pilot_plan')
    return gaps


def decide(payload, bank, normalized, critical_weak, critical_unverified, missing, gaps, issues):
    context = payload.get('context', {})
    u = payload.get('use_case', {})
    u_gaps = use_case_gaps(u)
    solution = u.get('solution_type') if isinstance(u, dict) else None
    requirements = bank.get('pilot_minimums', {}).get(payload.get('mode', 'screening'), {})
    blocked = [qid for qid, minimum in requirements.items()
               if normalized[qid]['value'] is not None and normalized[qid]['value'] < minimum]
    if context.get('access_permission') == 'denied':
        route = 'hentikan_akses_data'
    elif isinstance(context.get('expert_review'), dict) and context['expert_review'].get('status') == 'rejected':
        route = 'tunda_dan_review_risiko'
    elif issues:
        route = 'klarifikasi_bukti'
    elif (critical_weak or blocked) and (solution != 'process' or
          any(k in ('S1b', 'S7a', 'S7b', 'D1d', 'D2c', 'D7a', 'D7b', 'D7c', 'D7d') for k in critical_weak)
          or not isinstance(u.get('remediates'), list) or not set(critical_weak + blocked).issubset(u['remediates'])):
        route = 'perkuat_fondasi'
    elif gaps or missing or critical_unverified:
        route = 'discovery_dan_verifikasi'
    elif isinstance(u, dict) and any(isinstance(u.get(k), dict) and u[k].get('status') == 'not_viable'
                                    for k in ('value_case', 'feasibility')):
        route = 'tunda_atau_pilih_alternatif'
    elif u_gaps:
        route = 'pilih_dan_uji_kelayakan_solusi'
    else:
        route = PILOT_ROUTES[solution]
    return route, u_gaps, blocked


def next_questions(route, gaps, issues, candidates, questions, u_gaps):
    if route in ('hentikan_akses_data', 'tunda_dan_review_risiko'):
        return []
    if issues:
        return [{'id': 'clarify_conflict', 'question': issues[0]['description'],
                 'probe': 'Untuk proses yang sedang kita bahas, keadaan sebenarnya bagaimana?'}]
    context_probes = {
        'process': 'Satu proses apa yang ingin dibenahi lebih dulu?',
        'problem': 'Hambatan apa yang paling terasa pada proses itu?',
        'process_owner': 'Siapa yang bertanggung jawab atas proses ini?',
        'baseline': 'Apa ukuran kondisi saat ini yang bisa kita gunakan sebagai pembanding?',
        'access_permission': 'Siapa yang berwenang mengizinkan penggunaan data untuk tujuan ini?',
        'impact': 'Apa akibatnya bila solusi pada proses ini memberikan hasil yang salah?',
        'human_review': 'Siapa yang akan meninjau hasil sebelum dipakai?',
        'fallback': 'Bagaimana proses dilanjutkan jika alat mengalami gangguan?',
        'expert_review_required': 'Siapa penanggung jawab yang dapat meninjau risiko penggunaan ini?'}
    result = [{'id': k, 'question': context_probes[k], 'probe': context_probes[k]}
              for k in gaps if k in context_probes]
    result += [{'id': k, 'question': questions[k]['question'], 'probe': questions[k]['probe']}
               for k in dict.fromkeys(candidates)]
    if not result and u_gaps:
        probes = {'solution_type':'Alternatif perbaikan apa yang sudah dibandingkan untuk proses ini?',
                  'objective':'Hasil apa yang ingin dicapai dari percobaan ini?',
                  'selection_reason':'Apa alasan memilih opsi ini dibanding alternatifnya?',
                  'alternatives':'Alternatif perbaikan apa yang sudah dibandingkan?',
                  'diagnosis':'Apa bukti bahwa hambatan yang kita temukan merupakan penyebab utama masalah ini?',
                  'value_case':'Apa bukti manfaat yang cukup untuk melanjutkan percobaan ini?',
                  'feasibility':'Apa bukti bahwa opsi ini dapat dijalankan dengan sumber daya yang tersedia?',
                  'pilot_plan':'Siapa penanggung jawab percobaan yang akan dijalankan?'}
        question = probes[u_gaps[0]]
        result = [{'id': 'use_case', 'question': question, 'probe': question}]
    return result[:3]
