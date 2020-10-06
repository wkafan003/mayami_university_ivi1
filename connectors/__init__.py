import psycopg2
import psycopg2.extensions
import configurations.settings as setting

conn: psycopg2.extensions.connection
try:
    conn = psycopg2.connect(
        f"dbname='{setting.DB_OPTIONS['dbname']}' user='{setting.DB_OPTIONS['user']}' "
        f"host='{setting.DB_OPTIONS['host']}' password='{setting.DB_OPTIONS['password']}'")
except:
    print("I am unable to connect to the database")
    raise
