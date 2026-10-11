"""Bounded in-memory recovery check; private key is protected by Windows CurrentUser."""
import argparse,ctypes,gzip,hashlib,hmac,io,json,math,os,re,sqlite3,stat,struct,tarfile,zipfile
from pathlib import Path
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.primitives.asymmetric import padding,rsa
from cryptography.fernet import Fernet
import omnisense_ops as ops

LABEL=b'OmniSense recovery v1'
SNAPSHOT_NAME=re.compile(r'snapshot-\d{8}T\d{6}Z(?:-[0-9a-f]{32})?\.fernet\Z')
HEX=re.compile(r'[0-9a-f]{64}\Z')
DATABASES={'consultations.sqlite3','pipeline.sqlite3','web_security.sqlite3','wa_security.sqlite3'}
SEEDS={'web-rate-key','wa-rate-key'}
CONTENTS=DATABASES|SEEDS
METADATA_FIELDS={'version','snapshot','snapshot_bytes','snapshot_sha256','key_encryption','public_key_sha256','no_plaintext_key'}
MAX_METADATA=16384
MAX_WRAPPED_KEY=1024
MAX_PRIVATE_BLOB=32768

class Blob(ctypes.Structure):_fields_=[('size',ctypes.c_ulong),('data',ctypes.POINTER(ctypes.c_ubyte))]

def unprotect(data):
    if os.name!='nt':raise OSError('Windows CurrentUser is required')
    if len(data)>MAX_PRIVATE_BLOB:raise ValueError('Private key blob exceeds cap')
    raw=ctypes.create_string_buffer(data);src=Blob(len(data),ctypes.cast(raw,ctypes.POINTER(ctypes.c_ubyte)));out=Blob()
    api=ctypes.windll.crypt32.CryptUnprotectData
    api.argtypes=[ctypes.POINTER(Blob),ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong,ctypes.POINTER(Blob)];api.restype=ctypes.c_int
    free=ctypes.windll.kernel32.LocalFree;free.argtypes=[ctypes.c_void_p];free.restype=ctypes.c_void_p
    if not api(ctypes.byref(src),None,None,None,None,1,ctypes.byref(out)):raise ctypes.WinError()
    try:
        if out.size>MAX_PRIVATE_BLOB:raise ValueError('Unprotected private key exceeds cap')
        return ctypes.string_at(out.data,out.size)
    finally:free(ctypes.cast(out.data,ctypes.c_void_p))

def strict_json(data):
    def pairs(items):
        result={}
        for name,value in items:
            if name in result:raise ValueError('Duplicate JSON field')
            result[name]=value
        return result
    def constant(value):raise ValueError('Nonfinite JSON value')
    return json.loads(data,object_pairs_hook=pairs,parse_constant=constant)

def digest_stream(f):
    digest=hashlib.sha256()
    for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()

def check_zip_envelope(f,size):
    if size<22 or size>ops._ciphertext_cap()+MAX_METADATA+MAX_WRAPPED_KEY+8192+22:raise ValueError('Recovery bundle size invalid')
    f.seek(-22,os.SEEK_END)
    signature,disk,cd_disk,on_disk,total,cd_size,cd_offset,comment=struct.unpack('<4s4H2LH',f.read(22))
    if signature!=b'PK\x05\x06' or disk or cd_disk or on_disk!=3 or total!=3 or comment or cd_size>8192 or cd_offset+cd_size!=size-22:raise ValueError('Recovery ZIP envelope invalid')
    f.seek(0)

def verify_archive(plain):
    if len(plain)>ops._archive_cap():raise ValueError('Recovery payload exceeds cap')
    seen=set();digests={};checks=[];manifest=None;total=0
    with gzip.GzipFile(fileobj=io.BytesIO(plain),mode='rb') as gz:
        bounded=ops._BoundedReader(gz,ops.MAX_BYTES+ops.MAX_MANIFEST_BYTES+ops.ARCHIVE_OVERHEAD_BYTES)
        with tarfile.open(fileobj=bounded,mode='r|') as tar:
            for member in tar:
                cap=ops.MAX_MANIFEST_BYTES if member.name=='manifest.json' else ops.MAX_MEMBER_BYTES
                if member.name not in CONTENTS|{'manifest.json'} or member.name in seen or not member.isfile() or member.sparse is not None or member.size<0 or member.size>cap:raise ValueError('Recovery tar member invalid')
                seen.add(member.name);source=tar.extractfile(member)
                if source is None:raise ValueError('Recovery member unavailable')
                if member.name=='manifest.json':manifest=strict_json(source.read(ops.MAX_MANIFEST_BYTES+1));continue
                total+=member.size
                if total>ops.MAX_BYTES:raise ValueError('Recovery expanded contents exceed cap')
                if member.name in SEEDS and member.size!=32:raise ValueError('Recovery rate seed size invalid')
                data=source.read(member.size+1)
                if len(data)!=member.size:raise ValueError('Recovery member size mismatch')
                digests[member.name]=hashlib.sha256(data).hexdigest()
                if member.name in DATABASES:
                    db=sqlite3.connect(':memory:')
                    try:
                        db.deserialize(data);db.execute('PRAGMA query_only=ON');db.execute('PRAGMA trusted_schema=OFF')
                        if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('Recovery database invalid')
                    finally:db.close()
                    checks.append(member.name)
        while bounded.read(1024*1024):pass
    if seen!=CONTENTS|{'manifest.json'} or not isinstance(manifest,dict) or type(manifest.get('version')) is not int or manifest.get('version')!=1 or manifest.get('sha256')!=digests:raise ValueError('Recovery manifest or member hashes invalid')
    if set(manifest)-{'version','created','cross_database_atomic','sha256'}:raise ValueError('Recovery manifest fields invalid')
    if 'created' in manifest and (type(manifest['created']) not in (int,float) or not math.isfinite(manifest['created']) or manifest['created']<0):raise ValueError('Recovery timestamp invalid')
    if 'cross_database_atomic' in manifest and manifest['cross_database_atomic'] is not False:raise ValueError('Recovery consistency metadata invalid')
    if set(checks)!=DATABASES:raise ValueError('Recovery database set incomplete')
    return checks

