from typing import Dict

NAME: str = "kinopoisk_spyder"

DB_OPTIONS: Dict[str, str] = {
    'dbname': 'postgres',
    'user': 'postgres',
    'host': '127.0.0.1',
    'port': '5432',
    'password': '123',
}
USE_PROXY=False
PROXIES = {
  'https': '81.200.82.240:8080',
}
