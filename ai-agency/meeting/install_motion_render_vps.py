from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,shutil,sys,zipfile

base=Path("/home/ubuntu/ai-agency")
site=(base/"website").resolve()
bundle=Path(sys.argv[1])
expected={"index.html","assets/architect.css","assets/architect-motion.js","assets/architect-rig.js","assets/architect.webp"}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
stage=base/"staging"/("motion_render_"+stamp)
backup=base/"backups"/("website_motion_render_"+stamp)
changed=[]
with zipfile.ZipFile(bundle) as package:
    assert set(package.namelist())==expected|{"patch-manifest.json"}
    manifest=json.loads(package.read("patch-manifest.json"))
    assert set(manifest["files"])==expected
    assert set(manifest["expected_current_files"])==expected
    for name,before in manifest["expected_current_files"].items():
        destination=site/name
        assert site in destination.resolve().parents
        assert sha(destination)==before, "file changed since reviewed baseline: "+name
    stage.mkdir(parents=True,mode=0o700)
    backup.mkdir(parents=True,mode=0o700)
    for name in sorted(expected):
        data=package.read(name)
        assert hashlib.sha256(data).hexdigest()==manifest["files"][name]
        staged=stage/name;staged.parent.mkdir(parents=True,exist_ok=True);staged.write_bytes(data)
        saved=backup/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(site/name,saved)
    def replace(destination,data):
        temporary=destination.with_name(destination.name+".motion-install-"+stamp)
        with temporary.open("wb") as handle:
            handle.write(data);handle.flush();os.fsync(handle.fileno())
        temporary.chmod(0o644);os.replace(temporary,destination)
    try:
        for name in sorted(expected-{"index.html"})+["index.html"]:
            assert sha(site/name)==manifest["expected_current_files"][name], "file changed during install: "+name
            replace(site/name,(stage/name).read_bytes());changed.append(name)
            assert sha(site/name)==manifest["files"][name]
    except Exception:
        for name in reversed(changed):
            if sha(site/name)==manifest["files"][name]:
                replace(site/name,(backup/name).read_bytes())
        raise
    record={"backup":str(backup),"staging":str(stage),"version":manifest["version"],"installed":manifest["files"],"previous":manifest["expected_current_files"]}
    (backup/"deployment.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
    print(json.dumps(record,indent=2))
