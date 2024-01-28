import asyncio

from src.parser.on_map_russia.service import start_scraping


if __name__ == '__main__':
    asyncio.run(start_scraping())