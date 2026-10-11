import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'handoff-v9'))
from workflow_agency import transition

class ResumeHoldTests(unittest.TestCase):
 def record(self,target):return {'stage':'deferred','resume_stage':target,'revision':2,'scope_version':1,'data':{'client_update_review':{'pending':True,'fingerprint':'current','source_ref':'client'}}}
 def test_pending_correction_cannot_resume_delivery(self):
  for target in ['diagnosis','options','proposal','onboarding','pilot','delivery','adoption']:
   with self.subTest(target=target),self.assertRaises(ValueError):transition(self.record(target),{'expected_revision':2,'action':'resume'},{'id':'operator','role':'operator'}, {})
 def test_discovery_resume_still_allows_review_work(self):
  r=transition(self.record('discovery'),{'expected_revision':2,'action':'resume'},{'id':'operator','role':'operator'}, {});self.assertEqual(r['stage'],'discovery')

if __name__=='__main__':unittest.main()
