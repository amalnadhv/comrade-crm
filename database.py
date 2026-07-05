import sqlite3
import pandas as pd

DB_NAME = "crm.db"

# ---------------- INIT DB ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    add_assigned_column()
    # Customers table
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

    # Leads table (future module)
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
        remarks TEXT
    )
    """)

    conn.commit()
    conn.close()
    
# ---------------- QUOTATIONS ----------------
cur.execute("""
CREATE TABLE IF NOT EXISTS quotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    amount REAL,
    discount REAL,
    tax REAL,
    total REAL,
    status TEXT,
    created_on TEXT
)
""")
# ---------------- USERS ----------------
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

# Create default admin if not exists
cur.execute("SELECT * FROM users WHERE username='admin'")
if not cur.fetchone():
    cur.execute("""
        INSERT INTO users (username, password, role)
        VALUES ('admin', 'admin123', 'Admin')
    """)

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

cur.execute("SELECT * FROM users WHERE username='admin'")
if not cur.fetchone():
    cur.execute("""
        INSERT INTO users (username, password, role)
        VALUES ('admin', 'admin123', 'Admin')
    """)
    
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

def add_user(username, password, role="Sales"):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
    """, (username, password, role))

    conn.commit()
    conn.close()

# ---------------- LEADS (READY FOR NEXT STEP) ----------------
def add_lead(company, contact_person, phone, email, source, status, followup_date, remarks):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO leads 
        (company, contact_person, phone, email, source, status, followup_date, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (company, contact_person, phone, email, source, status, followup_date, remarks))

    conn.commit()
    conn.close()

# ---------------- USERS / AUTH ----------------
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
    
def init_followups_table():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

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

    conn.commit()
    conn.close()
    
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

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Customers
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

    # Leads
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
        remarks TEXT
    )
    """)

    # Followups
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

    conn.commit()
    conn.close()

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

def add_quotation(customer_name, amount, discount, tax, total, status, created_on):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO quotations
        (customer_name, amount, discount, tax, total, status, created_on)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (customer_name, amount, discount, tax, total, status, created_on))

    conn.commit()
    conn.close()

def get_quotations():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM quotations", conn)
    conn.close()
    return df

def validate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM users
        WHERE username=? AND password=?
    """, (username, password))

    user = cur.fetchone()
    conn.close()

    return user

def add_assigned_column():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    try:
        cur.execute("ALTER TABLE leads ADD COLUMN assigned_to TEXT")
    except:
        pass

    conn.commit()
    conn.close()

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
