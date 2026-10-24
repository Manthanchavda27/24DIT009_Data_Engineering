from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT = ROOT / "data", ROOT / "output"
WATERMARK_MINUTES, WINDOW_MINUTES = 2, 5


def main():
    DATA.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    base = pd.Timestamp("2025-06-01 10:00:00")
    specs = [
        ("evt01","devA",0,0,12.0), ("evt02","devA",60,60,18.0),
        ("evt03","devB",90,90,25.0), ("evt04","devA",120,480,20.0),
        ("evt05","devB",180,190,30.0), ("evt06","devA",240,240,15.0),
        ("evt07","devB",300,300,35.0), ("evt08","devA",360,360,22.0),
        ("evt09","devB",420,900,40.0), ("evt10","devA",480,490,28.0),
        ("evt11","devB",540,540,45.0), ("evt12","devA",600,600,16.0)
    ]
    events = pd.DataFrame([{
        "event_id": eid, "device_id": dev, "event_time": base + pd.Timedelta(seconds=event_s),
        "arrival_time": base + pd.Timedelta(seconds=arrival_s), "volume": volume
    } for eid,dev,event_s,arrival_s,volume in specs])
    metadata = pd.DataFrame([
        {"device_id":"devA","site":"Factory-A","device_type":"temperature_sensor","critical_limit":25.0},
        {"device_id":"devB","site":"Factory-B","device_type":"flow_sensor","critical_limit":40.0}
    ])
    events.to_csv(DATA / "iot_telemetry.csv", index=False)
    metadata.to_csv(DATA / "device_metadata.csv", index=False)

    filtered = events[events.volume >= 15].copy()
    enriched = filtered.merge(metadata, on="device_id", how="left", validate="many_to_one")
    enriched["delay_minutes"] = (enriched.arrival_time - enriched.event_time).dt.total_seconds() / 60
    enriched["is_late_by_watermark"] = enriched.delay_minutes > WATERMARK_MINUTES
    on_time = enriched[~enriched.is_late_by_watermark].copy()
    late = enriched[enriched.is_late_by_watermark].copy()
    late.to_csv(OUT / "late_events.csv", index=False)

    parts = []
    for _, group in on_time.groupby("device_id"):
        group = group.sort_values("event_time").set_index("event_time")
        group["rolling_5min_volume"] = group.volume.rolling("5min", closed="both").sum()
        group["rolling_5min_event_count"] = group.volume.rolling("5min", closed="both").count().astype(int)
        parts.append(group.reset_index())
    rolling = pd.concat(parts, ignore_index=True)
    rolling["tumbling_window_start"] = rolling.groupby("device_id").event_time.transform(
        lambda s: s.min() + pd.to_timedelta(((s - s.min()).dt.total_seconds() // 300) * 300, unit="s")
    )
    tumbling = rolling.groupby(["device_id","tumbling_window_start"], as_index=False).agg(
        tumbling_event_count=("event_id","count"), tumbling_volume=("volume","sum"))
    alerts = rolling[rolling.rolling_5min_volume >= 70][
        ["event_id","device_id","event_time","rolling_5min_volume","rolling_5min_event_count"]]

    rolling.to_csv(OUT / "transformed_events.csv", index=False)
    tumbling.to_csv(OUT / "window_comparison.csv", index=False)
    alerts.to_csv(OUT / "rolling_volume_alerts.csv", index=False)
    report = f"""# Practical 10 — Batch and Streaming Transformations

## Execution summary
- Input telemetry events: {len(events)}
- Events remaining after volume filter (volume >= 15): {len(enriched)}
- Events accepted by simulated watermark: {len(on_time)}
- Events flagged late and excluded from on-time aggregates: {len(late)}
- Watermark delay: {WATERMARK_MINUTES} minutes
- Window size: {WINDOW_MINUTES} minutes

## Transformations
1. Conditional filtering: volume >= 15.
2. Enrichment join: telemetry joined with device metadata on device_id.
3. Late data: arrival delay beyond the simulated watermark is logged separately.
4. Rolling window: five-minute sum and event count per device.
5. Tumbling window: fixed non-overlapping five-minute buckets.
6. Example threshold alert: rolling five-minute volume >= 70.

## Rolling vs tumbling
Rolling windows overlap and update for each event, offering finer detail but requiring more repeated computation/state. Tumbling windows use fixed non-overlapping blocks and are generally simpler to maintain.

## Watermark
A watermark is an event-time progress threshold that bounds how long a streaming engine waits for late records. Exact handling of late events depends on the engine and configuration.

## Output files
- transformed_events.csv — enriched on-time events and rolling metrics
- late_events.csv — records beyond the simulated watermark
- window_comparison.csv — tumbling aggregates
- rolling_volume_alerts.csv — sample rolling threshold alerts

## Limitation
This is a finite Pandas simulation of streaming/watermark behavior. The practical index lists PySpark; if actual Spark execution is mandatory, this must be ported to Spark Structured Streaming.
"""
    (OUT / "practical_report.md").write_text(report, encoding="utf-8")
    print("Practical 10 completed successfully.")
    print(f"Input events: {len(events)}")
    print(f"Filtered/enriched events: {len(enriched)}")
    print(f"Accepted on-time events: {len(on_time)}")
    print(f"Late events: {len(late)}")
    print(f"Rolling volume alerts: {len(alerts)}")
    print("\nGenerated files:")
    for f in ["transformed_events.csv","late_events.csv","window_comparison.csv","rolling_volume_alerts.csv","practical_report.md"]:
        print(f"  output\\{f}")


if __name__ == "__main__":
    main()
