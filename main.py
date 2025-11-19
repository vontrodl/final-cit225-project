from flask import Flask, request, render_template, redirect, url_for, flash
import sqlite3
import os
import math

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

DATABASE = os.environ.get('DATABASE', '/nfs/demo.db')
PER_PAGE_DEFAULT = 10

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL
            );
        ''')
        db.commit()
        db.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'delete':
            contact_id = request.form.get('contact_id')
            if contact_id:
                db = get_db()
                db.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
                db.commit(); db.close()
                flash('Contact deleted successfully.', 'success')
            else:
                flash('Missing contact id.', 'danger')
            return redirect(url_for('index'))

        if action == 'update':
            contact_id = request.form.get('contact_id')
            name = request.form.get('name')
            phone = request.form.get('phone')
            address = request.form.get('address')
            if contact_id and name and phone:
                db = get_db()
                db.execute('UPDATE contacts SET name=?, phone=?, address=? WHERE id=?', (name, phone, address, contact_id))
                db.commit(); db.close()
                flash('Contact updated.', 'success')
            else:
                flash('Missing fields for update.', 'danger')
            return redirect(url_for('index'))

        # default → add
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        if name and phone:
            db = get_db()
            db.execute('INSERT INTO contacts (name, phone, address) VALUES (?, ?, ?)', (name, phone, address))
            db.commit(); db.close()
            flash('Contact added successfully.', 'success')
        else:
            flash('Missing name or phone number.', 'danger')
        return redirect(url_for('index'))

    # GET: pagination
    try:
        page = max(int(request.args.get('page', 1)), 1)
    except ValueError:
        page = 1
    try:
        per_page = max(int(request.args.get('per', PER_PAGE_DEFAULT)), 1)
    except ValueError:
        per_page = PER_PAGE_DEFAULT
    offset = (page - 1) * per_page

    # Sorting support (by id, name, phone) and direction (asc, desc)
    sort = request.args.get('sort', 'id')
    direction = request.args.get('dir', 'desc')
    allowed = {'id': 'id', 'name': 'name', 'phone': 'phone', 'address':'address'}
    if sort not in allowed:
        sort = 'id'
    if direction not in ('asc', 'desc'):
        direction = 'desc'

    db = get_db()
    total = db.execute('SELECT COUNT(*) FROM contacts').fetchone()[0]
    order_clause = f"{allowed[sort]} {direction.upper()}"
    # Safe: column is validated against `allowed` map and direction limited to asc/desc
    query = f'SELECT * FROM contacts ORDER BY {order_clause} LIMIT ? OFFSET ?'
    contacts = db.execute(query, (per_page, offset)).fetchall()
    db.close()

    pages = max(1, math.ceil(total / per_page))
    has_prev = page > 1
    has_next = page < pages
    start_page = max(1, page - 2)
    end_page = min(pages, page + 2)

    return render_template(
        'index.html',
        contacts=contacts,
        page=page, pages=pages, per_page=per_page,
        has_prev=has_prev, has_next=has_next, total=total,
        start_page=start_page, end_page=end_page
        , sort=sort, dir=direction
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    init_db()
    app.run(debug=True, host='0.0.0.0', port=port)
