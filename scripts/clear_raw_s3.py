import os
import sys
from pathlib import Path

# Ensure project root is on sys.path when running as a script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.s3_client import S3Client


def main():
    # Read bucket and region from environment or fall back to config defaults if you prefer later
    bucket = os.environ.get("S3_BUCKET")
    region = os.environ.get("AWS_REGION", "us-east-1")
    if not bucket:
        raise SystemExit("S3_BUCKET env var is required. Example: set S3_BUCKET=stock-trade-data-2025")

    s3 = S3Client(region=region, bucket=bucket)

    raw_prefix = "raw/"
    keys = s3.list_keys(raw_prefix)
    if not keys:
        print(f"No objects found under s3://{bucket}/{raw_prefix}")
        return

    print(f"Deleting {len(keys)} objects under s3://{bucket}/{raw_prefix} ...")

    # Use bulk delete in batches of 1000 for efficiency
    import boto3
    client = boto3.client("s3", region_name=region)

    batch = []
    for k in keys:
        batch.append({"Key": k})
        if len(batch) == 1000:
            client.delete_objects(Bucket=bucket, Delete={"Objects": batch, "Quiet": True})
            batch = []
    if batch:
        client.delete_objects(Bucket=bucket, Delete={"Objects": batch, "Quiet": True})

    print("Completed delete of raw/ prefix.")


if __name__ == "__main__":
    main()