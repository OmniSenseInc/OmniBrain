"""Local consented review-job retry. No model, messaging, account access or runtime tools."""
import argparse,json
from pathlib import Path
from consultation_gateway import Store
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);args=p.parse_args()
    print(json.dumps(Store(args.data).retry_review_sync()))
