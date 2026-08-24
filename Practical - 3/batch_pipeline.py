import glob
import os
import time

import pandas as pd


INPUT_DIR = "data/incoming"
RESULT_DIR = "data/results"

os.makedirs(
    RESULT_DIR,
    exist_ok=True
)


def process_batch(filename):

    start_time = time.perf_counter()

    df = pd.read_csv(filename)

    average_response = (
        df["response_time_ms"].mean()
    )

    average_cpu = (
        df["cpu_percent"].mean()
    )

    average_memory = (
        df["memory_percent"].mean()
    )

    error_count = (
        df["status_code"] >= 400
    ).sum()

    processing_time = (
        time.perf_counter() - start_time
    )

    result = {

        "file":
            os.path.basename(filename),

        "records":
            len(df),

        "average_response_ms":
            round(average_response, 2),

        "average_cpu":
            round(average_cpu, 2),

        "average_memory":
            round(average_memory, 2),

        "errors":
            int(error_count),

        "processing_time_seconds":
            round(processing_time, 6)
    }

    print(result)

    return result


def main():

    print(
        "Starting micro-batch pipeline..."
    )

    files = sorted(
        glob.glob(
            os.path.join(
                INPUT_DIR,
                "*.csv"
            )
        )
    )

    if not files:

        print("No input files found.")
        return

    results = []

    for filename in files:

        result = process_batch(filename)

        results.append(result)

    results_df = pd.DataFrame(results)

    output_file = os.path.join(
        RESULT_DIR,
        "batch_results.csv"
    )

    results_df.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nResults saved to: {output_file}"
    )

    print(
        "\nMicro-batch pipeline completed."
    )


if __name__ == "__main__":
    main()