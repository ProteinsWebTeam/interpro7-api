import cx_Oracle

def get_cursor(host, port, name, user, password):
    dsn = cx_Oracle.makedsn(host, port, name)
    con = cx_Oracle.connect(user, password, dsn)
    return con.cursor()
