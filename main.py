import argparse
import importlib

# Crear un parser de argumentos
parser = argparse.ArgumentParser(description="Gestor de scrappers para busqueda de autos nuevos y usados.")

# Agregar argumento para la ruta del archivo "scraper"
parser.add_argument("--s", "--scraper", metavar="path", help="Ruta del archivo scraper", required=True)

# Procesar los argumentos
args = parser.parse_args()
scrapper_path = f'scrappers.{args.s}'

module = importlib.import_module(scrapper_path)
