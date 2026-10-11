import copy
import unittest
from pathlib import Path
from assessment_v3 import load_bank, assess, roi


class AssessmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = load_bank(Path(__file__).with_name('pertanyaan_v3.json'))

    def payload(self, mode='screening', value=5, evidence='self_reported'):
        p = {'version': '3.0', 'mode': mode,
                'answers': {q['id']: {'value': value, 'evidence': evidence, 'source': 'simulasi: log 7 hari'}
                            for q in self.bank[mode]},
                'context': {'process': 'Ringkasan tiket', 'problem': 'Pencarian lama', 'process_owner': 'Lead support',
                            'baseline': {'metric': 'durasi per tiket', 'value': 12, 'unit': 'menit/tiket',
                                         'period': '7 hari', 'source': 'simulasi: sampel 30 tiket'},
                            'access_permission': 'confirmed', 'impact': 'low', 'human_review': 'defined', 'fallback': 'defined'}}
        if evidence != 'self_reported':
            for a in p['answers'].values():
                a['review_record'] = {'reviewer':'SIMULASI A','reviewed_at':'2026-10-04','source_ref':a['source'],'scope':'SIMULASI tiket','finding':'supports'}
        return p

    def test_all_unknown_is_not_low_or_neutral(self):
        r = assess(self.payload(value=None), self.bank)
        self.assertIsNone(r['score']); self.assertIsNone(r['band'])
        self.assertEqual(r['range'], [20, 100]); self.assertEqual(r['answer_coverage_percent'], 0)

    def test_self_report_does_not_authorize_pilot(self):
        r = assess(self.payload(), self.bank)
        self.assertEqual(r['score'], 100); self.assertEqual(r['verified_evidence_coverage_percent'], 0)
        self.assertEqual(r['route'], 'discovery_dan_verifikasi'); self.assertFalse(r['deployment_approved'])

    def test_critical_weakness_overrides_high_aggregate_recommendation(self):
        p = self.payload(evidence='reviewed')
        critical = next(q['id'] for q in self.bank['screening'] if q['critical'])
        p['answers'][critical]['value'] = 1
        r = assess(p, self.bank)
        self.assertGreaterEqual(r['score'], 80)
        self.assertEqual(r['route'], 'perkuat_fondasi'); self.assertIn(critical, r['critical_weak'])

    def test_partial_coverage_keeps_full_weight_denominator(self):
        p = self.payload(value=None)
        q = self.bank['screening'][0]; p['answers'][q['id']]['value'] = 5
        weight = next(d['weight'] for d in self.bank['dimensions'] if d['id'] == q['dimension']) / 2
        r = assess(p, self.bank)
        self.assertIsNone(r['score']); self.assertEqual(r['range'], [round(20 + 80 * weight, 1), 100])
        self.assertEqual(r['answer_coverage_percent'], round(100 * weight, 1))

    def test_denied_access_blocks_even_full_score(self):
        p = self.payload(evidence='reviewed'); p['context']['access_permission'] = 'denied'
        self.assertEqual(assess(p, self.bank)['route'], 'hentikan_akses_data')

    def test_verified_complete_only_designs_pilot(self):
        for mode in ('screening', 'discovery'):
            p = self.payload(mode=mode, evidence='observed')
            r = assess(p, self.bank)
            self.assertEqual(r['route'], 'pilih_dan_uji_kelayakan_solusi')
            import json
            p['use_case'] = json.loads(Path(__file__).with_name('input_contoh_discovery_reviewed.json').read_text())['use_case']
            r=assess(p,self.bank)
            self.assertEqual(r['route'], 'rancang_pilot_ai'); self.assertFalse(r['deployment_approved'])

    def test_high_impact_needs_expert_review(self):
        p = self.payload(evidence='reviewed'); p['context']['impact'] = 'high'
        r = assess(p, self.bank)
        self.assertIn('expert_review_required', r['context_gaps'])
        self.assertEqual(r['route'], 'discovery_dan_verifikasi')

    def test_invalid_or_unsubstantiated_inputs_rejected(self):
        qid = self.bank['screening'][0]['id']
        for v in (True, 0, 6, 2.5, '5', float('nan')):
            p = self.payload(); p['answers'][qid]['value'] = v
            with self.assertRaises(ValueError): assess(p, self.bank)
        p = self.payload(evidence='reviewed'); p['answers'][qid]['source'] = ''
        with self.assertRaises(ValueError): assess(p, self.bank)
        p = self.payload(); p['version'] = '2.0'
        with self.assertRaises(ValueError): assess(p, self.bank)
        p = self.payload(); p['answers']['not-a-question'] = {'value': 5}
        with self.assertRaises(ValueError): assess(p, self.bank)

    def test_baseline_requires_unit_period_and_source(self):
        p = self.payload(evidence='reviewed'); del p['context']['baseline']['unit']
        self.assertIn('baseline', assess(p, self.bank)['context_gaps'])

    def test_capacity_is_not_cash(self):
        p = dict(monthly_volume=1000, minutes_before=10, minutes_after_including_review=6,
                 adoption_fraction=0.8, loaded_hourly_cost=60000, cash_realization_fraction=0,
                 monthly_operating_cost=500000, implementation_cost=5000000)
        r = roi(p)
        self.assertEqual(r['capacity_hours_per_month'], 53.33)
        self.assertEqual(r['capacity_value_per_month'], 3200000)
        self.assertEqual(r['net_cash_per_month'], -500000); self.assertIsNone(r['payback_months'])
        p['cash_realization_fraction'] = 0.5
        r = roi(p); self.assertEqual(r['net_cash_per_month'], 1100000); self.assertEqual(r['payback_months'], 4.55)

    def test_worse_workflow_is_negative_not_clamped(self):
        p = dict(monthly_volume=60, minutes_before=1, minutes_after_including_review=2,
                 adoption_fraction=1, loaded_hourly_cost=100, cash_realization_fraction=1,
                 monthly_operating_cost=0, implementation_cost=0)
        r = roi(p); self.assertEqual(r['capacity_hours_per_month'], -1); self.assertIsNone(r['payback_months'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
