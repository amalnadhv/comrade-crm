import sqlite3

DB_NAME = "crm.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Customers table
    c.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT,
        company TEXT,
        status TEXT
    )
    """)

    # USERS TABLE (PUT IT HERE)
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        subscription_status TEXT DEFAULT 'inactive'
    )
    """)

    conn.commit()
    conn.close()

def add_customer(name, phone, email, company, status):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO customers (name, phone, email, company, status)
        VALUES (?, ?, ?, ?, ?)
    """, (name, phone, email, company, status))

    conn.commit()
    conn.close()


def get_customers():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM customers")
    rows = c.fetchall()

    conn.close()
    return rows


def delete_customer(customer_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM customers WHERE id=?", (customer_id,))
    conn.commit()
    conn.close()


def update_customer(id, name, phone, email, company, status):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        UPDATE customers
        SET name=?, phone=?, email=?, company=?, status=?
        WHERE id=?
    """, (name, phone, email, company, status, id))

    conn.commit()
    conn.close()
