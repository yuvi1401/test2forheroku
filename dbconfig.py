database = "ssc"
user = None
password = None

dsn = "dbname=" + database
if (user):
    dsn += " user=" + user
if (password):
    dsn += " password=" + password
