import itertools
import re
from asyncio import Semaphore, as_completed
from typing import AsyncIterable, Literal

from bs4 import BeautifulSoup, Tag

from models.car import Car
from scrappers.scrapper import Scrapper

BASE_URL = 'https://www.deruedas.com.ar'
sem = Semaphore(2)

class Deruedas(Scrapper):
    def __init__(self, usd_rate: float) -> None:
        super().__init__(usd_rate)
        self.agency = "Deruedas"

    async def _run(self) -> AsyncIterable[Car | None]:
        brands = await self.get_brands()
        conditions = {"Nuevos", "Usados"}
        # 0 for cars, 1 for trucks
        segments = {0, 1}
        base_url = "https://www.deruedas.com.ar/busCraw.asp?segmento={segment}&marca={brand}&condicion={condition}&weNeed=divBusqueda&pag="
        # product from 3 sets combined
        combinations = itertools.product(segments, brands, conditions)
        urls = {
            base_url.format(segment=s, brand=b, condition=c) for s, b, c in combinations
        }
        pags = [self.paginate(url) for url in urls]
        for pag in as_completed(pags):
            page = await pag
            for car, page_soup in page:
                yield self.build_car(car, page_soup)

    async def get_brands(self) -> set[str]:
        res = await self.async_http.get("https://www.deruedas.com.ar/bus.asp")
        soup = BeautifulSoup(res.text, "html.parser")
        brand_anchors = soup.find_all("a", {"refreshparam": "marca"})
        return {a.text for a in brand_anchors}

    async def paginate(self, url: str) -> list[tuple[Tag, Tag]]:
        tuples = []
        page = 1
        while True:
            async with sem:
                res = await self.async_http.get(url + str(page))
            soup = BeautifulSoup(res.text, "html.parser")
            cars = soup.select("div[itemprop='item']")
            if not cars:
                break
            for car in cars:
                tuples.append((car, soup)) # entire soup for the images
            page += 1
        return tuples

    def build_car(self, car: Tag, page_soup: Tag) -> Car | None:
        mandatory_fields = {
            "id": self.get_attribute(car, 'sku'),
            "url": self.get_url(car),
            "region": self.get_attribute(car, 'address'),
            "km": self.get_km(car),
            "brand": self.get_brand(car),
            "model": self.get_attribute(car, 'model'),
            "full_name": self.get_attribute(car, 'name'),
            "ars_price": self.get_ars_price(car),
            "year": self.get_year(car)
        }
        if all(v is not None for v in mandatory_fields.values()):
            car_obj = Car(
                images=self.get_images(mandatory_fields['id'], page_soup),
                fuel=self.get_fuel(mandatory_fields["id"], page_soup),
                agency=self.agency,
                scrapping_dttm=self.scrapping_dttm,
                **mandatory_fields
            )
            return car_obj
        else:
            self.logger.info("Skipped car")

    def get_url(self, car: Tag) -> str | None:
        if url := car.select_one('link[itemprop="url"]'):
            return url.attrs.get('href')

    def get_km(self, car: Tag) -> int | None:
        if meta := car.select_one('meta[itemprop="mileageFromOdometer"]'):
            text = meta.attrs.get('content')
            #api hardcoded 1 to non specified km -> 750 cars, km optional? TODO
            return next((int(n) for n in re.findall(r"(\d*)", text) if n and n.isdigit() and n != '1'), None)

    def get_brand(self, car: Tag) -> str | None:
        if meta := car.select_one('div[itemprop="brand"] meta[itemprop="name"]'):
            return meta.attrs.get('content')

    def get_attribute(self, car: Tag, itemprop: Literal['model', 'name', 'address', 'sku']) -> str | None:
        if meta := car.select_one(f'meta[itemprop="{itemprop}"]'):
            return meta.attrs.get('content')

    def get_year(self, car: Tag) -> int | None:
        if meta := car.select_one('meta[itemprop="modelDate"]'):
            text = meta.attrs.get('content') or ''
            return int(text) if text.isdigit() else None

    def get_ars_price(self, car: Tag) -> float | None:
        if meta := car.select_one('meta[itemprop="priceCurrency"]'):
            if meta.attrs.get('content') == 'ARS' and (meta_price := car.select_one('meta[itemprop="price"]')):
                text =  meta_price.attrs.get("content")
                return float(text) if text and text.isdigit() else None

    def get_fuel(self, car_id: str, page_soup: Tag) -> str | None:
        if div := page_soup.find('div', {'id': re.compile(car_id)}):
            text = div.select_one('span.texto').text.replace('\xa0', '').strip().split('|')
            return text[0]

    def get_images(self, car_id: str, page_soup: Tag) -> list[str] | None:
        img = page_soup.find('img', {'src': re.compile(car_id)})
        if img and (src := img.get('src')):
            return [src]