import tempfile,sqlite3,unittest
from pathlib import Path
from unittest.mock import patch
from cryptography.fernet import Fernet,InvalidToken
import omnisense_ops as ops

class BackupTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);r=Path(self.tmp.name)
  sources={}
  for name in ops.SOURCES:
   p=r/name
   if name.endswith('.sqlite3'):
    c=sqlite3.connect(p);c.execute('CREATE TABLE synthetic(value TEXT)');c.execute('INSERT INTO synthetic VALUES(?)',('fake-client-only',));c.commit();c.close()
   else:p.write_bytes(b'x'*32)
   sources[name]=p
  key=r/'backup.key';key.write_bytes(Fernet.generate_key());key.chmod(0o600)
  for name,value in [('STATE',r/'state'),('BACKUPS',r/'backups'),('KEY',key),('SOURCES',sources)]:
   q=patch.object(ops,name,value);q.start();self.addCleanup(q.stop)
 def test_snapshot_authenticated_restore_and_no_plaintext_in_archive(self):
  report=ops.backup();p=ops.BACKUPS/report['file']
  self.assertNotIn(b'fake-client-only',p.read_bytes());self.assertTrue(report['verification']['authenticated_decrypt']);self.assertEqual(len(report['verification']['database_checks']),4)
  self.assertFalse(report['offsite_configured']);self.assertEqual(p.stat().st_mode&0o777,0o600)
 def test_corrupt_ciphertext_and_wrong_key_rejected(self):
  report=ops.backup();p=ops.BACKUPS/report['file'];good=p.read_bytes();bad=bytearray(good);bad[len(bad)//2]^=1;p.write_bytes(bad)
  with self.assertRaises(InvalidToken):ops.restore_test(p)
  p.write_bytes(good);ops.KEY.write_bytes(Fernet.generate_key())
  with self.assertRaises(InvalidToken):ops.restore_test(p)

if __name__=='__main__':unittest.main()
