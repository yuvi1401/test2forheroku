database = "ssc"
user = None
password = None
host = None

dsn = "dbname=" + database
if (user):
    dsn += " user=" + user
if (password):
    dsn += " password=" + password
