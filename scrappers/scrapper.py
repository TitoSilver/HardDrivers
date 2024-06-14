from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import AsyncIterable

from colorama import Fore, Style
from httpx import AsyncClient, Response, AsyncHTTPTransport

from models.car import Car
from utils.logging_handler import get_logger


class Scrapper(ABC):
    async_http: AsyncClient
    agency: str
    scrapped_items: set[str]
    scrapping_dttm: datetime

    def __init__(self) -> None:
        self.async_http = self._http_setup()
        self.scrapped_items = set()
        self.scrapping_dttm = datetime.now(UTC)
        self.logger = self._logger_setup()

    async def run(self) -> AsyncIterable[Car]:
        async for car in self._run():
            if not car:
                self.logger.info("%sSkipped None%s", Fore.RED, Fore.RESET)
                continue
            elif car.id in self.scrapped_items:
                self.logger.info("%sCar %s %s repeated%s", Fore.RED, car.full_name, car.full_name, Style.RESET_ALL)
                continue
            self.scrapped_items.add(car.id)
            self.logger.info("%s[%s cars]: %s %s", Fore.GREEN, len(self.scrapped_items), car.full_name, Style.RESET_ALL)
            yield car

    @abstractmethod
    async def _run(self) -> AsyncIterable[Car | None]:
        pass

    def _http_setup(self) -> AsyncClient:
        async def log_response(res: Response) -> Response:
            self.logger.info("[%s][%s][redirect: %s] %s", res.status_code, res.request.method, res.is_redirect, res.request.url)
            return res
        cli = AsyncClient(
            headers={
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            },
            timeout=20,
            event_hooks={'response': [log_response]},
            transport=AsyncHTTPTransport(retries=6)
        )
        return cli

    @classmethod
    def _logger_setup(cls):
        logger = get_logger(cls.__name__)
        return logger