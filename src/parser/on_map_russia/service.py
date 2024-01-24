import asyncio
import aiohttp as aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from src.api.map.models import CityOrm, StreetOrm, RegionOrm
from src.database import get_async_session

ua = UserAgent()
header = {'User-Agent': str(ua.chrome)}


async def get_beautified_name_from_link(link):
    """
    Возвращает имя с заглвной буквы полученное из ссылки
    :param link: ссылка на обьект, содержащая его название
    :return: имя объекта с заглвной буквы
    """
    return str.title(link.split("/")[-2])


async def get_subject_links_list(subject_link, subject, time_sleep=1):
    """
    :param subject_link: ссылка на карту области/края. Материнская сущность с главной страницы сайта
    :param subject: слово, по которому происходит поиск в заголовках. Позволяет находить блок со списками городов/районов/улиц переданной области/края
    :return: список ссылок на города/районы/улицы в переданном области/крае. Если нет необходимого блока то вернет None
    """
    async with aiohttp.ClientSession(headers=header) as session:
        async with session.get(subject_link) as response:

            response = await response.text()
            soup = BeautifulSoup(response, 'lxml')
            try:
                subject_links = soup.find("h2", text=re.compile(fr'{subject}\s+(\w+)')).find_next_sibling().find_all("a")
            except Exception:
                return None

            subject_links = [link.get("href") for link in subject_links]

            # Проверяем, что последняя ссылка, не является ссылкой на полный список улиц
            # Если явлется, то получим полный список улиц
            if not re.search(".+\/улицы\/", subject_links[-1]):
                return subject_links

            street_link = "https://xn----7sbbuxpzq.xn--p1ai/" + subject_links[-1]

    async with aiohttp.ClientSession(headers=header) as session:
        async with session.get(street_link) as response:
            response = await response.text()
            soup = BeautifulSoup(response, 'lxml')
            pagination = soup.find("ul", class_="pagination").find_all("a")
            last_page = int(pagination[-1].contents[0]) + 1

            for page_number in range(1, last_page):
                street_page_link = street_link + f"страница-{page_number}/"

                async with session.get(street_page_link) as response:
                    await asyncio.sleep(time_sleep)
                    response = await response.text()
                    soup = BeautifulSoup(response, 'lxml')
                    streets = soup.find("ul", class_="pagination").find_previous_sibling().find_all("a")

                    subject_links.extend([street.get("href") for street in streets])

        return subject_links


async def get_regions():
    """
    :return: Ссылки на регионы
    """
    link = "https://xn----7sbbuxpzq.xn--p1ai/"

    async with aiohttp.ClientSession(headers=header) as session:
        async with session.get(link) as response:

            response = await response.text()
            soup = BeautifulSoup(response, 'lxml')
            map_links = soup.find("div", class_="row").find_all("a")
            map_links = ["https://xn----7sbbuxpzq.xn--p1ai/" + link.get("href") for link in map_links]

            return map_links


async def start_scraping(db_session=get_async_session, time_sleep=1):
    """
    Выполняет процесс парсинга и занесение информации в БД:
    Получает список ссылок на регионы.
    В цикле берет id региона из БД по имени.Если не нашел совпадений - заносит запись и возвращает id наверх
    Получает список всех городов региона, взятого в работу ранее.
    В цикле для каждого города берет его id из БД по имени.Если не нашел совпадений - заносит запись и возвращает id наверх
    Получет список всех улиц города, взятого в работу ранее. Заносит их в БД, используя insert ignore
    :param db_session: сессия БД
    :param time_sleep: время работы с
    :return:
    """
    regions_link_list = await get_regions()

    for region_link in regions_link_list:

        await asyncio.sleep(time_sleep)

        region_name = await get_beautified_name_from_link(region_link)

        async with db_session() as conn:
            region_id = await conn.execute(
                select(RegionOrm.id).select_from(RegionOrm).where(RegionOrm.name == region_name)
            )
            region_id = region_id.fetchone()
            region_id = region_id[0] if region_id is not None else await conn.execute(insert(RegionOrm).returning(RegionOrm.id).values(name=region_name))
            region_id = region_id if isinstance(region_id, int) is True else region_id.fetchone()[0]
            await conn.commit()

            city_link_list = await get_subject_links_list(subject_link=region_link, subject="Города", time_sleep=time_sleep)
            if city_link_list is None: continue

        async with db_session() as conn:
            for city_link in city_link_list:

                city_name = await get_beautified_name_from_link(city_link)

                city_id = await conn.execute(
                    select(CityOrm.id).select_from(CityOrm).where(CityOrm.name == city_name)
                )
                city_id = city_id.fetchone()
                city_id = city_id[0] if city_id is not None else await conn.execute(insert(CityOrm).returning(CityOrm.id).values(name=city_name, region_id=region_id))
                city_id = city_id if isinstance(city_id, int) is True else city_id.fetchone()[0]
                await conn.commit()

                street_link_list = await get_subject_links_list(subject_link="https://xn----7sbbuxpzq.xn--p1ai/" + city_link, subject="лицы", time_sleep=time_sleep)
                if street_link_list is None: continue

                for street_link in street_link_list:
                    insert_stmt = insert(StreetOrm).values(city_id=city_id, name=await get_beautified_name_from_link(street_link))
                    await conn.execute(insert_stmt.on_conflict_do_nothing(index_elements=['city_id', 'name']))

                await conn.commit()
