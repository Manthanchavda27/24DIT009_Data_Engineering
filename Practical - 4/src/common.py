from pathlib import Path
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "retail_sales.csv"
OUTPUT_DIR = ROOT / "output"

STORE_MAP = {
    "ST001": "AHMEDABAD",
    "OLD01": "AHMEDABAD",
    "ST002": "VADODARA",
    "OLD02": "VADODARA",
    "ST003": "SURAT",
    "OLD03": "SURAT",
    "ST004": "RAJKOT",
    "OLD04": "RAJKOT",
    "ST005": "ANAND",
    "OLD05": "ANAND",
}

def clean_store_code(value):
    return str(value).strip().upper()

def store_name(value):
    return STORE_MAP.get(clean_store_code(value), "UNKNOWN")

def now_utc():
    return datetime.now(timezone.utc).isoformat()

def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def save_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
