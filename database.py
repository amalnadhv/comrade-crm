import sqlite3
import pandas as pd
import json

DB_NAME = "crm.db"

# ---------------- INIT DB ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # ---------------- USERS ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # default admin
    cur.execute("SELECT * FROM users WHERE username='admin'")
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO users (username, password, role)
            VALUES ('admin', 'admin123', 'Admin')
        """)

    # ---------------- CUSTOMERS ----------------
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

    # ---------------- LEADS ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        contact_person TEXT,
        phone TEXT,
        email TEXT,
        source TEXT,
        status TEXT,
        followup_date TEXT,
        remarks TEXT,
        assigned_to TEXT
    )
    """)

    # ---------------- FOLLOWUPS ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS followups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER,
        title TEXT,
        followup_date TEXT,
        status TEXT,
        remarks TEXT
    )
    """)

    # ---------------- QUOTATIONS (FINAL STRUCTURE) ----------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS quotations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        items TEXT,
        subtotal REAL,
        discount REAL,
        tax REAL,
        total REAL,
        status TEXT,
        created_on TEXT,
        version TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------- CUSTOMERS ----------------
def get_customers():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM customers", conn)
    conn.close()
    return df


def add_customer(name, phone, email, company, status):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO customers (name, phone, email, company, status)
        VALUES (?, ?, ?, ?, ?)
    """, (name, phone, email, company, status))

    conn.commit()
    conn.close()


# ---------------- LEADS ----------------
def get_leads():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM leads", conn)
    conn.close()
    return df


def add_lead(company, contact_person, phone, email, source, status, followup_date, remarks, assigned_to):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO leads 
        (company, contact_person, phone, email, source, status, followup_date, remarks, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (company, contact_person, phone, email, source, status, followup_date, remarks, assigned_to))

    conn.commit()
    conn.close()


def delete_lead(lead_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("DELETE FROM leads WHERE id=?", (lead_id,))

    conn.commit()
    conn.close()


def convert_lead_to_customer(name, phone, email, company, status="New"):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO customers (name, phone, email, company, status)
        VALUES (?, ?, ?, ?, ?)
    """, (name, phone, email, company, status))

    conn.commit()
    conn.close()


# ---------------- FOLLOWUPS ----------------
def get_followups():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM followups", conn)
    conn.close()
    return df


def add_followup(lead_id, title, followup_date, status, remarks):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO followups (lead_id, title, followup_date, status, remarks)
        VALUES (?, ?, ?, ?, ?)
    """, (lead_id, title, followup_date, status, remarks))

    conn.commit()
    conn.close()


def update_followup(followup_id, lead_id, title, followup_date, status, remarks):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        UPDATE followups
        SET lead_id=?, title=?, followup_date=?, status=?, remarks=?
        WHERE id=?
    """, (lead_id, title, followup_date, status, remarks, followup_id))

    conn.commit()
    conn.close()


def delete_followup(followup_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("DELETE FROM followups WHERE id=?", (followup_id,))

    conn.commit()
    conn.close()


# ---------------- QUOTATIONS ----------------
def add_quotation(customer_name, items, subtotal, discount, tax, total, status, created_on, version):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO quotations
        (customer_name, items, subtotal, discount, tax, total, status, created_on, version)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        customer_name,
        json.dumps(items),
        subtotal,
        discount,
        tax,
        total,
        status,
        created_on,
        version
    ))

    conn.commit()
    conn.close()


def get_quotations():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM quotations", conn)
    conn.close()
    return df
