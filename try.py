import sqlite3


conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT,
    password TEXT
)
''')

conn.commit()
conn.close()