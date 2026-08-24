import os
import pandas as pd
import matplotlib.pyplot as plt

RESULTS_DIR = "data/results"

batch_file = os.path.join(
    RESULTS_DIR,
    "batch_results.csv"
)

streaming_file = os.path.join(
    RESULTS_DIR,
    "streaming_results.csv"
)

print("===== BENCHMARK ANALYSIS =====\n")

if os.path.exists(batch_file):

    batch = pd.read_csv(batch_file)

    print("MICRO-BATCH RESULTS")
    print("-------------------")

    print(
        batch[
            [
                "records",
                "processing_time_ms",
                "avg_response_time_ms"
            ]
        ].describe()
    )

else:

    print("batch_results.csv not found.")


if os.path.exists(streaming_file):

    streaming = pd.read_csv(streaming_file)

    print("\nSTREAMING RESULTS")
    print("-----------------")

    print(
        streaming["latency_ms"].describe()
    )

    throughput = (
        len(streaming) /
        (
            streaming["received_at"].max()
            - streaming["received_at"].min()
        )
    )

    print(
        f"\nApprox streaming throughput: "
        f"{throughput:.2f} events/sec"
    )

    plt.figure()

    plt.hist(
        streaming["latency_ms"].dropna(),
        bins=30
    )

    plt.xlabel("Latency (ms)")
    plt.ylabel("Number of Events")
    plt.title("Kafka Streaming Latency Distribution")

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            RESULTS_DIR,
            "streaming_latency_distribution.png"
        )
    )

    plt.show()

else:

    print("streaming_results.csv not found.")

print("\nBenchmark completed.")