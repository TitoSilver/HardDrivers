import unicodedata
from asyncio import as_completed
from typing import AsyncIterable, Literal

from httpx import Response

from models.car import Car
from scrappers.scrapper import Scrapper


class Kavak(Scrapper):
    def __init__(self) -> None:
        super().__init__()
        self.agency = "Kavac"
        self.async_http.headers.update({"kavak-country-acronym": "ar"})

    async def _run(self) -> AsyncIterable[Car]:
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

    def build_car(self, car: dict) -> Car:
        car_obj = Car(
            id=car["id"],
            agency=self.agency,
            url=car["url"],
            images=(
                [img] if (img := (car.get("image") or car.get("imageUrl"))) else None
            ),
            color=car.get("color"),
            transmission=self.get_transmission(car),
            region=car["regionName"],
            km=car["kmNoFormat"],
            brand=car["make"],
            model=car["model"],
            full_name=car["name"],
            ars_price=float(
                unicodedata.normalize("NFKD", car["price"]).replace('$', '').replace('.', '')
            ),
            scrapping_dttm=self.scrapping_dttm
        )
        return car_obj

    def get_transmission(self, car: dict) -> Literal["Manual", "Automatic"] | None:
        if tran := car.get("transmission"):
            return "Manual" if "man" in tran.lower() else "Automatic"
