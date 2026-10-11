"""Inspect UFW IPv6 display using an allow subset of the existing public rule."""
import subprocess
from fw_rules import parse,baseline

def run(args):return subprocess.run(args,capture_output=True,text=True,check=True,timeout=20).stdout
baseline(parse(run(['ufw','status','numbered'])))
rule=['allow','proto','tcp','from','2400:cb00::/32','to','any','port','80,443','comment','OmniSense format check']
try:
    run(['ufw',*rule])
    for line in run(['ufw','status','numbered']).splitlines():
        if '2400:cb00' in line:print(line)
finally:run(['ufw','delete',*rule])
baseline(parse(run(['ufw','status','numbered'])))
print('original_six_rules_restored')
