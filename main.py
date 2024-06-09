import argparse
import importlib
from asyncio import run

from scrappers.scrapper import Scrapper

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


async def main(scrapper: Scrapper):
    async for car in scrapper.run():
        break # aca guardar en db


run(main(scrapper))
