import sqlite3

def create_connection():
    conn = sqlite3.connect('user_data.db')
    return conn

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            tron_address TEXT NOT NULL,
            usdt_balance REAL DEFAULT 0,
            busd_balance REAL DEFAULT 0
        );
    ''')
    conn.commit()

def save_user_address(user_id, address):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_id, tron_address) VALUES (?, ?)", (user_id, address))
    conn.commit()
    conn.close()

def get_user_address(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT tron_address FROM users WHERE user_id = ?", (user_id,))
    address = cursor.fetchone()
    conn.close()
    return address[0] if address else None


def get_balances(user_id: int) -> dict:
    # Query user's balances (USDT and BUSD) from your database
    balances = get_user_balances(user_id)
    
    # If user not found in the database, return balances as 0
    if not balances:
        return {'usdt': 0, 'busd': 0}
    
    return balances

def get_user_balances(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT usdt_balance, busd_balance FROM users WHERE user_id = ?", (user_id,))
    balances = cursor.fetchone()
    conn.close()
    return {'usdt': balances[0], 'busd': balances[1]} if balances else None

def update_user_balance(user_id, currency, new_balance):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET {currency}_balance = ? WHERE user_id = ?", (new_balance, user_id))
    conn.commit()
    conn.close()


conn = create_connection()
create_tables(conn)
