import sqlite3
import bcrypt

DB_NAME = "smart_home.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # чтобы обращаться к полям по имени
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    # пользователи
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'resident'
        )
    """)
    # комнаты
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    # устройства (и датчики)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            status TEXT DEFAULT 'off',
            room_id INTEGER,
            FOREIGN KEY (room_id) REFERENCES rooms(id)
        )
    """)
    # сценарии
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            trigger_device_id INTEGER,
            action_device_id INTEGER,
            action_command TEXT,
            delay_seconds INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (trigger_device_id) REFERENCES devices(id),
            FOREIGN KEY (action_device_id) REFERENCES devices(id)
        )
    """)
    # лог событий
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            device_id INTEGER,
            event_type TEXT,
            description TEXT,
            FOREIGN KEY (device_id) REFERENCES devices(id)
        )
    """)
    conn.commit()
    # Добавим тестового администратора, если нет
    try:
        hashed = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ("admin", hashed, "admin"))
        # Тестовые устройства
        cursor.execute("INSERT OR IGNORE INTO rooms (id, name) VALUES (1, 'Гостиная')")
        cursor.execute("INSERT OR IGNORE INTO devices (id, name, type, status, room_id) VALUES (1, 'Люстра', 'light', 'off', 1)")
        cursor.execute("INSERT OR IGNORE INTO devices (id, name, type, status, room_id) VALUES (2, 'Датчик движения', 'sensor', 'idle', 1)")
        conn.commit()
    except Exception as e:
        print("Init error:", e)
    finally:
        conn.close()