import sqlite3

def get_cursor(file):
    con = sqlite3.connect(file)
    return con.cursor()
