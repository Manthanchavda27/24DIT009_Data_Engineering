# Practical 10 — Batch and Streaming Transformations

## Windows CMD setup
```cmd
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python src\run_practical.py
```

This runnable starter uses Python/Pandas to simulate batch and streaming-style micro-batches without requiring a local Spark/Java installation. Your practical index lists PySpark, Pandas, and Python datetime tools; if faculty requires actual Spark execution, this simulation must be ported to Spark Structured Streaming.

## Demonstrates
- Batch filtering and metadata enrichment joins
- Out-of-order IoT events and a simulated 2-minute watermark
- Five-minute rolling aggregations and tumbling windows
- Rolling-volume threshold alerts

## Outputs
`data/iot_telemetry.csv`, `data/device_metadata.csv`, `output/transformed_events.csv`, `output/late_events.csv`, `output/window_comparison.csv`, `output/rolling_volume_alerts.csv`, and `output/practical_report.md`.
