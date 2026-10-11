"""Export an authenticated existing snapshot and RSA-wrapped key, never plaintext."""
from pathlib import Path
import argparse,hashlib,json,os,re,stat,sys,tempfile,zipfile
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.primitives.asymmetric import padding,rsa

# Production exports use the installed, root-owned validation implementation.
sys.path.insert(0,'/opt/omnisense-ops')
import omnisense_ops as ops

LABEL=b'OmniSense recovery v1'
SNAPSHOT_NAME=re.compile(r'snapshot-\d{8}T\d{6}Z(?:-[0-9a-f]{32})?\.fernet\Z')

def digest_stream(f):
    digest=hashlib.sha256()
    for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()

def read_backup_key(path):
    fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
    with os.fdopen(fd,'rb') as f:
        st=os.fstat(f.fileno())
        if st.st_uid!=0 or st.st_mode&0o077 or not stat.S_ISREG(st.st_mode) or st.st_size!=44:raise PermissionError('Unsafe backup key')
        secret=f.read(45)
    if len(secret)!=44:raise ValueError('Backup key length invalid')
    return secret

def export_bundle(public_key,out):
    out=Path(out);public_key=Path(public_key)
    pub=serialization.load_pem_public_key(ops._read_bounded(public_key,8192))
    if not isinstance(pub,rsa.RSAPublicKey) or not 3072<=pub.key_size<=8192:raise ValueError('Recovery RSA key size invalid')
    public_hash=hashlib.sha256(pub.public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo)).hexdigest()
    pending=None
    with ops._backup_lock():
        report=json.loads(ops._read_bounded(ops.STATE/'last-backup.json',16384));name=report.get('file')
        if not isinstance(name,str) or not SNAPSHOT_NAME.fullmatch(name):raise ValueError('Unexpected snapshot name')
        snapshot=ops.BACKUPS/name
        if snapshot.is_symlink():raise ValueError('Snapshot symlink invalid')
        ops.restore_test(snapshot)
        secret=read_backup_key(ops.KEY)
        wrapped=pub.encrypt(secret,padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=LABEL))
        try:
            snapshot_fd=os.open(snapshot,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
            with os.fdopen(snapshot_fd,'rb') as source:
                st=os.fstat(source.fileno())
                if not stat.S_ISREG(st.st_mode) or st.st_size>ops._ciphertext_cap() or st.st_size!=report.get('bytes'):raise ValueError('Snapshot size invalid')
                fd,pending_name=tempfile.mkstemp(prefix='.'+out.name+'.',suffix='.pending',dir=out.parent)
                pending=Path(pending_name);digest=hashlib.sha256();count=0
                with os.fdopen(fd,'wb') as f:
                    with zipfile.ZipFile(f,'w',zipfile.ZIP_STORED) as z:
                        with z.open(name,'w') as target:
                            while True:
                                block=source.read(1024*1024)
                                if not block:break
                                count+=len(block)
                                if count>ops._ciphertext_cap():raise ValueError('Snapshot grew beyond cap')
                                digest.update(block);target.write(block)
                        if count!=st.st_size:raise ValueError('Snapshot changed during export')
                        metadata={'version':1,'snapshot':name,'snapshot_bytes':count,'snapshot_sha256':digest.hexdigest(),'key_encryption':'RSA-OAEP-SHA256','public_key_sha256':public_hash,'no_plaintext_key':True}
                        z.writestr('backup-key.oaep',wrapped);z.writestr('manifest.json',json.dumps(metadata,indent=2))
                    f.flush();os.fsync(f.fileno())
            # Publish without overwriting an existing delivery, then remove the private temp name.
            os.link(pending,out);pending.unlink();pending=None;ops._sync_directory(out.parent)
        finally:
            if pending is not None and pending.exists():pending.unlink()
    with out.open('rb') as f:bundle_hash=digest_stream(f)
    return {'encrypted_recovery_bundle_created':True,'bytes':out.stat().st_size,'snapshot':name,'bundle_sha256':bundle_hash,'no_plaintext_key_exported':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--public-key',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if os.geteuid()!=0:raise PermissionError('Root required')
    print(json.dumps(export_bundle(a.public_key,a.out)))
