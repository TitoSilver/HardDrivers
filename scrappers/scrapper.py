from abc import ABC, abstractmethod
from datetime import datetime, UTC
from typing import Any, AsyncIterable
from logging import getLogger

from httpx import AsyncClient, Response

logger = getLogger(__name__)

class Scrapper(ABC):
    async_http: AsyncClient
    agency: str
    scrapped_items: set[str]
    scrapping_dttm: datetime

    def __init__(self) -> None:
        self.async_http = self._http_setup()
        self.scrapped_items = set()
        self.scrapping_dttm = datetime.now(UTC)

    @abstractmethod
    async def run(self) -> AsyncIterable[Any]:
        pass

    def _http_setup(self) -> AsyncClient:
        async def log_response(res: Response) -> Response:
            logger.info("[%s][%s][redirect: %s] %s", res.status_code, res.request.method, res.is_redirect, res.request.url)
            return res
        cli = AsyncClient(
            headers={
                "kavak-country-acronym": "ar",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            }
        )
        cli.event_hooks = {'response': [log_response]}
        return cli
