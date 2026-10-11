"""Synthetic RSA/Fernet recovery fixtures; no live files, private records or messaging."""
import gzip,hashlib,io,json,os,sqlite3,stat,tarfile,tempfile,unittest,warnings,zipfile
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from cryptography.fernet import Fernet,InvalidToken
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.primitives.asymmetric import padding,rsa
import omnisense_ops as ops
import export_recovery as export
import verify_local_recovery as verify
ORIGINAL_READ_KEY=export.read_backup_key

class RecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.private=rsa.generate_private_key(public_exponent=65537,key_size=3072)

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='recovery-test-',dir=Path(__file__).parent);self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve();self.secret=Fernet.generate_key();self.fernet=Fernet(self.secret)
        self.sources={};self.contents={}
        for name in ops.SOURCES:
            p=self.root/name
            if name.endswith('.sqlite3'):
                db=sqlite3.connect(':memory:')
                try:
                    db.execute('CREATE TABLE synthetic(value TEXT)');db.execute("INSERT INTO synthetic VALUES('synthetic-only')");db.commit();data=db.serialize()
                finally:db.close()
            else:data=b'x'*32
            p.write_bytes(data);self.sources[name]=p;self.contents[name]=data
        self.key=self.root/'backup.key';self.key.write_bytes(self.secret)
        self.public=self.root/'owner.pem';self.public.write_bytes(self.private.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo))
        for n,v in [('STATE',self.root/'state'),('BACKUPS',self.root/'backups'),('KEY',self.key),('SOURCES',self.sources)]:
            q=patch.object(ops,n,v);q.start();self.addCleanup(q.stop)
        q=patch.object(ops,'cipher',return_value=self.fernet);q.start();self.addCleanup(q.stop)
        q=patch.object(export,'read_backup_key',return_value=self.secret);q.start();self.addCleanup(q.stop)
        self.backup=ops.backup();self.bundle=self.root/'recovery.zip'
        self.report=export.export_bundle(self.public,self.bundle)

    def expected_hash(self):return hashlib.sha256(self.bundle.read_bytes()).hexdigest()
    def verify(self):return verify.verify_bundle(self.private,self.bundle,self.expected_hash())

    def archive(self,contents=None,extras=(),manifest=None):
        contents=self.contents if contents is None else contents
        if manifest is None:manifest={'version':1,'sha256':{n:hashlib.sha256(b).hexdigest() for n,b in contents.items()}}
        out=io.BytesIO()
        with tarfile.open(fileobj=out,mode='w:gz') as tar:
            for name,b in [*contents.items(),('manifest.json',json.dumps(manifest).encode()),*extras]:
                m=tarfile.TarInfo(name);m.size=len(b);tar.addfile(m,io.BytesIO(b))
        return out.getvalue()

    def rewrite(self,transform=lambda members:members,compression=zipfile.ZIP_STORED):
        with zipfile.ZipFile(self.bundle) as z:members=[(m.filename,z.read(m)) for m in z.infolist()]
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',UserWarning)
            with zipfile.ZipFile(self.bundle,'w',compression) as z:
                for name,data in transform(members):z.writestr(name,data)

    def set_payload(self,plain):
        payload=self.fernet.encrypt(plain)
        def transform(members):
            result=[]
            for name,data in members:
                if name==self.backup['file']:data=payload
                elif name=='manifest.json':
                    meta=json.loads(data);meta['snapshot_sha256']=hashlib.sha256(payload).hexdigest();meta['snapshot_bytes']=len(payload);data=json.dumps(meta).encode()
                result.append((name,data))
            return result
        self.rewrite(transform)

    def change_meta(self,change):
        def transform(members):
            result=[]
            for name,data in members:
                if name=='manifest.json':meta=json.loads(data);change(meta);data=json.dumps(meta).encode()
                result.append((name,data))
            return result
        self.rewrite(transform)

    def test_real_export_and_inmemory_verification_four_databases(self):
        result=self.verify()
        self.assertEqual(result['databases_verified'],4);self.assertTrue(result['authenticated_decrypt'])
        self.assertFalse(result['plaintext_database_files_written'])
        self.assertEqual(self.report['bundle_sha256'],self.expected_hash())
        data=self.bundle.read_bytes();self.assertNotIn(self.secret,data);self.assertNotIn(b'synthetic-only',data)

    def test_verification_database_checks_only_use_memory_connections(self):
        original=sqlite3.connect;targets=[]
        def connect(target,*args,**kwargs):targets.append(target);return original(target,*args,**kwargs)
        with patch.object(verify.sqlite3,'connect',side_effect=connect):self.verify()
        self.assertEqual(targets,[':memory:']*4)

    def test_key_reader_checks_opened_file_owner_mode_type_and_size(self):
        for uid,mode,size in ((1000,stat.S_IFREG|0o600,44),(0,stat.S_IFREG|0o644,44),(0,stat.S_IFDIR|0o700,44),(0,stat.S_IFREG|0o600,10000)):
            with self.subTest(uid=uid,mode=mode,size=size),patch.object(export.os,'fstat',return_value=SimpleNamespace(st_uid=uid,st_mode=mode,st_size=size)):
                with self.assertRaises(PermissionError):ORIGINAL_READ_KEY(self.key)
        with patch.object(export.os,'fstat',return_value=SimpleNamespace(st_uid=0,st_mode=stat.S_IFREG|0o600,st_size=44)):
            self.assertEqual(ORIGINAL_READ_KEY(self.key),self.secret)

    def test_export_rejects_untrusted_snapshot_path_in_report(self):
        state=ops.STATE/'last-backup.json';metadata=json.loads(state.read_text());metadata['file']='../snapshot-20261007T000000Z.fernet';state.write_text(json.dumps(metadata))
        with self.assertRaises(ValueError):export.export_bundle(self.public,self.root/'new.zip')

    def test_export_does_not_overwrite_existing_bundle(self):
        original=self.bundle.read_bytes()
        with self.assertRaises(FileExistsError):export.export_bundle(self.public,self.bundle)
        self.assertEqual(self.bundle.read_bytes(),original);self.assertEqual(list(self.root.glob('.*.pending')),[])

    def test_export_rejects_tampered_existing_snapshot(self):
        snapshot=ops.BACKUPS/self.backup['file'];bad=bytearray(snapshot.read_bytes());bad[len(bad)//2]^=1;snapshot.write_bytes(bad)
        out=self.root/'new.zip'
        with self.assertRaises(InvalidToken):export.export_bundle(self.public,out)
        self.assertFalse(out.exists())

    def test_trusted_bundle_checksum_is_required_and_checked(self):
        for checksum in (None,'','bad','0'*64):
            with self.subTest(checksum=checksum):
                with self.assertRaises(ValueError):verify.verify_bundle(self.private,self.bundle,checksum)

    def test_bundle_size_rejected_before_checksum_or_zip_read(self):
        with patch.object(ops,'_ciphertext_cap',return_value=1),patch.object(verify,'MAX_METADATA',1),patch.object(verify,'MAX_WRAPPED_KEY',1),patch.object(verify,'digest_stream',side_effect=AssertionError('Must reject before reading bundle')):
            # Envelope allowance is 8192; append beyond it before validation.
            with self.bundle.open('ab') as f:f.write(b'x'*10000)
            with self.assertRaises(ValueError):self.verify()

    def test_zip_duplicate_member_rejected(self):
        self.rewrite(lambda m:[m[0],m[0],m[2]])
        with self.assertRaises(ValueError):self.verify()

    def test_zip_extra_member_rejected_before_loading_members(self):
        self.rewrite(lambda m:m+[('extra',b'x')])
        with self.assertRaises(ValueError):self.verify()

    def test_compressed_zip_not_accepted(self):
        self.rewrite(compression=zipfile.ZIP_DEFLATED)
        with self.assertRaises(ValueError):self.verify()

    def test_metadata_size_bounded_before_read(self):
        with patch.object(verify,'MAX_METADATA',1):
            with self.assertRaises(ValueError):self.verify()

    def test_duplicate_json_fields_rejected(self):
        self.rewrite(lambda m:[(n,b'{"version":1,"version":1}' if n=='manifest.json' else b) for n,b in m])
        with self.assertRaises(ValueError):self.verify()

    def test_metadata_public_key_fingerprint_must_match_private_key(self):
        self.change_meta(lambda m:m.update(public_key_sha256='0'*64))
        with self.assertRaises(ValueError):self.verify()

    def test_metadata_extra_fields_and_wrong_snapshot_size_rejected(self):
        self.change_meta(lambda m:m.update(snapshot_bytes=1))
        with self.assertRaises(ValueError):self.verify()

    def test_metadata_extra_fields_rejected(self):
        self.change_meta(lambda m:m.update(extra='unexpected'))
        with self.assertRaises(ValueError):self.verify()

    def test_wrapped_key_tampering_rejected(self):
        self.rewrite(lambda m:[(n,b'x'*384 if n=='backup-key.oaep' else b) for n,b in m])
        with self.assertRaises(ValueError):self.verify()

    def test_wrapped_key_wrong_length_rejected(self):
        self.rewrite(lambda m:[(n,b'x'*383 if n=='backup-key.oaep' else b) for n,b in m])
        with self.assertRaises(ValueError):self.verify()

    def test_authenticated_empty_archive_cannot_report_success(self):
        self.set_payload(self.archive(contents={}))
        with self.assertRaises(ValueError):self.verify()

    def test_tar_duplicate_members_rejected(self):
        self.set_payload(self.archive(extras=[('web-rate-key',b'x'*32)]))
        with self.assertRaises(ValueError):self.verify()

    def test_tar_traversal_members_rejected(self):
        self.set_payload(self.archive(extras=[('../outside',b'x')]))
        with self.assertRaises(ValueError):self.verify()

    def test_missing_database_rejected(self):
        contents=dict(self.contents);contents.pop('consultations.sqlite3');self.set_payload(self.archive(contents))
        with self.assertRaises(ValueError):self.verify()

    def test_rate_seed_size_rejected(self):
        contents=dict(self.contents);contents['web-rate-key']=b'x'*33;self.set_payload(self.archive(contents))
        with self.assertRaises(ValueError):self.verify()

    def test_tar_aggregate_member_cap_enforced(self):
        with patch.object(ops,'MAX_BYTES',8192):
            with self.assertRaises(ValueError):self.verify()

    def test_gzip_bomb_after_tar_terminator_rejected(self):
        raw=gzip.decompress(self.archive());self.set_payload(gzip.compress(raw+b'\0'*(2*1024*1024)))
        with patch.object(ops,'MAX_BYTES',65536):
            with self.assertRaises(ValueError):self.verify()

    def test_tar_manifest_hash_mismatch_rejected(self):
        self.set_payload(self.archive(manifest={'version':1,'sha256':{}}))
        with self.assertRaises(ValueError):self.verify()

    def test_invalid_sqlite_rejected_in_memory(self):
        contents=dict(self.contents);contents['consultations.sqlite3']=b'invalid SQLite';self.set_payload(self.archive(contents))
        with self.assertRaises((sqlite3.DatabaseError,ValueError)):self.verify()

    def test_private_rsa_key_size_is_checked(self):
        small=rsa.generate_private_key(public_exponent=65537,key_size=2048)
        with self.assertRaises(ValueError):verify.verify_bundle(small,self.bundle,self.expected_hash())

if __name__=='__main__':unittest.main()
