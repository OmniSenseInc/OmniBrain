import copy
import json
import tempfile
import unittest
from pathlib import Path
from assessment_v3 import assess, load_bank
from baca_konsultasi_v3 import parse, MARKER
from workflow_agency import apply_event, STAGES
from fixtures_agent import agent_fixture, result_fixture

HERE=Path(__file__).parent
BANK=load_bank(HERE/'pertanyaan_v3.json')
FIXTURE=json.loads((HERE/'input_contoh_discovery_reviewed.json').read_text())


class DecisionTests(unittest.TestCase):
    def p(self):return copy.deepcopy(FIXTURE)

    def test_source_string_is_not_review(self):
        p=self.p()
        for a in p['answers'].values():a.pop('review_record',None)
        r=assess(p,BANK)
        self.assertEqual(r['verified_evidence_coverage_percent'],0)
        self.assertEqual(r['route'],'discovery_dan_verifikasi')

    def test_malformed_context_and_resolution_rejected(self):
        for field in ['answers','context','consistency_resolutions']:
            p=self.p();p[field]=None
            with self.assertRaises(ValueError):assess(p,BANK)
        with self.assertRaises(ValueError):assess([],BANK)

    def test_process_and_operator_weakness_block_ai(self):
        for qid in ['D4d','D6a','D6b']:
            p=self.p();p['answers'][qid]['value']=1
            r=assess(p,BANK)
            self.assertEqual(r['route'],'perkuat_fondasi');self.assertIn(qid,r['pilot_blockers'])

    def test_foundation_pilot_must_remediate_and_cannot_bypass_permission(self):
        p=self.p();p['answers']['D4d']['value']=1;p['use_case']['solution_type']='process'
        self.assertEqual(assess(p,BANK)['route'],'perkuat_fondasi')
        p['use_case']['remediates']=['D4d']
        self.assertEqual(assess(p,BANK)['route'],'rancang_pilot_fondasi')
        p['answers']['D7b']['value']=1;p['use_case']['remediates'].append('D7b')
        self.assertEqual(assess(p,BANK)['route'],'perkuat_fondasi')

    def test_non_ai_pilot_distinct_and_no_deploy(self):
        p=self.p();p['use_case']['solution_type']='rule_automation'
        r=assess(p,BANK)
        self.assertEqual(r['route'],'rancang_pilot_non_ai');self.assertFalse(r['deployment_approved'])

    def test_missing_diagnosis_prevents_pilot(self):
        p=self.p();del p['use_case']['diagnosis']
        r=assess(p,BANK)
        self.assertEqual(r['route'],'pilih_dan_uji_kelayakan_solusi')
        self.assertIn('diagnosis',r['use_case_gaps'])

    def test_expert_review_can_finish_but_conditions_required(self):
        p=self.p();p['context']['impact']='high'
        self.assertIn('expert_review_required',assess(p,BANK)['context_gaps'])
        p['context']['expert_review']=dict(p['answers']['D7a']['review_record'],status='approved_with_conditions',conditions=['SIMULASI review100persen'],conditions_met=True)
        self.assertEqual(assess(p,BANK)['route'],'rancang_pilot_ai')
        p['context']['expert_review']['conditions_met']=False
        self.assertIn('expert_review_required',assess(p,BANK)['context_gaps'])
        p['context']['expert_review']['status']='rejected'
        self.assertEqual(assess(p,BANK)['route'],'tunda_dan_review_risiko')

    def test_not_applicable_is_restricted_and_explicit(self):
        p=self.p();a=p['answers']['D3d'];a.update(value=None,applicability='not_applicable',reason='SIMULASI tidak perlu migrasi')
        r=assess(p,BANK)
        self.assertEqual(r['not_applicable'],['D3d']);self.assertNotIn('D3d',r['missing'])
        self.assertEqual(next(d for d in r['dimensions'] if d['id']=='D3')['total'],3)
        p['answers']['D7a'].update(value=None,applicability='not_applicable',reason='bypass')
        with self.assertRaises(ValueError):assess(p,BANK)

    def test_not_applicable_needs_review(self):
        p=self.p();p['answers']['D3d'].update(value=None,applicability='not_applicable',reason='SIMULASI')
        del p['answers']['D3d']['review_record']
        with self.assertRaises(ValueError):assess(p,BANK)

    def test_conflict_is_clarified_not_scored_away(self):
        p=self.p();p['answers']['D2a']['value']=1;p['answers']['D2b']['value']=5
        r=assess(p,BANK)
        self.assertEqual(r['route'],'klarifikasi_bukti');before=r['score']
        p['consistency_resolutions']={'discovery_data_quality':dict(p['answers']['D2b']['review_record'])}
        r=assess(p,BANK)
        self.assertEqual(r['score'],before);self.assertEqual(r['route'],'perkuat_fondasi')

    def test_parser_denied_access_draft_matches_decision(self):
        p={'version':'3.1','mode':'screening','context':dict(self.p()['context'],access_permission='denied'),
           'answers':{q['id']:{'value':5} for q in BANK['screening']}}
        r=parse(MARKER+'\n'+json.dumps(p),BANK)
        self.assertEqual(r['route'],'hentikan_akses_data');self.assertIn('dihentikan',r['draft_client'])
        self.assertEqual(r['next_questions'],[]);self.assertFalse(r['handoff']['sent_to_team'])

    def test_website_cannot_supply_authoritative_reviews(self):
        p={'version':'3.1','mode':'screening','context':dict(self.p()['context'],impact='high',expert_review={'status':'approved_with_conditions'}),
           'answers':{q['id']:{'value':5,'evidence':'reviewed','source':'claim','review_record':self.p()['answers']['D7a']['review_record']} for q in BANK['screening']},
           'consistency_resolutions':{'x':{}},'use_case':self.p()['use_case']}
        r=parse(MARKER+'\n'+json.dumps(p),BANK)
        self.assertEqual(r['verified_evidence_coverage_percent'],0)
        self.assertIn('expert_review_required',r['context_gaps']);self.assertIn('solution_type',r['use_case_gaps'])


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp_root=(HERE/'test-tmp').resolve();self.temp_root.mkdir(exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=self.temp_root);self.db=Path(self.tmp.name)/'ledger.sqlite3'
        self.actor={'id':'SIMULASI operator','role':'team'};self.count=0
        self.record={'revision':0,'scope_version':0,'stage':'lead'}
    def tearDown(self):
        if not Path(self.tmp.name).resolve().is_relative_to(self.temp_root):raise RuntimeError('Unsafe test cleanup path')
        self.tmp.cleanup()
    def event(self,action='update',data=None,case='CASE1',tenant='SIMULASI_A',commit=True,actor=None):
        self.count+=1
        e={'id':'E'+str(self.count),'expected_revision':self.record['revision'],'action':action,'data':data or {}}
        r=apply_event(self.db,tenant,case,e,actor or self.actor,BANK,commit)
        self.record=r['case'];return e,r
    def initial_data(self):
        p=copy.deepcopy(FIXTURE)
        return {'scope':{'process':p['context']['process'],'problem':p['context']['problem'],'data_scope':'SIMULASI tiket'},
                'coordinator':'SIMULASI CMO','technical_owner':'SIMULASI CTO','client_owner':'SIMULASI lead','adoption_owner':'SIMULASI lead',
                'agent_contract':agent_fixture(),
                'baseline':p['context']['baseline'],'process_map_ref':'SIMULASI log alur',
                'diagnosis':p['use_case']['diagnosis'],'assessment_payload':p,
                'commercial':{'scope_ref':'SIMULASI scope','terms_ref':'SIMULASI termin','owner':'SIMULASI CEO'},
                'handoff':{'summary':'SIMULASI kebutuhan','decision_needed':'SIMULASI review scope','recipient':'SIMULASI tim',
                           'status':'accepted_by_team','reviewed_by':'SIMULASI CTO','review_ref':'SIMULASI keputusan'}}
    def approvals(self,kinds):
        return {k:{p:{'approved':True,'approved_by':'SIMULASI '+p,'source_ref':'SIMULASI keputusan '+k,
                     'scope_version':self.record['scope_version'],'case_id':'CASE1','tenant_id':'SIMULASI_A','bank_revision':BANK['bank_revision']}
                   for p in ['team','client']} for k in kinds}

    def test_dry_run_does_not_create_database(self):
        self.event(data=self.initial_data(),commit=False)
        self.assertFalse(self.db.exists())

    def test_repeat_event_is_idempotent_and_changed_content_rejected(self):
        e,r=self.event(data=self.initial_data())
        again=apply_event(self.db,'SIMULASI_A','CASE1',e,self.actor,BANK,True)
        self.assertTrue(again['idempotent']);self.assertEqual(r['case'],again['case'])
        e['data']['coordinator']='different'
        with self.assertRaises(ValueError):apply_event(self.db,'SIMULASI_A','CASE1',e,self.actor,BANK,True)

    def test_stale_revision_rejected(self):
        self.event(data=self.initial_data())
        with self.assertRaises(ValueError):apply_event(self.db,'SIMULASI_A','CASE1',{'id':'stale','expected_revision':0,'action':'advance'},self.actor,BANK,True)

    def test_tenants_with_same_case_id_do_not_share_state(self):
        self.event(data=self.initial_data())
        self.record={'revision':0}
        self.event(case='CASE1',tenant='SIMULASI_B',data={'coordinator':'B'})
        self.assertNotIn('scope',self.record['data']);self.assertEqual(self.record['tenant_id'],'SIMULASI_B')

    def test_client_role_cannot_write_or_approve(self):
        with self.assertRaises(ValueError):self.event(actor={'id':'SIMULASI client','role':'client'},data=self.initial_data())
        with self.assertRaises(ValueError):self.event(actor={'id':'SIMULASI op','role':'operator'},data={'approvals':{}})

    def test_scope_change_invalidates_approvals_and_results(self):
        self.event(data=self.initial_data())
        self.event(data={'approvals':self.approvals(['commercial','pilot','go_live']),'pilot_result':{'status':'accepted'}})
        before=self.record['scope_version']
        self.event(data={'scope':{'process':'SIMULASI changed','problem':'changed','data_scope':'other'},
            'change_record':{'reason':'SIMULASI perubahan scope','source_ref':'SIMULASI keputusan','recorded_by':'SIMULASI tim'}})
        self.assertEqual(self.record['scope_version'],before+1)
        self.assertNotIn('approvals',self.record['data']);self.assertNotIn('pilot_result',self.record['data'])

    def test_full_lifecycle_has_actual_gates_and_zero_usage_is_not_success(self):
        self.event(data=self.initial_data())
        while self.record['stage']!='proposal':self.event('advance')
        with self.assertRaises(ValueError):self.event('advance')
        self.event(data={'approvals':self.approvals(['commercial'])});self.event('advance')
        with self.assertRaises(ValueError):self.event('advance')
        self.event(data={'approvals':self.approvals(['commercial','pilot'])});self.event('advance')
        with self.assertRaises(ValueError):self.event('advance')
        self.event(data={'pilot_result':{'status':'accepted','metrics_ref':'SIMULASI log','evaluator':'SIMULASI lead','measured_period':'SIMULASI 2 minggu',
                         'agent_validation':result_fixture(self.record['data']['agent_contract'])},
                         'approvals':self.approvals(['commercial','pilot','go_live'])});self.event('advance')
        with self.assertRaises(ValueError):self.event('advance')
        self.event(data={'go_live_receipt':{'status':'confirmed','source_ref':'SIMULASI deployment log','timestamp':'SIMULASI date'},
                         'adoption_owner':'SIMULASI lead','operating_guide_ref':'SIMULASI guide','support_plan_ref':'SIMULASI support'});self.event('advance')
        self.event(data={'usage':{'metric':'pemakaian','value':0,'period':'SIMULASI 7 hari','source_ref':'SIMULASI log'},'outcome_comparison_ref':'SIMULASI baseline vs now'});self.event('advance')
        self.event(data={'evaluation':{'decision':'improve','reviewer':'SIMULASI team','source_ref':'SIMULASI retrospective','reason':'SIMULASI belum dipakai'},
                         'handover_ref':'SIMULASI handover','followup':{'owner':'SIMULASI lead','action':'SIMULASI periksa hambatan adopsi'}});self.event('advance')
        self.assertEqual(self.record['stage'],'closed');self.assertEqual(self.record['data']['evaluation']['decision'],'improve')

    def test_defer_resume_preserves_stage(self):
        self.event(data={'defer_reason':'SIMULASI menunggu baseline'});self.event('defer')
        self.assertEqual(self.record['stage'],'deferred')
        with self.assertRaises(ValueError):self.event('defer')
        self.event('resume');self.assertEqual(self.record['stage'],'lead')

    def test_approval_cannot_cross_tenant_or_scope(self):
        self.event(data=self.initial_data())
        while self.record['stage']!='proposal':self.event('advance')
        approvals=self.approvals(['commercial'])
        approvals['commercial']['client']['tenant_id']='OTHER'
        self.event(data={'approvals':approvals})
        with self.assertRaises(ValueError):self.event('advance')

    def test_changed_diagnosis_invalidates_old_approvals(self):
        self.event(data=self.initial_data())
        self.event(data={'approvals':self.approvals(['pilot'])})
        self.event(data={'diagnosis':{'selected_cause':'SIMULASI new','evidence_ref':'SIMULASI new observation'},
            'change_record':{'reason':'SIMULASI koreksi','source_ref':'SIMULASI observasi','recorded_by':'SIMULASI tim'}})
        self.assertNotIn('approvals',self.record['data']);self.assertNotIn('assessment_payload',self.record['data'])

    def test_bank_revision_change_requires_fresh_approval(self):
        self.event(data=self.initial_data())
        while self.record['stage']!='proposal':self.event('advance')
        approvals=self.approvals(['commercial'])
        approvals['commercial']['team']['bank_revision']='old'
        self.event(data={'approvals':approvals})
        with self.assertRaises(ValueError):self.event('advance')


if __name__=='__main__':unittest.main(verbosity=2)
