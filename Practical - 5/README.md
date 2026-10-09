# ITUC301 Data Engineering — Practical 5: Distributed Storage Systems

## Demonstration
- Generate synthetic application metric data.
- Save an unpartitioned Parquet baseline.
- Save Hive-style partitions: `year=YYYY/month=MM/region=REGION/`.
- Compare a filtered full-file query with a query against the matching partition file.
- Optionally upload partitioned objects to MinIO (S3-compatible object storage) using Docker and Boto3.
- Generate a benchmark report.

## Windows CMD setup
Open CMD in this folder:
```cmd
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
```

## Run in this order
```cmd
python src\prepare_storage.py --rows 100000
python src\benchmark_queries.py --year 2025 --month 3 --region west
python src\create_report.py
```

## Optional MinIO section
Start Docker Desktop, then:
```cmd
docker compose up -d
python src\upload_to_minio.py
python src\verify_minio.py
```
MinIO Console: http://localhost:9001
S3 endpoint: http://localhost:9000
Demo credentials: `minioadmin` / `minioadmin`

Stop MinIO:
```cmd
docker compose down
```

## Output
`data/generated_metrics.csv`, `data/unpartitioned/metrics.parquet`, `data/partitioned/year=.../month=.../region=.../part-0.parquet`, `output/benchmark.json`, and `output/practical_report.md`.

## GitHub
```cmd
git init
git branch -M main
git add .
git commit -m "Add Practical 5 distributed storage systems"
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Generated data, output, `.venv`, and caches are excluded by `.gitignore`. Benchmark numbers are specific to your computer and dataset size.
