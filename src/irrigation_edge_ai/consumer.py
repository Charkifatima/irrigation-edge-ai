
import json
import os
from datetime import datetime

from kafka import KafkaConsumer
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.engine import URL

from irrigation_edge_ai.models import Sensor, Measurement


# Configuration PostgreSQL
database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("POSTGRES_USER", "irrigation"),
    password=os.getenv("POSTGRES_PASSWORD", "irrigation"),
    host=os.getenv("POSTGRES_HOST", "postgres"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    database=os.getenv("POSTGRES_DB", "irrigation"),
)

engine = create_engine(database_url)

# Configuration Kafka
consumer = KafkaConsumer(
    "irrigation-measurements",
    bootstrap_servers=os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"
    ),
    value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    auto_offset_reset="latest",
    enable_auto_commit=False,
    group_id="irrigation-db-writer-v1",
)


def process_message(data):
    required_fields = [
        "schema_version",
        "device_id",
        "simulated",
        "sequence",
        "timestamp_utc",
        "soil_moisture_pct",
        "air_temperature_c",
        "relative_humidity_pct",
    ]

    if not all(field in data for field in required_fields):
        print("Message ignoré : champs manquants", flush=True)
        return

    if data["schema_version"] != 1:
        print("Message ignoré : version inconnue", flush=True)
        return

    timestamp = datetime.fromisoformat(
        data["timestamp_utc"].replace("Z", "+00:00")
    )

    with Session(engine) as session:
        sensor = session.scalar(
            select(Sensor).where(
                Sensor.device_id == data["device_id"]
            )
        )

        if sensor is None:
            print(
                f"Capteur inconnu : {data['device_id']}",
                flush=True,
            )
            return

        existing = session.scalar(
            select(Measurement).where(
                Measurement.sensor_id == sensor.id,
                Measurement.sequence == data["sequence"],
            )
        )

        if existing is not None:
            print(
                f"Mesure déjà enregistrée : séquence {data['sequence']}",
                flush=True,
            )
            return

        measurement = Measurement(
            sensor_id=sensor.id,
            timestamp_utc=timestamp,
            sequence=data["sequence"],
            schema_version=data["schema_version"],
            simulated=data["simulated"],
            soil_moisture_pct=data["soil_moisture_pct"],
            air_temperature_c=data["air_temperature_c"],
            relative_humidity_pct=data["relative_humidity_pct"],
        )

        session.add(measurement)
        session.commit()

        print(
            f"Mesure enregistrée : séquence {data['sequence']}",
            flush=True,
        )


if __name__ == "__main__":
    print("Consumer Kafka démarré. En attente de messages...", flush=True)

    try:
        for message in consumer:
            try:
                process_message(message.value)
                consumer.commit()
            except Exception as error:
                print(f"Erreur de traitement : {error}", flush=True)

    except KeyboardInterrupt:
        print("Arrêt du Consumer...", flush=True)

    finally:
        consumer.close()
        engine.dispose()
