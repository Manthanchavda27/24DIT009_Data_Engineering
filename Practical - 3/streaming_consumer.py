import json
import random
import time
from datetime import datetime, timezone

from kafka import KafkaProducer


producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda value:
        json.dumps(value).encode("utf-8")
)


EVENT_TYPES = [
    "page_view",
    "login",
    "logout",
    "api_request",
    "file_download",
    "search"
]


ENDPOINTS = [
    "/",
    "/login",
    "/dashboard",
    "/api/users",
    "/api/data",
    "/search"
]


def generate_event():

    return {

        "timestamp":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "sent_at":
            time.time(),

        "user_id":
            f"U{random.randint(1000, 9999)}",

        "event_type":
            random.choice(EVENT_TYPES),

        "endpoint":
            random.choice(ENDPOINTS),

        "response_time_ms":
            random.randint(20, 800),

        "cpu_percent":
            round(
                random.uniform(20, 95),
                2
            ),

        "memory_percent":
            round(
                random.uniform(30, 90),
                2
            ),

        "status_code":
            random.choice(
                [200, 200, 200, 201, 400, 404, 500]
            )
    }


print("Kafka streaming producer started...")

try:

    while True:

        event = generate_event()

        producer.send(
            "user-telemetry",
            value=event
        )

        print(
            f"Sent | "
            f"user={event['user_id']} | "
            f"event={event['event_type']}"
        )

        # Approximately 10 events/sec
        time.sleep(0.1)

except KeyboardInterrupt:

    print("\nProducer stopped.")

finally:

    producer.flush()
    producer.close()