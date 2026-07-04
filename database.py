import sqlite3

DB_NAME = "crm.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT,
        company TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_customer(name, phone, email, company, status):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO customers (name, phone, email, company, status)
        VALUES (?, ?, ?, ?, ?)
    """, (name, phone, email, company, status))

    conn.commit()
    conn.close()


def get_customers():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM customers")
    rows = cur.fetchall()

    conn.close()
    return rows


def delete_customer(id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM customers WHERE id=?", (id,))

    conn.commit()
    conn.close()


def update_customer(id, name, phone, email, company, status):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE customers
        SET name=?, phone=?, email=?, company=?, status=?
        WHERE id=?
    """, (name, phone, email, company, status, id))

    conn.commit()
    conn.close()
