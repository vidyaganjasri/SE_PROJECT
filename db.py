import sqlite3

con = sqlite3.connect('database.db')
cur = con.cursor()
try:
    cur.execute("ALTER TABLE reports ADD COLUMN category TEXT DEFAULT ''")
    con.commit()
    print("Column added")
except sqlite3.OperationalError:
    print("Column already exists")
con.close()