def verify_bundle(private,bundle,expected_bundle_sha256):
    if not isinstance(private,rsa.RSAPrivateKey) or not 3072<=private.key_size<=8192:raise ValueError('Recovery private RSA key size invalid')
    if not isinstance(expected_bundle_sha256,str) or not HEX.fullmatch(expected_bundle_sha256):raise ValueError('Trusted bundle checksum is required')
    bundle=Path(bundle)
    with bundle.open('rb') as f:
        st=os.fstat(f.fileno())
        if not stat.S_ISREG(st.st_mode):raise ValueError('Recovery bundle must be a regular file')
        check_zip_envelope(f,st.st_size)
        if not hmac.compare_digest(digest_stream(f),expected_bundle_sha256):raise ValueError('Trusted bundle checksum mismatch')
        f.seek(0)
        with zipfile.ZipFile(f) as z:
            members=z.infolist();names=[m.filename for m in members]
            snapshots=[n for n in names if SNAPSHOT_NAME.fullmatch(n)]
            if len(members)!=3 or len(set(names))!=3 or len(snapshots)!=1 or set(names)!={snapshots[0],'backup-key.oaep','manifest.json'}:raise ValueError('Recovery ZIP members invalid')
            for m in members:
                cap=MAX_METADATA if m.filename=='manifest.json' else MAX_WRAPPED_KEY if m.filename=='backup-key.oaep' else ops._ciphertext_cap()
                file_type=stat.S_IFMT(m.external_attr>>16)
                if m.is_dir() or file_type not in (0,stat.S_IFREG) or m.flag_bits&1 or m.compress_type!=zipfile.ZIP_STORED or m.file_size<0 or m.file_size>cap or m.compress_size!=m.file_size:raise ValueError('Recovery ZIP member bounds invalid')
            meta=strict_json(z.read('manifest.json'))
            if not isinstance(meta,dict) or set(meta)!=METADATA_FIELDS or type(meta['version']) is not int or meta['version']!=1 or meta['snapshot']!=snapshots[0] or meta['key_encryption']!='RSA-OAEP-SHA256' or meta['no_plaintext_key'] is not True:raise ValueError('Recovery metadata invalid')
            for n in ('snapshot_sha256','public_key_sha256'):
                if not isinstance(meta[n],str) or not HEX.fullmatch(meta[n]):raise ValueError('Recovery checksum format invalid')
            snapshot_info=z.getinfo(snapshots[0])
            if type(meta['snapshot_bytes']) is not int or meta['snapshot_bytes']!=snapshot_info.file_size:raise ValueError('Recovery snapshot size metadata invalid')
            public_hash=hashlib.sha256(private.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo)).hexdigest()
            if not hmac.compare_digest(public_hash,meta['public_key_sha256']):raise ValueError('Recovery public key mismatch')
            wrapped=z.read('backup-key.oaep')
            if len(wrapped)!=private.key_size//8:raise ValueError('Wrapped recovery key size invalid')
            payload=z.read(snapshots[0])
            if not hmac.compare_digest(hashlib.sha256(payload).hexdigest(),meta['snapshot_sha256']):raise ValueError('Snapshot transport hash mismatch')
    secret=private.decrypt(wrapped,padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=LABEL))
    if len(secret)!=44:raise ValueError('Unwrapped backup key length invalid')
    checks=verify_archive(Fernet(secret).decrypt(payload))
    return {'local_recovery_verified':True,'authenticated_decrypt':True,'databases_verified':len(checks),'plaintext_database_files_written':False,'trusted_bundle_checksum_verified':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--private-key',type=Path,required=True);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--expected-bundle-sha256',required=True);a=p.parse_args()
    private=serialization.load_der_private_key(unprotect(ops._read_bounded(a.private_key,MAX_PRIVATE_BLOB)),password=None)
    result=verify_bundle(private,a.bundle,a.expected_bundle_sha256)
    result['key_bound_to_current_windows_account']=True
    print(json.dumps(result))
