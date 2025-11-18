import re
import main


def setup_db(db_path):
    # point main to a temporary DB file and initialize schema
    main.DATABASE = db_path
    main.init_db()
    db = main.get_db()
    db.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)", ("Alice", "555"))
    db.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)", ("Bob", "111"))
    db.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)", ("Charlie", "999"))
    db.commit()
    db.close()


def test_sort_by_name_asc(tmp_path):
    dbfile = str(tmp_path / "test.db")
    setup_db(dbfile)
    client = main.app.test_client()
    resp = client.get('/?sort=name&dir=asc')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    names = re.findall(r'<td class="name">([^<]+)</td>', html)
    assert names == ["Alice", "Bob", "Charlie"]


def test_sort_by_phone_desc(tmp_path):
    dbfile = str(tmp_path / "test2.db")
    setup_db(dbfile)
    client = main.app.test_client()
    resp = client.get('/?sort=phone&dir=desc')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    phones = re.findall(r'<td class="phone[^>]*>([^<]+)</td>', html)
    assert phones == ["999", "555", "111"]


def test_invalid_sort_defaults_to_id_desc(tmp_path):
    dbfile = str(tmp_path / "test3.db")
    setup_db(dbfile)
    client = main.app.test_client()
    resp = client.get('/?sort=unknown&dir=bad')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    ids = re.findall(r'<td class="id text-secondary">([^<]+)</td>', html)
    assert ids == ["3", "2", "1"]
