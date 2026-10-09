from pathlib import Path
import boto3
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[1]
PART = ROOT / "data" / "partitioned"
BUCKET = "practical5-metrics"

def main():
    if not PART.exists():
        raise FileNotFoundError("Run prepare_storage.py first.")
    s3 = boto3.client("s3", endpoint_url="http://localhost:9000",
        aws_access_key_id="minioadmin", aws_secret_access_key="minioadmin",
        region_name="us-east-1")
    try:
        s3.head_bucket(Bucket=BUCKET)
    except ClientError:
        s3.create_bucket(Bucket=BUCKET)
    count = 0
    for path in PART.rglob("*.parquet"):
        key = path.relative_to(PART).as_posix()
        s3.upload_file(str(path), BUCKET, key)
        print(f"Uploaded s3://{BUCKET}/{key}")
        count += 1
    print(f"Upload complete. Objects uploaded: {count}")

if __name__ == "__main__":
    main()
