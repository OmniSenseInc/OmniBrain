"""Synthetic examples for tests only; never evidence of real client results."""
import copy
import json
from pathlib import Path
from agent_contract import CATEGORIES, contract_hash


def agent_fixture():
    p=json.loads(Path(__file__).with_name('input_contoh_discovery_reviewed.json').read_text())
    return {'version':'1.0','process':p['context']['process'],
        'objective':'SIMULASI mempercepat pencarian informasi tiket dengan mutu terjaga',
        'owner':'SIMULASI CTO','authority_source_ref':'SIMULASI rancangan scope',
        'pilot_environment':'shadow','baseline_sha256':contract_hash(p['context']['baseline']),'primary_metric_id':'duration',
        'data_policy':{'purpose':'SIMULASI pencarian tiket','allowed_scope':'SIMULASI dataset anonim',
                      'minimization':'SIMULASI hapus identitas','retention_ref':'SIMULASI kebijakan',
                      'permission_ref':'SIMULASI persetujuan dataset'},
        'escalation':{'owner':'SIMULASI lead','channel_ref':'SIMULASI kanal internal','fallback_ref':'SIMULASI manual'},
        'rollback':{'owner':'SIMULASI CTO','trigger':'SIMULASI mutu di bawah batas','procedure_ref':'SIMULASI runbook'},
        'actions':[{'id':'find','description':'SIMULASI cari tiket','resource_scope':'SIMULASI tiket tenant sendiri','mode':'observe'},
                   {'id':'draft','description':'SIMULASI draf ringkasan','resource_scope':'SIMULASI workspace internal','mode':'draft'},
                   {'id':'send','description':'SIMULASI kirim ke pelanggan','resource_scope':'SIMULASI kanal klien','mode':'human_required','requires_human':True}],
        'exceptions':[{'id':x,'category':x,'trigger':'SIMULASI '+x,'response':'SIMULASI tahan dan eskalasi','owner':'SIMULASI lead'}
                      for x in sorted(CATEGORIES-{'normal'})],
        'evaluation_suite':[{'id':x,'category':x,'expected_behavior':'SIMULASI sesuai scope atau eskalasi','blocking':True}
                            for x in sorted(CATEGORIES)],
        'metrics':[{'id':'duration','kind':'outcome','unit':'menit/tiket','definition':'SIMULASI waktu kerja termasuk review',
                    'method_ref':'SIMULASI metode pengukuran','target_source_ref':'SIMULASI target disepakati',
                    'comparison':'lte','target':8,'baseline':{'value':12,'unit':'menit/tiket','period':'7 hari','source_ref':'simulasi: sampel 30 tiket'}},
                   {'id':'quality','kind':'guardrail','unit':'persen','definition':'SIMULASI jawaban benar dari sampel',
                    'method_ref':'SIMULASI review manual','target_source_ref':'SIMULASI batas mutu',
                    'comparison':'gte','target':95}]}


def result_fixture(contract=None,scope_version=1,tenant='SIMULASI_A',case='CASE1'):
    c=copy.deepcopy(contract) if contract else agent_fixture()
    return {'tenant_id':tenant,'case_id':case,'scope_version':scope_version,'bank_revision':'2026-10-04-flow-1',
        'contract_sha256':contract_hash(c),'dataset_ref':'SIMULASI held-out dataset',
        'measured_period':'SIMULASI 2 minggu','sample_count':30,'reviewer':'SIMULASI lead','review_ref':'SIMULASI review hasil',
        'scenarios':[{'id':x['id'],'passed':True,'observed_behavior':'SIMULASI sesuai expectation',
                      'trace_ref':'SIMULASI trace '+x['id'],'reviewer':'SIMULASI lead'} for x in c['evaluation_suite']],
        'metrics':[{'id':x['id'],'value':7 if x['id']=='duration' else 97,'unit':x['unit'],
                    'period':'SIMULASI 2 minggu','source_ref':'SIMULASI pengukuran '+x['id']} for x in c['metrics']]}
