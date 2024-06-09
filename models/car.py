import hashlib
from typing import Literal


class Car:
    _id: str
    agency: str
    url: str
    images: list[str] | None
    color: str | None
    transmission: Literal["Manual", "Automatic"] | None
    region: str
    km: int
    brand: str
    model: str
    full_name: str
    ars_price: float
    usd_price: float | None

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
        ars_price: float,
        color: str | None=None,
        images: list[str] | None=None,
        transmission: Literal["Manual", "Automatic"] | None=None,
        usd_price: float | None=None,
    ) -> None:
        self.agency = agency
        self.id = id
        self.url = url
        self.images = images
        self.color = color
        self.transmission = transmission
        self.region = region
        self.km = km
        self.brand = brand
        self.model = model
        self.full_name = full_name
        self.ars_price = ars_price
        self.usd_price = usd_price

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id: str) -> None:
        self._id = hashlib.md5((self.agency + id).encode("utf-8")).hexdigest()
