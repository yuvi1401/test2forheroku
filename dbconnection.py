import psycopg2
import urllib.parse as urlparse
import os
from dbconfig import user, password, database, host

try:
    if 'DATABASE_URL' in os.environ:
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port

        connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )

    else:
        connection = psycopg2.connect(
            user=user,
            password=password,
            database=database,
            host=host)

    cursor = connection.cursor()

except:
    connection = None
    cursor = None
