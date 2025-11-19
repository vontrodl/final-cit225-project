import sqlite3
import os

DATABASE = '/nfs/demo.db'

def connect_db():
    """Connect to the SQLite database."""
    return sqlite3.connect(DATABASE)

def generate_test_data(num_contacts):
    """Generate test data for the contacts table."""
    db = connect_db()
    cur = db.cursor()
    cur.execute("PRAGMA table_info(contacts);")
    cols = [row[1] for row in cur.fetchall()]
    if 'address' not in cols:
        cur.execute("ALTER TABLE contacts ADD COLUMN address TEXT;")
    for i in range(num_contacts):
        name = f'Test Name {i}'
        phone = f'123-456-789{i}'
        address = f'{i} myPlace'
        db.execute('INSERT INTO contacts (name, phone, address) VALUES (?, ?, ?)', (name, phone, address))
    db.commit()
    print(f'{num_contacts} test contacts added to the database.')
    db.close()

if __name__ == '__main__':
    generate_test_data(10)  # Generate 10 test contacts.
