import os
import boto3
from botocore.client import Config
from datetime import datetime
import json

# ───────────────────────────────────────────────
# 🌩️  Load R2 environment
S3_ENABLED = os.getenv("S3_ENABLED", "false").lower() == "true"
S3_BUCKET = os.getenv("S3_BUCKET")
S3_REGION = os.getenv("S3_REGION", "auto")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_ENDPOINT = os.getenv("S3_ENDPOINT")

# ───────────────────────────────────────────────
# 📦  Create R2 client
def get_r2_client():
    if not S3_ENABLED:
        raise RuntimeError("R2 storage disabled (S3_ENABLED=false)")
    return boto3.client(
        "s3",
        region_name=S3_REGION,
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        config=Config(signature_version="s3v4")
    )

# ───────────────────────────────────────────────
# 🧠  Upload telemetry / backup file
def upload_backup(local_path: str, remote_name: str = None):
    if not S3_ENABLED:
        print("⚠️  Cloud sync skipped (S3 disabled).")
        return False

    if not remote_name:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        remote_name = f"backup_{timestamp}.json"

    s3 = get_r2_client()
    try:
        s3.upload_file(local_path, S3_BUCKET, remote_name)
        print(f"✅ Uploaded {remote_name} → R2 bucket {S3_BUCKET}")
        return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

# ───────────────────────────────────────────────
# ⬇️  Download file (optional, for dashboard)
def download_backup(remote_name: str, local_path: str):
    s3 = get_r2_client()
    try:
        s3.download_file(S3_BUCKET, remote_name, local_path)
        print(f"✅ Downloaded {remote_name} → {local_path}")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False


# ───────────────────────────────────────────────
# 🧩  Example manual test
if __name__ == "__main__":
    test_data = {"status": "AI sync demo", "timestamp": str(datetime.utcnow())}
    local = "telemetry_test.json"
    with open(local, "w") as f:
        json.dump(test_data, f, indent=2)
    upload_backup(local)
