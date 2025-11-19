#!/usr/bin/env python3
"""Check and add missing columns for the contacts table.

This script ensures the `address` column exists on the `contacts` table
in the SQLite database at `/nfs/demo.db`. It can be executed inside the
application pod (same as `data-gen.py`).
"""
import sqlite3

DATABASE = '/nfs/demo.db'


def connect_db():
    return sqlite3.connect(DATABASE)


def ensure_address_column():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(contacts);")
    cols = [row[1] for row in cur.fetchall()]
    if 'address' not in cols:
        cur.execute("ALTER TABLE contacts ADD COLUMN address TEXT;")
        conn.commit()
        print("Added 'address' column to contacts table.")
    else:
        print("'address' column already exists.")
    conn.close()


if __name__ == '__main__':
    ensure_address_column()
