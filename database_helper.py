import sqlite3

from flask import g

DATABASE = 'data.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def create_db():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    cursor.execute('''
       CREATE TABLE  IF NOT EXISTS films (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    description TEXT,
    annee INTEGER,
    realisation TEXT,
    producteur TEXT,
    image TEXT,
    acteurs TEXT
);

    ''')

    conn.close()


create_db()
