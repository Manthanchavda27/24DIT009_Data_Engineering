# Data Engineering Practical 3

## Micro-Batch and Real-Time Streaming Data Ingestion

### Problem Definition

Design, implement and evaluate two parallel data ingestion pipelines:

1. Periodic time-triggered micro-batch processing
2. Continuous low-latency real-time event streaming

The pipelines process simulated web application activity logs and server performance telemetry.

---

## Objectives

- Implement a micro-batch ingestion pipeline.
- Implement a real-time Kafka streaming pipeline.
- Run Apache Kafka using Docker.
- Generate telemetry data.
- Measure processing latency.
- Measure streaming throughput.
- Simulate traffic spikes.
- Demonstrate Kafka partitions.
- Demonstrate consumer-group scaling.
- Evaluate fault-tolerance concepts.
- Compare batch and streaming architectures.

---

## Technologies

- Docker
- Apache Kafka 4.3.1
- Python
- kafka-python-ng
- Pandas
- Matplotlib

---

## Project Structure

```text
Practical - 3/
│
├── data/
│   ├── incoming/
│   └── results/
│
├── scripts/
│   ├── generate_data.py
│   ├── batch_pipeline.py
│   ├── streaming_producer.py
│   ├── streaming_consumer.py
│   └── benchmark.py
│
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .gitignore