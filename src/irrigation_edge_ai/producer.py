
import argparse
import json
import os
import time
import random

from datetime import datetime, timezone
from kafka import KafkaProducer


def generate_measurement(sequence):
    rng = random.Random(sequence)

    return {
        "schema_version": 1,
        "device_id": "edge-sim-01",
        "simulated": True,
        "sequence": sequence,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "soil_moisture_pct": round(rng.uniform(15, 65), 2),
        "air_temperature_c": round(rng.uniform(18, 38), 2),
        "relative_humidity_pct": round(rng.uniform(25, 85), 2),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--interval", type=float, default=0.2)
    args = parser.parse_args()

    producer = KafkaProducer(
        bootstrap_servers=os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"
        ),
        value_serializer=lambda data: json.dumps(data).encode("utf-8"),
    )

    try:
        for sequence in range(1, args.count + 1):
            measurement = generate_measurement(sequence)

            producer.send(
                "irrigation-measurements",
                value=measurement,
            )

            print(f"Mesure envoyée : {sequence}", flush=True)
            time.sleep(args.interval)

        producer.flush()
        print("Envoi terminé : toutes les mesures ont été envoyées.")

    finally:
        producer.close()


if __name__ == "__main__":
    main()
