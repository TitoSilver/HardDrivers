import hashlib
from datetime import datetime
from typing import Literal
from typing import List
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, PrimaryKeyConstraint, String, Integer, Column
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from models.base import Base

class CarImage(Base):
    __tablename__ = 'car_images'
    id = Column(Integer, primary_key=True, autoincrement=True)
    scrapping_dttm: Mapped[datetime]
    url = Column(String(400))
    car_id = Column(String(60), ForeignKey("cars.id"), index=True)

    def __init__(self, url: str, scrapping_dttm: datetime, car_id: str, agency: str) -> None:
        self.url = url
        self.scrapping_dttm = scrapping_dttm
        self.car_id = agency + car_id

class Car(Base):
    __tablename__  = 'cars'
    _id: Mapped[str] = mapped_column(String(60), primary_key=True, name='id')
    agency: Mapped[str] = mapped_column(String(30))
    url: Mapped[str] = mapped_column(String(400))
    images: Mapped[Optional[List[CarImage]]] = relationship("CarImage", cascade= 'all, delete')
    color: Mapped[Optional[str]] = mapped_column(String(30))
    transmission: Mapped[Optional[Literal["Manual", "Automatic"]]] = mapped_column(String(15))
    region: Mapped[str] = mapped_column(String(30))
    km: Mapped[int]
    brand: Mapped[str] = mapped_column(String(30))
    model: Mapped[str] = mapped_column(String(30))
    full_name: Mapped[str] = mapped_column(String(100))
    ars_price: Mapped[float]
    usd_price: Mapped[Optional[float]]

    def __init__(
        self,
        id: str,
        agency: str,
        url: str,
        region: str,
        km: int,
        brand: str,
        model: str,
        full_name: str,
        year: int,
        ars_price: float,
        scrapping_dttm: datetime,
        fuel: str | None= None,
        color: str | None=None,
        images: list[str] | None=None,
        transmission: Literal["Manual", "Automatic"] | None=None,
        usd_price: float | None=None,
    ) -> None:
        self.agency = agency
        self.id = id
        self.url = url
        self.images = [CarImage(img, scrapping_dttm, id, agency) for img in images or []]
        self.color = color
        self.transmission = transmission
        self.region = region
        self.km = km
        self.brand = brand
        self.model = model
        self.full_name = full_name
        self.year =  year
        self.fuel = fuel
        self.ars_price = ars_price
        self.usd_price = usd_price
        self.scrapping_dttm = scrapping_dttm

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id: str) -> None:
        self._id = hashlib.md5((self.agency + id).encode("utf-8")).hexdigest()
