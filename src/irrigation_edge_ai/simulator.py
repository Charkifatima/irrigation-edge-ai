"""Capteurs synthétiques sur CPU : aucune commande de pompe ni modèle IA."""
import argparse
from datetime import datetime, timezone
import json
import math
import random
import time


def positive_integer(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("count doit être supérieur à zéro")
    return number


def nonnegative_finite(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise argparse.ArgumentTypeError("interval doit être fini et positif ou nul")
    return number


def samples(count: int, seed: int):
    """Émet des mesures une à une ; les plages servent uniquement à la démo."""
    rng = random.Random(seed)
    for sequence in range(1, count + 1):
        yield {
            "schema_version": 1,
            "device_id": "edge-sim-01",
            "simulated": True,
            "sequence": sequence,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "soil_moisture_pct": round(rng.uniform(15, 65), 2),
            "air_temperature_c": round(rng.uniform(18, 38), 2),
            "relative_humidity_pct": round(rng.uniform(25, 85), 2),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=positive_integer, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--interval", type=nonnegative_finite, default=1.0,
                        help="secondes entre deux mesures ; 0 pour un test rapide")
    args = parser.parse_args()
    for sample in samples(args.count, args.seed):
        print(json.dumps(sample), flush=True)
        if sample["sequence"] < args.count:
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
