from typing import Dict
import psycopg2
import psycopg2.extensions
import connectors

import json


conn: psycopg2.extensions.connection = connectors.conn


def insert_film(conn: psycopg2.extensions.connection, data: Dict):
    cur: psycopg2.extensions.cursor = conn.cursor()
    film_id: str
    country_id: str

    cur.execute("select id from countries where name=%s", (data['country'],))
    country_id = cur.fetchone()
    if country_id is None:
        cur.execute("insert into countries (name) values (%s) returning id", (data['country'],))
        country_id = cur.fetchone()
    cur.connection.commit()

    cur.execute("select id from films where title=%s and country=%s and release_date=%s",
                (data['title'], country_id, data['release_date']))
    film_id = cur.fetchone()
    if film_id is None:
        cur.execute("insert into films (title, country, box_office, release_date) values (%s,%s,%s,%s) returning id",
                    (data['title'], country_id, data['box_office'], data['release_date']))
        film_id = cur.fetchone()

    type_id: str
    person_id: str
    person2content_exist: bool

    for i in data['actors']:
        cur.execute("select id from person_types where type=%s", (i[1],))
        type_id = cur.fetchone()
        if type_id is None:
            cur.execute("insert into person_types (type) values (%s) returning id", (i[1],))
            type_id = cur.fetchone()
        cur.connection.commit()

        cur.execute("select id from persons where fio=%s", (i[0],))
        person_id = cur.fetchone()
        if person_id is None:
            cur.execute("insert into persons (fio) values (%s) returning id", (i[0],))
            person_id = cur.fetchone()
        cur.connection.commit()

        cur.execute("select count(*) from persons2content where person_id=%s and film_id=%s and person_type=%s",
                    (person_id, film_id, type_id))
        person2content_exist = cur.fetchone()[0] > 0
        if not person2content_exist:
            cur.execute("insert into persons2content (person_id, film_id, person_type)  values (%s,%s,%s)",
                        (person_id, film_id, type_id))
        cur.connection.commit()

    cur.connection.commit()
    cur.close()


