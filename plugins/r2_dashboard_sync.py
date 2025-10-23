import os
import boto3
from botocore.client import Config
import json
from datetime import datetime

S3_ENABLED = os.getenv("S3_ENABLED", "false").lower() == "true"
S3_BUCKET = os.getenv("S3_BUCKET")
S3_REGION = os.getenv("S3_REGION", "auto")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_ENDPOINT = os.getenv("S3_ENDPOINT")

def get_r2_client():
    if not S3_ENABLED:
        raise RuntimeError("R2 storage disabled")
    return boto3.client(
        "s3",
        region_name=S3_REGION,
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        config=Config(signature_version="s3v4")
    )

def fetch_latest_backup():
    """📊 Fetch most recent backup file from R2"""
    if not S3_ENABLED:
        return {"error": "Cloud sync disabled"}
    try:
        s3 = get_r2_client()
        files = s3.list_objects_v2(Bucket=S3_BUCKET)
        if "Contents" not in files:
            return {"error": "No backups found"}
        sorted_files = sorted(files["Contents"], key=lambda x: x["LastModified"], reverse=True)
        latest_file = sorted_files[0]["Key"]
        local_file = f"tmp_latest.json"
        s3.download_file(S3_BUCKET, latest_file, local_file)
        with open(local_file, "r") as f:
            data = json.load(f)
        print(f"✅ Dashboard sync: {latest_file}")
        return data
    except Exception as e:
        return {"error": str(e)}

# Optional test
if __name__ == "__main__":
    result = fetch_latest_backup()
    print(json.dumps(result, indent=2))
