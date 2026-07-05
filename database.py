import sqlite3
import pandas as pd
    
DB_NAME = "crm.db"

# ---------------- INIT DB ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

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

    # ---------------- QUOTATIONS ----------------
      # DROP OLD TABLE (important for fix)
    cur.execute("DROP TABLE IF EXISTS quotations")

    # CREATE NEW TABLE
    cur.execute("""
    CREATE TABLE quotations (
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

    cur.execute("PRAGMA table_info(quotations)")
    columns = [col[1] for col in cur.fetchall()]

    if "items" not in columns:
        cur.execute("ALTER TABLE quotations ADD COLUMN items TEXT")

    conn.commit()
    conn.close()
    
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

    conn.commit()
    conn.close()


# ---------------- CUSTOMERS ----------------
def add_customer(name, phone, email, company, status):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO customers (name, phone, email, company, status)
        VALUES (?, ?, ?, ?, ?)
    """, (name, phone, email, company, status))

    conn.commit()
    conn.close()


def get_customers():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT * FROM customers")
    rows = cur.fetchall()

    conn.close()
    return rows


def update_customer(customer_id, name, phone, email, company, status):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        UPDATE customers
        SET name=?, phone=?, email=?, company=?, status=?
        WHERE id=?
    """, (name, phone, email, company, status, customer_id))

    conn.commit()
    conn.close()


def delete_customer(customer_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("DELETE FROM customers WHERE id=?", (customer_id,))
    conn.commit()
    conn.close()


# ---------------- USERS ----------------
def add_user(username, password, role="Sales"):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
    """, (username, password, role))

    conn.commit()
    conn.close()


def validate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, username, role FROM users
        WHERE username=? AND password=?
    """, (username, password))

    user = cur.fetchone()
    conn.close()
    return user


# ---------------- LEADS ----------------
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


def get_leads():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM leads", conn)
    conn.close()
    return df


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
def add_followup(lead_id, title, followup_date, status, remarks):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO followups (lead_id, title, followup_date, status, remarks)
        VALUES (?, ?, ?, ?, ?)
    """, (lead_id, title, followup_date, status, remarks))

    conn.commit()
    conn.close()


def get_followups():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM followups", conn)
    conn.close()
    return df


# ---------------- QUOTATIONS ----------------
def add_quotation(customer_name, items, subtotal, discount, tax, total, status, created_on, version):
    import json
    import sqlite3

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

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

    cur.execute("""
        INSERT INTO quotations (
            customer_name, items, subtotal, discount, tax,
            total, status, created_on, version
        )
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
    df = pd.read_sql_query("SELECT * FROM quotations ORDER BY id DESC", conn)
    conn.close()
    return df
    
# ---------------- MIGRATION HELPERS ----------------
def add_assigned_column():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    try:
        cur.execute("ALTER TABLE leads ADD COLUMN assigned_to TEXT")
    except:
        pass

    conn.commit()
    conn.close()

def delete_lead(lead_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("DELETE FROM leads WHERE id=?", (lead_id,))

    conn.commit()
    conn.close()

def delete_followup(followup_id):
    import sqlite3

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("DELETE FROM followups WHERE id=?", (followup_id,))

    conn.commit()
    conn.close()

def delete_followup(followup_id):
    import sqlite3

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("DELETE FROM followups WHERE id=?", (followup_id,))

    conn.commit()
    conn.close()

def update_followup(followup_id, lead_id, title, followup_date, status, remarks):
    import sqlite3

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        UPDATE followups
        SET lead_id=?, title=?, followup_date=?, status=?, remarks=?
        WHERE id=?
    """, (lead_id, title, followup_date, status, remarks, followup_id))

    conn.commit()
    conn.close()


def get_customers():
    import sqlite3
    import pandas as pd

    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query(
        "SELECT * FROM customers",
        conn
    )

    conn.close()
    return df
