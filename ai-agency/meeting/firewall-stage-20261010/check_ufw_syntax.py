import json,subprocess
args=['allow','proto','tcp','from','103.21.244.0/22','to','any','port','80,443','comment','OmniSense Cloudflare web']
for prefix in [['ufw','--dry-run'],['ufw','--dry-run','--force']]:
    r=subprocess.run(prefix+args,capture_output=True,text=True,timeout=20)
    print(json.dumps({'force':'--force' in prefix,'returncode':r.returncode,'stderr':r.stderr[:1000],'stdout_lines':len(r.stdout.splitlines())}))
print(subprocess.check_output(['ufw','status','numbered'],text=True))
