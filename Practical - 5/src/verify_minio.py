import json
from pathlib import Path
import boto3

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "minio_objects.json"
BUCKET = "practical5-metrics"

def main():
    s3 = boto3.client("s3", endpoint_url="http://localhost:9000",
        aws_access_key_id="minioadmin", aws_secret_access_key="minioadmin",
        region_name="us-east-1")
    paginator = s3.get_paginator("list_objects_v2")
    objects = []
    for page in paginator.paginate(Bucket=BUCKET):
        for item in page.get("Contents", []):
            objects.append({"key":item["Key"], "size_bytes":item["Size"]})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(objects, indent=2), encoding="utf-8")
    print(f"Bucket: {BUCKET}; objects found: {len(objects)}")
    for item in objects[:20]:
        print(f"{item['key']} ({item['size_bytes']:,} bytes)")
    print(f"Saved: {OUT}")

if __name__ == "__main__":
    main()
