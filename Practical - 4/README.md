# ITUC301 Data Engineering — Practical 4
## ETL vs ELT Pipeline Design

This project implements the Practical 4 requirement from the ITUC301 Data Engineering practical list:

- ETL: Extract → Transform in Python/Pandas → Load into DuckDB
- ELT: Extract → Load raw data into DuckDB staging → Transform using DuckDB SQL
- Both pipelines use the same retail transaction CSV.
- Execution time, row counts, output comparison, and basic lineage are recorded.

### Dataset
The dataset is generated locally by `src/generate_data.py`. It intentionally contains:
- inconsistent whitespace
- legacy store codes
- numeric values represented as raw strings
- transaction timestamps
- product/category information

### Transformation rules
1. Trim whitespace from text columns.
2. Convert quantity to integer.
3. Convert unit_price to numeric.
4. Map legacy store codes:
   - ST001 / OLD01 → AHMEDABAD
   - ST002 / OLD02 → VADODARA
   - ST003 / OLD03 → SURAT
   - ST004 / OLD04 → RAJKOT
   - ST005 / OLD05 → ANAND
5. Parse transaction_date as a timestamp.
6. Calculate `total_amount = quantity * unit_price`.
7. Keep a clean analytical table with standardized fields.

### Run
From the project root:

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

Windows CMD:
```cmd
.venv\Scripts\activate
```

Linux/macOS:
```bash
source .venv/bin/activate
```

Install:
```bash
python -m pip install -r requirements.txt
```

Generate data:
```bash
python src/generate_data.py --rows 100000
```

Run ETL:
```bash
python src/etl_pipeline.py
```

Run ELT:
```bash
python src/elt_pipeline.py
```

Compare results:
```bash
python src/compare_results.py
```

Generate final benchmark report:
```bash
python src/benchmark_report.py
```

### Expected output
After execution:

```text
data/
  raw/retail_sales.csv

output/
  etl.duckdb
  elt.duckdb
  etl_clean_sales.csv
  elt_clean_sales.csv
  benchmark.csv
  lineage.json
  final_report.md
```

### GitHub
```bash
git init
git branch -M main
git add .
git commit -m "Add Practical 4 ETL vs ELT pipeline"
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

Do not commit `.venv/` or generated DuckDB database files if your faculty repository should contain source code only. The included `.gitignore` excludes local environments and generated outputs.
