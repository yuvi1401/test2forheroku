import psycopg2
from dbconfig_prod import user, password, database, host

try:
    connection = psycopg2.connect(
    user=user,
    password=password,
    database=database,
    host=host)

    cursor = connection.cursor()

except:
    connection = None
    cursor = None
