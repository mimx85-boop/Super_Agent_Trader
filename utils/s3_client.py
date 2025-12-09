import boto3
import pandas as pd
from io import BytesIO
from typing import List, Optional
from botocore.exceptions import ClientError


class S3Client:
    def __init__(self, region: str, bucket: str):
        self.s3 = boto3.client("s3", region_name=region)
        self.bucket = bucket

    def write_parquet(self, df: pd.DataFrame, key: str):
        buf = BytesIO()
        df.to_parquet(buf, index=True)
        buf.seek(0)
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=buf.getvalue())

    def read_parquet(self, key: str) -> pd.DataFrame:
        """
        Read a parquet file from S3 into a pandas DataFrame.
        
        We must fully read the StreamingBody into BytesIO because pyarrow
        expects a seekable file-like object, and the raw StreamingBody is not.
        """
        obj = self.s3.get_object(Bucket=self.bucket, Key=key)
        data = obj["Body"].read()  # bytes
        buf = BytesIO(data)
        return pd.read_parquet(buf)

    def list_keys(self, prefix: str) -> List[str]:
        keys = []
        continuation_token = None
        while True:
            kwargs = {"Bucket": self.bucket, "Prefix": prefix}
            if continuation_token:
                kwargs["ContinuationToken"] = continuation_token
            resp = self.s3.list_objects_v2(**kwargs)
            for item in resp.get("Contents", []):
                keys.append(item["Key"])
            if resp.get("IsTruncated"):
                continuation_token = resp.get("NextContinuationToken")
            else:
                break
        return keys

    def get_latest_key(self, prefix: str) -> Optional[str]:
        keys = self.list_keys(prefix)
        if not keys:
            return None
        keys.sort()
        return keys[-1]

    def list_prefixes(self, prefix: str) -> List[str]:
        """List 'folders' (common prefixes) directly under the given prefix."""
        prefixes: List[str] = []
        continuation_token = None
        while True:
            kwargs = {"Bucket": self.bucket, "Prefix": prefix, "Delimiter": "/"}
            if continuation_token:
                kwargs["ContinuationToken"] = continuation_token
            resp = self.s3.list_objects_v2(**kwargs)
            for p in resp.get("CommonPrefixes", []):
                prefixes.append(p["Prefix"])  # e.g., raw/AAPL/
            if resp.get("IsTruncated"):
                continuation_token = resp.get("NextContinuationToken")
            else:
                break
        return prefixes

    def delete_oldest(self, prefix: str) -> Optional[str]:
        """Delete the oldest object under the given prefix. Returns deleted key or None."""
        keys = self.list_keys(prefix)
        if not keys or len(keys) < 2:
            return None
        keys.sort()
        oldest = keys[0]
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=oldest)
            return oldest
        except ClientError:
            return None
