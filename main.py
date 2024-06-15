import argparse
import enum
import importlib
from asyncio import run

from scrappers.scrapper import Scrapper
from utils.db import SessionDB
from utils.logging_handler import get_logger, setup_logger

root_logger = get_logger()
setup_logger(root_logger)

BATCH = 1000
# Crear un parser de argumentos
parser = argparse.ArgumentParser(
    description="Gestor de scrappers para busqueda de autos nuevos y usados."
)

# Agregar argumento para la ruta del archivo "scraper"
parser.add_argument(
    "--s", "--scraper", metavar="path", help="Ruta del archivo scraper", required=True
)

# Procesar los argumentos
args = parser.parse_args()
module = importlib.import_module(f"scrappers.{args.s}")

module_class = getattr(module, args.s.capitalize())
scrapper = module_class()

session_db = SessionDB()

async def main(scrapper: Scrapper):
    list_car = []
    count = 0
    async for  car in scrapper.run():
        if count == BATCH:
            session_db.save_all(list_car)
            list_car.clear()
            count = 0
            continue
        count += 1
        list_car.append(car)
    if list_car:
        session_db.save_all(list_car)

run(main(scrapper))
