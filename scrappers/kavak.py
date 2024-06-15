import re
import unicodedata
from asyncio import as_completed
from typing import AsyncIterable, Literal

from httpx import Response

from models.car import Car
from scrappers.scrapper import Scrapper


class Kavak(Scrapper):
    def __init__(self, usd_rate: float) -> None:
        super().__init__(usd_rate)
        self.agency = "Kavac"
        self.async_http.headers.update({"kavak-country-acronym": "ar"})

    async def _run(self) -> AsyncIterable[Car | None]:
        async for car in self.paginate_api():
            yield self.build_car(car)

    async def paginate_api(self) -> AsyncIterable[dict]:
        url = "https://www.kavak.com/api/advanced-search-api/v2/advanced-search?page={}&url=/"
        res = await self.async_http.get(url.format(1))
        first_page = res.json()
        routines = [
            self.async_http.get(url.format(page))
            for page in range(2, first_page["pagination"]["total"] + 1)
        ]
        for car in first_page.get("cars") or []:
            yield car
        for i, task in enumerate(as_completed(routines)):
            res: Response = await task
            self.logger.info("Page %s / %s", i + 1, first_page["pagination"]["total"])
            if res and (data := res.json()) and (cars := data.get("cars")):
                for car in cars:
                    yield car

    def build_car(self, car: dict) -> Car | None:
        mandatory_fields = {
            "id": car["id"],
            "url": car["url"].replace('https://', ''),
            "region": car["regionName"],
            "km": car["kmNoFormat"],
            "brand": car["make"],
            "model": car["model"],
            "full_name": car["name"],
            "ars_price": float(
                unicodedata.normalize("NFKD", car["price"]).replace('$', '').replace('.', '')
            ),
            "year": self.get_year(car)
        }
        if all(v is not None for v in mandatory_fields.values()):
            car_obj = Car(
                **mandatory_fields,
                agency=self.agency,
                images=(
                    [img] if (img := (car.get("image") or car.get("imageUrl"))) else None
                ),
                color=car.get("color"),
                transmission=self.get_transmission(car),
                scrapping_dttm=self.scrapping_dttm
            )
            return car_obj

    def get_transmission(self, car: dict) -> Literal["Manual", "Automatic"] | None:
        if tran := car.get("transmission"):
            return "Manual" if "man" in tran.lower() else "Automatic"

    def get_year(self, car: dict) -> int | None:
        if details := car.get("details"):
            results = re.findall(r"2\d{3}", details)
            return next((int(r) for r in results if r.isdigit()), None)
