import sqlite3,tempfile,unittest
from pathlib import Path
from omnisense_ops import review_health

class HealthTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=Path(__file__).parent);self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  c=sqlite3.connect(self.root/'consultations.sqlite3');c.execute('CREATE TABLE review_sync_jobs(ticket TEXT,status TEXT,updated REAL,attempts INTEGER)');c.commit();c.close()
 def insert(self,status,age,attempts):
  c=sqlite3.connect(self.root/'consultations.sqlite3');c.execute('INSERT INTO review_sync_jobs VALUES(?,?,?,?)',('synthetic-id',status,1000-age,attempts));c.commit();c.close()
 def test_empty_queue_healthy(self):self.assertEqual(review_health(self.root,1000),({'pending':0,'seconds_since_oldest_update':0,'retrying':0,'max_attempts':0},[]))
 def test_recent_queue_is_not_false_alarm(self):
  self.insert('pending',60,0);m,i=review_health(self.root,1000);self.assertEqual(m['pending'],1);self.assertEqual(i,[])
 def test_stale_retry_is_visible_without_case_content(self):
  self.insert('pending',601,2);m,i=review_health(self.root,1000);self.assertIn('review_sync_backlog',i);self.assertEqual(m['retrying'],1);self.assertNotIn('synthetic-id',str(m))
 def test_done_job_not_counted(self):
  self.insert('done',9000,5);self.assertEqual(review_health(self.root,1000)[0]['pending'],0)
 def test_clock_shift_does_not_create_negative_age(self):
  self.insert('pending',-30,0);self.assertEqual(review_health(self.root,1000)[0]['seconds_since_oldest_update'],0)
 def test_repeated_failure_not_hidden_by_fresh_retry_timestamp(self):
  self.insert('pending',10,3);self.assertIn('review_sync_repeated_failures',review_health(self.root,1000)[1])

if __name__=='__main__':unittest.main()
