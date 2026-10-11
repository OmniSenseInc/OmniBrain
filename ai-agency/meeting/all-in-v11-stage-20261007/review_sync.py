"""Local consented review-job retry. No model, messaging, account access or runtime tools."""
import argparse,json
from pathlib import Path
from consultation_gateway import Store
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);args=p.parse_args()
    result=Store(args.data).retry_review_sync()
    print(json.dumps(result))
    raise SystemExit(1 if result['retry_pending'] else 0)
