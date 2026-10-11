import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import time

stage=Path(__file__).resolve().parent
site=Path('/home/ubuntu/ai-agency/website')
consult=Path('/home/ubuntu/ai-agency/consulting')
plugin=Path('/home/ubuntu/.hermes/plugins/omnisense-consultation')
expected={
 site/'index.html':'ab27bd601da8efbca3bbb8f5a2914b01c0d18b1be00006701f5c4d7450f8972a',
 site/'konsultasi-v3.html':'0a41915a0173727552f1f9b87fab28ce119d7afd49c0d2a3b49431331c9558ee',
 site/'privacy.html':'4893c3a6d7128d389e9680a09c3acd7a0b89080aff3ebc7b8f4b34f6c934d875',
 consult/'consultation_gateway.py':'b4c4a2c10c935b4064c48bfec5143c45fc6bee936d286f6423c8a5a1ba7ba384',
 consult/'consultation_dialogue.py':'8a12a0e88caeceb5c6911ee61e8398c294fa4a224687e3ee01d9331053aa3854',
 plugin/'__init__.py':'c5e37674c0ccf42966253a7d511f020d707cc43978baffe311a3048b568f4dd5',
}
for target,digest in expected.items():
 if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:raise SystemExit('Baseline changed: '+str(target))
db=consult/'data/consultations.sqlite3'
with sqlite3.connect(db) as c:
 if c.execute("SELECT count(*) FROM replies WHERE status='pending' AND created>?",(time.time()-60,)).fetchone()[0]:raise SystemExit('Recent pending reply; defer install until idle')
backup=consult/('backup_optimization_v35_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
backup.mkdir(mode=0o700)
with sqlite3.connect(db) as source,sqlite3.connect(backup/'consultations.sqlite3') as destination:source.backup(destination)
os.chmod(backup/'consultations.sqlite3',0o600)
files=[*( (stage/'website'/name,site/name) for name in ['index.html','konsultasi-v3.html','privacy.html','assets/konsultasi-ui-v35.js']),*((stage/'consulting'/name,consult/name) for name in ['consultation_gateway.py','consultation_dialogue.py','gateway_operator.py','GATEWAY_KONSULTASI_V35.md','test_optimization_v35.py']), (stage/'hermes-plugin/__init__.py',plugin/'__init__.py')]
manifest={}
for source,target in files:
 if target.exists():
  old=backup/target.relative_to('/home/ubuntu');old.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,old)
 temp=target.with_name(target.name+'.v35-new');temp.write_bytes(source.read_bytes());os.chmod(temp,0o644);os.replace(temp,target)
 manifest[str(target)]=hashlib.sha256(target.read_bytes()).hexdigest()
(backup/'installation.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'backup':str(backup),'installed':manifest},indent=2))
