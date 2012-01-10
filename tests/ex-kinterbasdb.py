import kinterbasdb

# The server is named 'bison'; the database file is at '/temp/test.db'.
con = kinterbasdb.connect(dsn='bison:/temp/test.db', user='sysdba', password='pass')

# Or, equivalently:
con = kinterbasdb.connect(
    host='bison', database='/temp/test.db',
    user='sysdba', password='pass')
