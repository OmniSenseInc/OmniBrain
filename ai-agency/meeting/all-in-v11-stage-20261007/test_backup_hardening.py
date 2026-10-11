"""Synthetic snapshots only; no production files or network access."""
import concurrent.futures,gzip,hashlib,io,json,os,sqlite3,tarfile,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from cryptography.fernet import Fernet,InvalidToken
import omnisense_ops as ops

class BackupHardeningTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='backup-test-',dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name).resolve()
        sources={}
        for name in ops.SOURCES:
            p=self.root/name
            if name.endswith('.sqlite3'):
                db=sqlite3.connect(p)
                try:
                    db.execute('CREATE TABLE synthetic(value TEXT)')
                    db.execute('INSERT INTO synthetic VALUES(?)',('synthetic-client-only',))
                    db.commit()
                finally:db.close()
            else:p.write_bytes(b'x'*32)
            sources[name]=p
        self.f=Fernet(Fernet.generate_key())
        for name,value in [('STATE',self.root/'state'),('BACKUPS',self.root/'backups'),('SOURCES',sources)]:
            p=patch.object(ops,name,value);p.start();self.addCleanup(p.stop)
        ops.STATE.mkdir();ops.BACKUPS.mkdir()
        p=patch.object(ops,'cipher',return_value=self.f);p.start();self.addCleanup(p.stop)

    def bytes_by_name(self):return {n:p.read_bytes() for n,p in ops.SOURCES.items()}

    def archive(self,contents=None,manifest=None,extras=()):
        contents=self.bytes_by_name() if contents is None else contents
        if manifest is None:manifest={'version':1,'sha256':{n:hashlib.sha256(b).hexdigest() for n,b in contents.items()}}
        out=io.BytesIO()
        with tarfile.open(fileobj=out,mode='w:gz') as tar:
            for name,b in [*contents.items(),('manifest.json',json.dumps(manifest).encode()),*extras]:
                member=tarfile.TarInfo(name);member.size=len(b);tar.addfile(member,io.BytesIO(b))
        p=self.root/'test.fernet';p.write_bytes(self.f.encrypt(out.getvalue()));return p

    def test_snapshot_streamed_to_disk_and_authenticated_restore(self):
        # Whole SQLite files must not be accumulated by Path.read_bytes().
        with patch.object(Path,'read_bytes',side_effect=AssertionError('Unbounded file read')):
            report=ops.backup()
        self.assertEqual(len(report['verification']['database_checks']),4)
        self.assertFalse(report['offsite_configured'])
        self.assertNotIn(b'synthetic-client-only',(ops.BACKUPS/report['file']).read_bytes())

    def test_same_second_snapshots_never_replace_previous_snapshot(self):
        with patch.object(ops.time,'strftime',return_value='20261007T000000Z'):
            a=ops.backup();b=ops.backup()
        self.assertNotEqual(a['file'],b['file'])
        self.assertEqual(len(list(ops.BACKUPS.glob('snapshot-*.fernet'))),2)
        self.assertTrue((ops.BACKUPS/a['file']).exists())

    def test_stale_pending_marker_does_not_block_atomic_write(self):
        p=ops.STATE/'status.json';stale=p.with_suffix('.json.pending');stale.write_bytes(b'stale')
        ops.atomic(p,b'new');self.assertEqual(p.read_bytes(),b'new')
        self.assertEqual(stale.read_bytes(),b'stale')

    def test_atomic_failure_removes_its_unique_pending_file(self):
        p=ops.STATE/'status.json';p.write_bytes(b'previous')
        with patch.object(ops.os,'replace',side_effect=OSError('synthetic failure')):
            with self.assertRaises(OSError):ops.atomic(p,b'new')
        self.assertEqual(p.read_bytes(),b'previous')
        self.assertEqual(list(ops.STATE.glob('.*.pending')),[])

    @unittest.skipUnless(os.name=='posix','Production atomic concurrency uses POSIX rename; verify on Linux')
    def test_concurrent_atomic_writers_only_publish_complete_payloads(self):
        p=ops.STATE/'status.json';values=[str(i).encode()*1000 for i in range(20)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda b:ops.atomic(p,b),values))
        self.assertIn(p.read_bytes(),values)
        self.assertEqual(list(ops.STATE.glob('.*.pending')),[])

    def test_overlapping_backup_rejected_and_lock_released(self):
        with ops._backup_lock():
            with self.assertRaises(OSError):ops.backup()
        self.assertTrue(ops.backup()['verification']['authenticated_decrypt'])

    def test_retention_keeps_seven_and_latest_report_points_to_retained_file(self):
        for _ in range(9):latest=ops.backup()
        self.assertEqual(len(list(ops.BACKUPS.glob('snapshot-*.fernet'))),7)
        self.assertTrue((ops.BACKUPS/latest['file']).exists())
        self.assertEqual(json.loads((ops.STATE/'last-backup.json').read_text())['file'],latest['file'])

    def test_failed_verification_keeps_previous_good_snapshot_and_report(self):
        previous=ops.backup();report=(ops.STATE/'last-backup.json').read_bytes()
        with patch.object(ops,'restore_test',side_effect=ValueError('synthetic invalid snapshot')):
            with self.assertRaises(ValueError):ops.backup()
        self.assertEqual((ops.STATE/'last-backup.json').read_bytes(),report)
        self.assertEqual([p.name for p in ops.BACKUPS.glob('snapshot-*.fernet')],[previous['file']])

    def test_ciphertext_file_size_is_bounded_before_decrypt(self):
        p=self.root/'oversized.fernet';p.write_bytes(b'x'*1025)
        with patch.object(ops,'_ciphertext_cap',return_value=1024),patch.object(self.f,'decrypt',side_effect=AssertionError('Must not decrypt oversized input')):
            with self.assertRaises(ValueError):ops.restore_test(p)

    def test_tampered_and_wrong_key_tokens_rejected(self):
        p=self.archive();good=p.read_bytes();bad=bytearray(good);bad[len(bad)//2]^=1;p.write_bytes(bad)
        with self.assertRaises(InvalidToken):ops.restore_test(p)
        p.write_bytes(good)
        with patch.object(ops,'cipher',return_value=Fernet(Fernet.generate_key())):
            with self.assertRaises(InvalidToken):ops.restore_test(p)

    def test_duplicate_tar_member_rejected(self):
        p=self.archive(extras=[('web-rate-key',b'x'*32)])
        with self.assertRaises(ValueError):ops.restore_test(p)

    def test_unlisted_and_path_traversal_members_rejected(self):
        for name in ('../outside','/absolute','unexpected'):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):ops.restore_test(self.archive(extras=[(name,b'x')]))

    def test_missing_member_rejected(self):
        contents=self.bytes_by_name();contents.pop('wa-rate-key')
        with self.assertRaises(ValueError):ops.restore_test(self.archive(contents))

    def test_manifest_hash_and_version_fail_closed(self):
        for manifest in ({'version':1,'sha256':{}},{'version':2,'sha256':{}},[],{'version':1,'sha256':{n:'0'*64 for n in ops.SOURCES}}):
            with self.subTest(manifest=manifest):
                with self.assertRaises(ValueError):ops.restore_test(self.archive(manifest=manifest))

    def test_manifest_size_rejected(self):
        p=self.archive(manifest={'version':1,'sha256':{},'padding':'x'*70000})
        with self.assertRaises(ValueError):ops.restore_test(p)

    def test_invalid_rate_seed_not_published(self):
        ops.SOURCES['web-rate-key'].write_bytes(b'x'*33)
        with self.assertRaises(ValueError):ops.backup()
        self.assertEqual(list(ops.BACKUPS.glob('snapshot-*.fernet')),[])

    def test_total_member_size_bounded_even_when_gzip_compresses_well(self):
        p=self.archive()
        with patch.object(ops,'MAX_BYTES',8192):
            with self.assertRaises(ValueError):ops.restore_test(p)

    def test_oversized_member_rejected_before_extraction(self):
        p=self.archive()
        with patch.object(ops,'MAX_MEMBER_BYTES',4096):
            with self.assertRaises(ValueError):ops.restore_test(p)

    def test_invalid_sqlite_file_rejected(self):
        contents=self.bytes_by_name();contents['consultations.sqlite3']=b'not a sqlite database'
        with self.assertRaises(sqlite3.DatabaseError):ops.restore_test(self.archive(contents))

    def test_gzip_bomb_hidden_after_tar_terminator_is_bounded(self):
        p=self.archive();plain=gzip.decompress(self.f.decrypt(p.read_bytes()))
        p.write_bytes(self.f.encrypt(gzip.compress(plain+b'\0'*(2*1024*1024))))
        with patch.object(ops,'MAX_BYTES',65536):
            with self.assertRaises(ValueError):ops.restore_test(p)

    def test_wal_growth_cannot_bypass_snapshot_database_cap(self):
        p=ops.SOURCES['consultations.sqlite3'];db=sqlite3.connect(p)
        try:
            db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA wal_autocheckpoint=0')
            db.execute('INSERT INTO synthetic VALUES(?)',('x'*100000,));db.commit()
            self.assertLess(p.stat().st_size,16384)
            with patch.object(ops,'MAX_MEMBER_BYTES',16384):
                with self.assertRaises(ValueError):ops.backup()
        finally:db.close()
        self.assertEqual(list(ops.BACKUPS.glob('snapshot-*.fernet')),[])

    def health(self,result='success',timer=0,now=None):
        with patch.object(ops.subprocess,'check_output',return_value=result),patch.object(ops.subprocess,'run',return_value=type('Result',(),{'returncode':timer})()):
            return ops.backup_health(now)

    def test_backup_worker_failure_visible_before_old_snapshot_stales(self):
        ops.backup();metrics,issues=self.health(result='exit-code')
        self.assertIn('backup_worker_failed',issues);self.assertNotIn('backup_stale',issues)
        self.assertEqual(metrics['worker_result'],'exit-code')

    def test_backup_timer_inactive_visible(self):
        ops.backup();self.assertIn('backup_timer_inactive',self.health(timer=1)[1])

    def test_missing_latest_snapshot_visible(self):
        r=ops.backup();(ops.BACKUPS/r['file']).unlink()
        self.assertIn('backup_snapshot_unavailable',self.health()[1])

    def test_stale_backup_visible(self):
        r=ops.backup();self.assertIn('backup_stale',self.health(now=r['created']+30*3600+1)[1])

    def test_healthy_backup_has_no_false_alarm(self):
        ops.backup();self.assertEqual(self.health()[1],[])

    def test_aggregate_source_cap_rejected_before_snapshot_work(self):
        with patch.object(ops,'MAX_BYTES',8192),patch.object(ops.sqlite3,'connect',side_effect=AssertionError('Early cap must reject before opening SQLite')):
            with self.assertRaises(ValueError):ops.backup()

    def test_restore_rejects_symlink_tar_member(self):
        contents=self.bytes_by_name();out=io.BytesIO()
        with tarfile.open(fileobj=out,mode='w:gz') as tar:
            m=tarfile.TarInfo('consultations.sqlite3');m.type=tarfile.SYMTYPE;m.linkname='../outside';tar.addfile(m)
        p=self.root/'link.fernet';p.write_bytes(self.f.encrypt(out.getvalue()))
        with self.assertRaises(ValueError):ops.restore_test(p)

if __name__=='__main__':unittest.main()
