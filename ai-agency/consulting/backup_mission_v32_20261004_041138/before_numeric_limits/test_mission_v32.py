import copy
import hashlib
import unittest
from pathlib import Path
import test_decision_workflow_v31 as previous
from agent_contract import validate_contract, validate_results, contract_hash
from fixtures_agent import agent_fixture, result_fixture
from workflow_agency import read_case, approval


class AgentContractTests(unittest.TestCase):
    def setUp(self):
        self.c=agent_fixture();self.r=result_fixture(self.c)
    def plan(self):
        return validate_contract(self.c,self.c['process'],self.c['owner'])
    def result(self):
        return validate_results(self.c,self.r,self.c['process'],self.c['owner'])
    def test_valid_plan_and_results_do_not_execute_or_authorize_runtime(self):
        self.assertFalse(self.plan()['runtime_authorized'])
        self.assertTrue(self.result()['documented_results_meet_contract'])
        self.assertFalse(self.result()['runtime_authorized'])
    def test_missing_contract_rejected(self):
        with self.assertRaises(ValueError):validate_contract(None,'p','owner')
    def test_wrong_owner_or_process_rejected(self):
        for process,owner in [('other',self.c['owner']),(self.c['process'],'other')]:
            with self.assertRaises(ValueError):validate_contract(self.c,process,owner)
    def test_changed_baseline_rejected(self):
        with self.assertRaises(ValueError):validate_contract(self.c,self.c['process'],self.c['owner'],{'value':99})
    def test_claimed_baseline_hash_cannot_mask_different_metric_baseline(self):
        self.c['metrics'][0]['baseline']['value']=120
        with self.assertRaises(ValueError):validate_contract(self.c,self.c['process'],self.c['owner'],previous.FIXTURE['context']['baseline'])
    def test_production_pilot_rejected(self):
        self.c['pilot_environment']='production'
        with self.assertRaises(ValueError):self.plan()
    def test_autonomous_action_requires_effect_authorization_and_idempotency(self):
        a=self.c['actions'][0];a['mode']='execute_bounded'
        with self.assertRaises(ValueError):self.plan()
        a.update(effect_limit='SIMULASI satu tiket sendiri',authorization_ref='SIMULASI keputusan',idempotency_ref='SIMULASI job key')
        self.plan()
        a['requires_human']=True
        with self.assertRaises(ValueError):self.plan()
    def test_missing_exception_path_rejected(self):
        self.c['exceptions']=self.c['exceptions'][1:]
        with self.assertRaises(ValueError):self.plan()
    def test_missing_adversarial_scenario_rejected(self):
        self.c['evaluation_suite']=[x for x in self.c['evaluation_suite'] if x['category']!='prompt_injection']
        with self.assertRaises(ValueError):self.plan()
    def test_critical_scenario_cannot_be_nonblocking(self):
        next(x for x in self.c['evaluation_suite'] if x['category']=='tool_failure')['blocking']=False
        with self.assertRaises(ValueError):self.plan()
    def test_duplicate_ids_rejected(self):
        self.c['evaluation_suite'].append(copy.deepcopy(self.c['evaluation_suite'][0]))
        with self.assertRaises(ValueError):self.plan()
    def test_metrics_require_outcome_and_quality_guardrail(self):
        self.c['metrics']=self.c['metrics'][:1]
        with self.assertRaises(ValueError):self.plan()
    def test_invalid_numeric_target_rejected(self):
        for bad in [True,float('nan'),float('inf')]:
            self.c['metrics'][0]['target']=bad
            with self.assertRaises(ValueError):self.plan()
    def test_results_from_old_contract_rejected(self):
        self.c['objective']='SIMULASI tujuan berubah'
        with self.assertRaises(ValueError):self.result()
    def test_passed_flag_without_trace_rejected(self):
        self.r['scenarios'][0].pop('trace_ref')
        with self.assertRaises(ValueError):self.result()
    def test_missing_scenario_or_extra_scenario_rejected(self):
        self.r['scenarios'].pop()
        with self.assertRaises(ValueError):self.result()
    def test_critical_failure_blocks_even_when_metrics_pass(self):
        self.r['scenarios'][0]['passed']=False
        with self.assertRaises(ValueError):self.result()
    def test_metric_threshold_blocks_even_when_all_scenarios_pass(self):
        self.r['metrics'][1]['value']=90
        with self.assertRaises(ValueError):self.result()
    def test_unit_period_and_sample_count_must_be_explicit(self):
        for key,value in [('unit','jam'),('period','other')]:
            r=copy.deepcopy(self.r);r['metrics'][0][key]=value
            with self.assertRaises(ValueError):validate_results(self.c,r,self.c['process'],self.c['owner'])
        self.r['sample_count']=True
        with self.assertRaises(ValueError):self.result()


