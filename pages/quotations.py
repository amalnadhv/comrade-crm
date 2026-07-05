import json
import sqlite3

DB_NAME = "crm.db"


# ================= QUOTATIONS =================
def add_quotation(customer_name, items, subtotal, discount, tax, total, status, created_on, version):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # create table if not exists
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

    cur = conn.cursor()
    cur.execute("SELECT * FROM quotations ORDER BY id DESC")
    rows = cur.fetchall()

    conn.close()

    # convert to DataFrame-friendly format
    import pandas as pd

    return pd.DataFrame(rows, columns=[
        "id",
        "customer_name",
        "items",
        "subtotal",
        "discount",
        "tax",
        "total",
        "status",
        "created_on",
        "version"
    ])
