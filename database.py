import sqlite3

# Conexion con la base de datos
conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()

# Crear la tabla de usuarios si no existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT UNIQUE NOT NULL
)
""")

# Crear la tabla de mensajes si no existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
               timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

def add_user(username):
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user:
        return True # Si el usuario ya existe permitir acceso
    try:
        cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False    # Si el usuario ya existe

def save_message(username, message):
    cursor.execute("INSERT INTO messages (username, message) VALUES (?, ?)", (username, message))
    conn.commit()

def get_messages():
    cursor.execute("SELECT username, message FROM messages ORDER BY timestamp ASC")
    return cursor.fetchall()