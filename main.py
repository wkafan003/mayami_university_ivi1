import pickle
import time
from typing import List, Dict
import re
import requests
from lxml import html
import connectors as conn
from connectors.db import insert_film
import utils.logger as logger
import configurations.settings as settings
import logging
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem


def get_film_data(s: requests.sessions.Session, film_id: str, delay: float = 0, proxy: Dict = None) -> Dict:
    film_data = {}
    film_link = f'https://www.kinopoisk.ru/film/{film_id}/'
    page = s.get(film_link, proxies=proxy)

    tree = html.fromstring(page.text)
    title = tree.xpath("//span[@class='styles_title__2l0HH']")[0].text

    # info = tree.xpath('//*[@id="__next"]/div/div[2]/div[1]/div[2]/div/div[3]/div/div/div[2]/div[1]/div')[0]
    info = tree.xpath('.//h3[text()="О фильме"]')[0].find('..')[1]

    release_date = info[0][1][0].text
    country = info[1][1][0].text
    box_office = info[13][1][0].text
    buf = box_office.find('=')
    box_office = ''.join(box_office[buf + 3:].split())

    film_data['title'] = title
    film_data['release_date'] = release_date
    film_data['country'] = country
    film_data['box_office'] = box_office

    time.sleep(delay)
    logging.info(f'Информация о фильме {title} загружена')
    actors_link = film_link + 'cast/'
    page = s.get(actors_link, proxies=proxy)
    tree = html.fromstring(page.text)

    actors = []
    z = tree.xpath('//*[@id="block_left"]/div')[0]
    current_type = ''
    for i in range(len(z)):
        name = z[i].attrib.get('name', None)
        if name is not None:
            current_type = name
        cls = z[i].attrib.get('class', None)
        if cls is not None and 'dub' in cls:
            fio = z[i].find_class('name')[0][0].text
            actors.append([fio, current_type])
    film_data['actors'] = actors
    logging.info(f'Информация об актерах фильма {title} загружена')
    return film_data


def get_films_list(s: requests.sessions.Session, link: str) -> List[str]:
    pass


def main():
    delay = 15
    logger.init_logger(f'logs/{settings.NAME}.log')
    s = requests.Session()
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]

    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
    # user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 ' \
    #              'Safari/537.36 '
    user_agent = user_agent_rotator.get_random_user_agent()
    s.headers.update({
        'User-Agent': user_agent
    })
    proxy = settings.PROXIES if settings.USE_PROXY else None
    try:
        with open('assets/cookie', 'rb') as f:
            s.cookies.update(pickle.load(f))
    except Exception as e:
        logging.warning(str(e))

    films = []
    r = re.compile('\d+')
    page_num = 1
    while True:

        page = s.get(f'https://www.kinopoisk.ru/popular/films/2018/?page={page_num}&quick_filters=films&tab=all',
                     proxies=proxy)
        tree = html.fromstring(page.text)
        films_buf = [r.findall(film.attrib['href'])[0] for film in tree.find_class('selection-film-item-meta__link')]
        logging.debug(f'Добавлено {len(films_buf)} фильмов')
        if len(films_buf) == 0:
            break
        films.extend(films_buf)
        page_num += 1
        time.sleep(delay)

    for i in range(len(films)):
        try:
            data = get_film_data(s, films[i], delay, proxy)
            insert_film(conn.conn, data)
            logging.debug(f'Фильм {data["title"]} обработан  {i}/{len(films)} ')
        except:
            logging.debug(f'Фильм не обработан, ошибка! {i}/{len(films)} ')

        time.sleep(delay)
    with open('assets/cookie', 'wb') as f:
        pickle.dump(s.cookies, f)


if __name__ == '__main__':
    main()
