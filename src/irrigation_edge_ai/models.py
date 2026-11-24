
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# Classe de base commune à tous les modèles
class Base(DeclarativeBase):
    pass


# 1. Informations sur les parcelles agricoles
class Parcel(Base):
    __tablename__ = "parcels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    region: Mapped[str | None] = mapped_column(String(100))
    crop: Mapped[str | None] = mapped_column(String(100))
    area_ha: Mapped[float | None] = mapped_column(Float)

    sensors: Mapped[list["Sensor"]] = relationship(back_populates="parcel")


# 2. Capteurs associés aux parcelles
class Sensor(Base):
    __tablename__ = "sensors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    parcel_id: Mapped[int] = mapped_column(
        ForeignKey("parcels.id"),
        nullable=False,
    )

    parcel: Mapped["Parcel"] = relationship(back_populates="sensors")
    measurements: Mapped[list["Measurement"]] = relationship(
        back_populates="sensor"
    )


# 3. Mesures envoyées par les capteurs
class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sensor_id: Mapped[int] = mapped_column(
        ForeignKey("sensors.id"),
        nullable=False,
    )

    timestamp_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    simulated: Mapped[bool] = mapped_column(Boolean, nullable=False)

    soil_moisture_pct: Mapped[float] = mapped_column(Float, nullable=False)
    air_temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    relative_humidity_pct: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    sensor: Mapped["Sensor"] = relationship(back_populates="measurements")