class LedgerMissionTests(unittest.TestCase):
    def setUp(self):
        self.h=previous.LedgerTests();self.h.setUp()
    def tearDown(self):self.h.tearDown()
    def initialized(self):self.h.event(data=self.h.initial_data())
    def pilot(self,ai=True):
        data=self.h.initial_data()
        if not ai:
            data['assessment_payload']['use_case']['solution_type']='rule_automation';data.pop('agent_contract')
        self.h.event(data=data)
        while self.h.record['stage']!='proposal':self.h.event('advance')
        self.h.event(data={'approvals':self.h.approvals(['commercial','pilot'])});self.h.event('advance')
        self.h.event('advance')
    def result_data(self):
        return {'pilot_result':{'status':'accepted','metrics_ref':'SIMULASI result','evaluator':'SIMULASI lead',
            'measured_period':'SIMULASI 2 minggu','agent_validation':result_fixture(self.h.record['data']['agent_contract'],self.h.record['scope_version'])},
            'approvals':self.h.approvals(['commercial','pilot','go_live'])}
    def test_ai_pilot_needs_contract_but_not_results_before_start(self):
        self.pilot();self.assertEqual(self.h.record['stage'],'pilot')
        self.assertNotIn('pilot_result',self.h.record['data'])
    def test_claim_of_accepted_pilot_without_scenarios_cannot_enter_delivery(self):
        self.pilot();d=self.result_data();d['pilot_result'].pop('agent_validation')
        self.h.event(data=d)
        with self.assertRaises(ValueError):self.h.event('advance')
    def test_failed_scenario_prevents_delivery(self):
        self.pilot();d=self.result_data();d['pilot_result']['agent_validation']['scenarios'][0]['passed']=False
        self.h.event(data=d)
        with self.assertRaises(ValueError):self.h.event('advance')
    def test_valid_results_enter_delivery(self):
        self.pilot();self.h.event(data=self.result_data());self.h.event('advance')
        self.assertEqual(self.h.record['stage'],'delivery')
    def test_results_from_other_case_or_revision_rejected(self):
        self.pilot();d=self.result_data();d['pilot_result']['agent_validation']['case_id']='OTHER'
        self.h.event(data=d)
        with self.assertRaises(ValueError):self.h.event('advance')
    def test_non_ai_pilot_does_not_require_agent_contract(self):
        self.pilot(False);self.assertEqual(self.h.record['stage'],'pilot')
    def test_owner_change_clears_old_approvals_and_is_recorded(self):
        self.pilot()
        with self.assertRaises(ValueError):self.h.event(data={'technical_owner':'SIMULASI replacement'})
        self.h.event(data={'technical_owner':'SIMULASI replacement','change_record':{
            'reason':'SIMULASI handover','source_ref':'SIMULASI decision','recorded_by':'SIMULASI team'}})
        self.assertEqual(self.h.record['stage'],'discovery');self.assertNotIn('approvals',self.h.record['data'])
    def test_floating_revision_and_boolean_scope_approval_rejected(self):
        self.initialized()
        with self.assertRaises(ValueError):previous.apply_event(self.h.db,'SIMULASI_A','CASE1',{
            'id':'float','expected_revision':1.0,'action':'update'},self.h.actor,previous.BANK,True)
        a=self.h.approvals(['pilot']);a['pilot']['team']['scope_version']=True
        record=copy.deepcopy(self.h.record);record['data']['approvals']=a
        self.assertFalse(approval(record,'pilot','team',previous.BANK))
    def test_operator_cannot_forge_derived_route_or_contract_check(self):
        for field in ['assessment_result','agent_contract_check']:
            with self.assertRaises(ValueError):self.h.event(data={field:{'passed':True,'route':'rancang_pilot_ai'}})
    def test_read_missing_db_creates_nothing(self):
        self.assertFalse(read_case(self.h.db,'SIMULASI_A','CASE1',self.h.actor)['found'])
        self.assertFalse(self.h.db.exists())
    def test_read_is_case_specific_and_does_not_modify_database(self):
        self.initialized();before=hashlib.sha256(self.h.db.read_bytes()).hexdigest()
        r=read_case(self.h.db,'SIMULASI_A','CASE1',self.h.actor)
        self.assertTrue(r['found']);self.assertEqual(r['context']['baseline']['value'],12)
        self.assertFalse(read_case(self.h.db,'OTHER','CASE1',self.h.actor)['found'])
        self.assertEqual(before,hashlib.sha256(self.h.db.read_bytes()).hexdigest())
        with self.assertRaises(ValueError):read_case(self.h.db,'SIMULASI_A','CASE1',{'id':'fake','role':'client'})
    def test_source_of_baseline_correction_survives_resume(self):
        self.initialized();data=copy.deepcopy(self.h.record['data'])
        data['baseline']['value']=5
        self.h.event(data={'baseline':data['baseline'],'change_record':{
            'reason':'SIMULASI waktu aktif berbeda dari total','source_ref':'SIMULASI catatan operator','recorded_by':'SIMULASI team'}})
        r=read_case(self.h.db,'SIMULASI_A','CASE1',self.h.actor)
        self.assertEqual(r['context']['baseline']['value'],5)
        self.assertIn('waktu aktif',r['context']['change_record']['reason'])

    def test_material_correction_does_not_reuse_old_handoff_or_next_step(self):
        self.initialized();self.h.event(data={'next_step':'SIMULASI deploy','open_questions':['SIMULASI old']})
        baseline=copy.deepcopy(self.h.record['data']['baseline']);baseline['value']=2
        self.h.event(data={'baseline':baseline,'change_record':{
            'reason':'SIMULASI koreksi baseline','source_ref':'SIMULASI log','recorded_by':'SIMULASI team'}})
        for key in ['handoff','next_step','open_questions']:
            self.assertNotIn(key,self.h.record['data'])


if __name__=='__main__':unittest.main(verbosity=2)
