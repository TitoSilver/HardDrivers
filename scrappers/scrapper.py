from abc import ABC, abstractmethod
from datetime import datetime, UTC
from typing import AsyncIterable
from logging import getLogger

from httpx import AsyncClient, Response

from models.car import Car

logger = getLogger(__name__)
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

class Scrapper(ABC):
    async_http: AsyncClient
    agency: str
    scrapped_items: set[str]
    scrapping_dttm: datetime

    def __init__(self) -> None:
        self.async_http = self._http_setup()
        self.scrapped_items = set()
        self.scrapping_dttm = datetime.now(UTC)

    async def run(self) -> AsyncIterable[Car]:
        async for car in self._run():
            if car.id in self.scrapped_items:
                logger.info("%sCar %s %s repeated%s", RED, car.full_name, car.full_name, RESET)
                continue
            self.scrapped_items.add(car.id)
            logger.info("%s[%s cars]: %s %s", GREEN, len(self.scrapped_items), car.full_name, RESET)
            yield car

    @abstractmethod
    async def _run(self) -> AsyncIterable[Car]:
        pass

    def _http_setup(self) -> AsyncClient:
        async def log_response(res: Response) -> Response:
            logger.info("[%s][%s][redirect: %s] %s", res.status_code, res.request.method, res.is_redirect, res.request.url)
            return res
        cli = AsyncClient(
            headers={
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            }
        )
        cli.event_hooks = {'response': [log_response]}
        return cli
