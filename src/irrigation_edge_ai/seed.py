
import os

from sqlalchemy import create_engine, select
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session

from irrigation_edge_ai.models import Parcel, Sensor


def get_database_url():
    return URL.create(
        drivername="postgresql+psycopg",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.environ["POSTGRES_DB"],
    )


def main():
    engine = create_engine(get_database_url())

    with Session(engine) as session:
        # Créer une parcelle si elle n'existe pas
        parcel = session.scalar(
            select(Parcel).where(Parcel.name == "parcel-demo")
        )

        if parcel is None:
            parcel = Parcel(
                name="parcel-demo",
                region="Morocco",
                crop="Tomato",
                area_ha=1.0,
            )
            session.add(parcel)
            session.flush()

        # Créer un capteur si il n'existe pas
        sensor = session.scalar(
            select(Sensor).where(Sensor.device_id == "edge-sim-01")
        )

        if sensor is None:
            sensor = Sensor(
                device_id="edge-sim-01",
                parcel_id=parcel.id,
            )
            session.add(sensor)

        session.commit()

        print("Parcelle et capteur prêts !")
        print(f"Parcel ID: {parcel.id}")
        print(f"Sensor ID: {sensor.id}")

    engine.dispose()


if __name__ == "__main__":
    main()
