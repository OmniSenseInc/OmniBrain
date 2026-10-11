"""Validate an agent's planned authority and recorded pilot results.

This module executes no tools. Complete records are not authentication or proof
that runtime permissions are enforced; the trusted operator must inspect traces.
"""
import hashlib
import json
import math

VERSION = '1.0'
CATEGORIES = {'normal', 'ambiguous', 'missing_data', 'tool_failure',
              'prompt_injection', 'out_of_scope'}
MODES = {'observe', 'draft', 'execute_bounded', 'human_required', 'forbidden'}


def text(value):
    return isinstance(value, str) and bool(value.strip())


def number(value):
    return (not isinstance(value, bool) and isinstance(value, (int, float))
            and math.isfinite(value))


def need(item, *keys):
    if not isinstance(item, dict) or not all(text(item.get(k)) for k in keys):
        raise ValueError('Kontrak agent belum lengkap: ' + ', '.join(keys))


def unique(items, label):
    if not isinstance(items, list) or not items:
        raise ValueError(label + ' harus berupa daftar tidak kosong')
    ids = []
    for item in items:
        need(item, 'id')
        ids.append(item['id'])
    if len(set(ids)) != len(ids):
        raise ValueError(label + ': ID duplikat')
    return items


def contract_hash(contract):
    return hashlib.sha256(json.dumps(contract, sort_keys=True, ensure_ascii=False,
        separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def validate_contract(contract, process, technical_owner, baseline=None):
    need(contract, 'process', 'objective', 'owner', 'authority_source_ref')
    if contract.get('version') != VERSION or contract['process'] != process:
        raise ValueError('Versi/proses kontrak agent berbeda dari kasus')
    if contract['owner'] != technical_owner:
        raise ValueError('Owner kontrak agent berbeda dari owner teknis kasus')
    if baseline is not None and contract.get('baseline_sha256') != contract_hash(baseline):
        raise ValueError('Baseline kontrak agent berbeda dari baseline kasus')
    if contract.get('pilot_environment') not in {'sandbox', 'shadow'}:
        raise ValueError('Pilot agent harus sandbox atau shadow, bukan aksi produksi')
    need(contract.get('data_policy'), 'purpose', 'allowed_scope', 'minimization',
         'retention_ref', 'permission_ref')
    need(contract.get('escalation'), 'owner', 'channel_ref', 'fallback_ref')
    need(contract.get('rollback'), 'owner', 'trigger', 'procedure_ref')
    actions = unique(contract.get('actions'), 'actions')
    for action in actions:
        need(action, 'description', 'resource_scope')
        if action.get('mode') not in MODES:
            raise ValueError('Mode kewenangan agent tidak dikenal')
        if action['mode'] == 'execute_bounded':
            need(action, 'effect_limit', 'authorization_ref', 'idempotency_ref')
            limits=action.get('effect_limits',{})
            count=limits.get('max_actions_per_run') if isinstance(limits,dict) else None
            if type(count) is not int or count<1 or not isinstance(action.get('changes_money'),bool):
                raise ValueError('Aksi otonom perlu batas jumlah integer positif dan klasifikasi uang')
            if action['changes_money']:
                amount=limits.get('max_amount')
                currency=limits.get('currency')
                if not number(amount) or amount<0 or not text(currency) or len(currency)!=3 or not currency.isalpha() or currency!=currency.upper():
                    raise ValueError('Aksi uang memerlukan batas nominal dan mata uang eksplisit')
        if action.get('requires_human') is not None and not isinstance(action['requires_human'], bool):
            raise ValueError('requires_human harus boolean')
        if action.get('requires_human') is True and action['mode'] != 'human_required':
            raise ValueError('Aksi yang memerlukan manusia tidak boleh otonom')
    exceptions = unique(contract.get('exceptions'), 'exceptions')
    if not CATEGORIES.difference({'normal'}).issubset({x['category'] for x in exceptions if 'category' in x}):
        raise ValueError('Jalur pengecualian/data kurang/gangguan/injeksi/di luar scope belum lengkap')
    for exception in exceptions:
        need(exception, 'category', 'trigger', 'response', 'owner')
    scenarios = unique(contract.get('evaluation_suite'), 'evaluation_suite')
    if not CATEGORIES.issubset({x.get('category') for x in scenarios}):
        raise ValueError('Suite evaluasi belum mencakup kasus normal dan pengecualian wajib')
    for scenario in scenarios:
        need(scenario, 'category', 'expected_behavior')
        if scenario['category'] not in CATEGORIES or not isinstance(scenario.get('blocking'), bool):
            raise ValueError('Kategori/blocking skenario tidak valid')
        if scenario['category'] != 'normal' and scenario['blocking'] is not True:
            raise ValueError('Kegagalan pengecualian kritis tidak boleh ditutupi rata-rata')
    metrics = unique(contract.get('metrics'), 'metrics')
    if not any(x.get('kind') == 'outcome' for x in metrics) or not any(x.get('kind') == 'guardrail' for x in metrics):
        raise ValueError('Metrik hasil dan batas mutu wajib ditentukan terpisah')
    for metric in metrics:
        need(metric, 'unit', 'definition', 'method_ref', 'target_source_ref')
        if metric.get('kind') not in {'outcome', 'guardrail'} or metric.get('comparison') not in {'gte', 'lte'}:
            raise ValueError('Jenis/perbandingan metrik tidak valid')
        if not number(metric.get('target')):
            raise ValueError('Target metrik harus angka hingga, bukan boolean/NaN')
        if metric['kind'] == 'outcome':
            metric_baseline = metric.get('baseline')
            need(metric_baseline, 'period', 'source_ref')
            if not number(metric_baseline.get('value')) or metric_baseline.get('unit') != metric['unit']:
                raise ValueError('Baseline metrik hasil tidak lengkap atau satuan berbeda')
    if baseline is not None:
        primary=next((x for x in metrics if x['id']==contract.get('primary_metric_id')),None)
        if primary is None or primary['kind']!='outcome':
            raise ValueError('Metrik utama harus merujuk baseline kasus')
        measured=primary['baseline']
        if any(measured.get(k)!=baseline.get(k) for k in ['value','unit','period']) or measured['source_ref']!=baseline.get('source'):
            raise ValueError('Baseline metrik utama berbeda dari angka/periode/sumber kasus')
    return {'contract_sha256': contract_hash(contract), 'runtime_authorized': False,
            'scenario_count': len(scenarios), 'metric_count': len(metrics)}


def validate_results(contract, result, process, technical_owner, baseline=None):
    checked = validate_contract(contract, process, technical_owner, baseline)
    need(result, 'contract_sha256', 'dataset_ref', 'measured_period', 'reviewer', 'review_ref')
    if result['contract_sha256'] != checked['contract_sha256']:
        raise ValueError('Hasil agent berasal dari versi kontrak berbeda')
    if type(result.get('sample_count')) is not int or result['sample_count'] < 1:
        raise ValueError('Cakupan sampel hasil harus dinyatakan, bukan klaim kelulusan umum')
    observed = unique(result.get('scenarios'), 'result.scenarios')
    specs = {x['id']: x for x in contract['evaluation_suite']}
    if set(specs) != {x['id'] for x in observed}:
        raise ValueError('Hasil harus mencakup setiap skenario kontrak, tanpa ID tambahan')
    for item in observed:
        need(item, 'observed_behavior', 'trace_ref', 'reviewer')
        if not isinstance(item.get('passed'), bool):
            raise ValueError('Hasil skenario harus boolean dengan trace/reviewer')
        if specs[item['id']]['blocking'] and item['passed'] is not True:
            raise ValueError('Skenario blocking gagal: ' + item['id'])
    actual = unique(result.get('metrics'), 'result.metrics')
    targets = {x['id']: x for x in contract['metrics']}
    if set(targets) != {x['id'] for x in actual}:
        raise ValueError('Metrik hasil tidak cocok dengan kontrak')
    for item in actual:
        need(item, 'unit', 'period', 'source_ref')
        spec = targets[item['id']]
        if item['unit'] != spec['unit'] or not number(item.get('value')) or item['period'] != result['measured_period']:
            raise ValueError('Nilai/satuan metrik hasil tidak valid')
        if (spec['comparison'] == 'lte' and item['value'] > spec['target']) or (
                spec['comparison'] == 'gte' and item['value'] < spec['target']):
            raise ValueError('Target/batas mutu belum terpenuhi: ' + item['id'])
    return dict(checked, documented_results_meet_contract=True)
