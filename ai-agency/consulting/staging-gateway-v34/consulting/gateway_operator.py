"""Local operator queue; no external notifications or client-controlled roles."""
import argparse
import json
from pathlib import Path
from consultation_gateway import Store

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',default=str(Path(__file__).with_name('data')))
    p.add_argument('--import-intake',metavar='CASE_ID')
    a=p.parse_args();s=Store(a.data)
    print(json.dumps(s.import_intake(a.import_intake) if a.import_intake else s.queue(),ensure_ascii=False,indent=2))
