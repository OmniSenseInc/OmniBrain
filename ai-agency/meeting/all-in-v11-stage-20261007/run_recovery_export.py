"""Run synthetic exporter checks, then export ciphertext to the owner account."""
from pathlib import Path
import hashlib,json,os,subprocess
from export_recovery import export_bundle

S=Path(__file__).resolve().parent
assert os.geteuid()==0
for name,want in {'export_recovery.py':'4fd6d6a2134e457ff4ca0c70e7e78f427cf37ac59f0a95ba88415ec90a783803','verify_local_recovery.py':'2a812eefd8aecaf6adfc62d21b1e5aaa3f1b2b8ffa6a70692c2668d62c446711','test_recovery_bundle.py':'45412be943311e35a97bf18791f62d7502973723953021e3fa71c3ae6c3770f3'}.items():
    assert hashlib.sha256((S/name).read_bytes()).hexdigest()==want
subprocess.run(['/home/ubuntu/.hermes/hermes-agent/venv/bin/python','-m','unittest','test_recovery_bundle'],cwd=S,check=True,timeout=60)
out=S/'encrypted-recovery-v11-20261007.zip'
report=export_bundle(S/'recovery-public.pem',out)
os.chown(out,1000,1000);out.chmod(0o600)
print(json.dumps(report))
