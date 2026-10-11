from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, shutil, zipfile

base = Path("/home/ubuntu/ai-agency")
site = (base/"website").resolve()
bundle = base/"meeting/omnisense-architect-patch.zip"
expected = {"index.html","assets/architect.css","assets/architect-motion.js","assets/architect-rig.js","assets/architect.webp"}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
with zipfile.ZipFile(bundle) as package:
    assert set(package.namelist()) == expected|{"patch-manifest.json"}, "unexpected package entries"
    manifest = json.loads(package.read("patch-manifest.json"))
    assert set(manifest["files"]) == expected
    baseline = manifest["baseline_index_sha256"]
    assert sha(site/"index.html") == baseline, "homepage changed since review; deployment stopped"
    stage = base/"staging"/("architect_"+stamp)
    backup = base/"backups"/("website_architect_"+stamp)
    stage.mkdir(parents=True,mode=0o700)
    backup.mkdir(parents=True,mode=0o700)
    for name in sorted(expected):
        contents = package.read(name)
        assert hashlib.sha256(contents).hexdigest() == manifest["files"][name], "package hash mismatch"
        destination = stage/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(contents)
        current = site/name
        assert site in current.resolve().parents, "path outside website"
        if current.exists():
            saved = backup/name
            saved.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(current,saved)
    for name in sorted(expected-{"index.html"})+["index.html"]:
        if name=="index.html":
            assert sha(site/"index.html")==baseline, "homepage changed during preparation"
        destination=site/name
        temporary=destination.with_name(destination.name+".architect-install-"+stamp)
        with temporary.open("wb") as handle:
            handle.write((stage/name).read_bytes())
            handle.flush();os.fsync(handle.fileno())
        temporary.chmod(0o644)
        os.replace(temporary,destination)
        assert sha(destination)==manifest["files"][name]
    record={"backup":str(backup),"staging":str(stage),"installed":manifest["files"],"baseline":baseline}
    (backup/"deployment.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
    print(json.dumps(record,indent=2))
