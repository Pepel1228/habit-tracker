import os
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "habits.db"


# ---------- ПОДКЛЮЧЕНИЕ ----------
def get_connection():
    """Создаёт подключение к SQLite, если базы нет — создаёт файл"""
    try:
        # если базы нет — создаём пустой файл
        if not os.path.exists(DB_PATH):
            open(DB_PATH, "w").close()
            print(f"📁 Создан новый файл базы данных: {DB_PATH}")

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # fetch возвращает dict-подобные строки
        return conn
    except Exception as e:
        print(f"❌ Ошибка подключения к SQLite: {e}")
        return None


# ---------- ИНИЦИАЛИЗАЦИЯ ----------
def init_db():
    conn = get_connection()
    if conn is None:
        print("❌ Не удалось подключиться к SQLite")
        return False

    cur = conn.cursor()
    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            goal TEXT,
            repeat TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS habit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER REFERENCES habits(id) ON DELETE CASCADE,
            date TEXT NOT NULL DEFAULT (date('now')),
            created_at TEXT DEFAULT (datetime('now'))
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER UNIQUE REFERENCES habits(id) ON DELETE CASCADE,
            time TEXT,
            repeat TEXT,
            days TEXT,
            vibration INTEGER,
            sound INTEGER,
            text TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dark_theme INTEGER,
            primary_color TEXT
        )
        """)

        conn.commit()
        print("✅ SQLite инициализирована и готова к работе")
        return True

    except Exception as e:
        print(f"❌ Ошибка при инициализации БД: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


# ---------- CRUD HABITS ----------
def add_habit(name, goal=None, repeat=None):
    conn = get_connection()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO habits (name, goal, repeat) VALUES (?, ?, ?)",
            (name, goal, repeat)
        )
        habit_id = cur.lastrowid
        conn.commit()
        return habit_id
    except Exception as e:
        print(f"❌ Ошибка добавления привычки: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()


def get_habits():
    conn = get_connection()
    if conn is None:
        return []
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM habits ORDER BY created_at DESC")
        return [dict(row) for row in cur.fetchall()]
    except Exception as e:
        print(f"❌ Ошибка получения привычек: {e}")
        return []
    finally:
        cur.close()
        conn.close()


def delete_habit(habit_id):
    conn = get_connection()
    if conn is None:
        return
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM habits WHERE id=?", (habit_id,))
        conn.commit()
    except Exception as e:
        print(f"❌ Ошибка удаления привычки: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


# ---------- CRUD HABIT LOGS ----------
def log_habit_done(habit_id, date=None):
    if date is None:
        date = datetime.today().strftime('%Y-%m-%d')
    conn = get_connection()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO habit_logs (habit_id, date) VALUES (?, ?)",
            (habit_id, date)
        )
        log_id = cur.lastrowid
        conn.commit()
        return log_id
    except Exception as e:
        print(f"❌ Ошибка отметки привычки: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()


def get_habit_logs(habit_id):
    conn = get_connection()
    if conn is None:
        return []
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM habit_logs WHERE habit_id=? ORDER BY date DESC", (habit_id,))
        return [dict(row) for row in cur.fetchall()]
    except Exception as e:
        print(f"❌ Ошибка получения логов: {e}")
        return []
    finally:
        cur.close()
        conn.close()


# ---------- СТАТИСТИКА ----------
def get_habit_stats(habit_id):
    conn = get_connection()
    if conn is None:
        return empty_stats()
    cur = conn.cursor()
    try:
        cur.execute("SELECT date FROM habit_logs WHERE habit_id=? ORDER BY date", (habit_id,))
        completions = [row[0] for row in cur.fetchall()]

        stats = {
            "total_done": len(completions),
            "current_streak": calculate_current_streak(completions),
            "longest_streak": calculate_longest_streak(completions),
            "completions": completions,
            "last_30_days": get_last_30_days_completions(habit_id)
        }
        return stats
    except Exception as e:
        print(f"❌ Ошибка получения статистики: {e}")
        return empty_stats()
    finally:
        cur.close()
        conn.close()


def empty_stats():
    return {
        "total_done": 0,
        "current_streak": 0,
        "longest_streak": 0,
        "completions": [],
        "last_30_days": []
    }


def calculate_current_streak(completions):
    if not completions:
        return 0
    today = datetime.now().date()
    streak = 0
    for i in range(30):
        check_date = today - timedelta(days=i)
        if check_date.strftime("%Y-%m-%d") in completions:
            streak += 1
        else:
            break
    return streak


def calculate_longest_streak(completions):
    if not completions:
        return 0
    dates = sorted(datetime.strptime(d, "%Y-%m-%d").date() for d in completions)
    longest, current = 1, 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            current += 1
            longest = max(longest, current)
        else:
            current = 1
    return longest


def get_last_30_days_completions(habit_id):
    conn = get_connection()
    if conn is None:
        return []
    cur = conn.cursor()
    try:
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        cur.execute(
            "SELECT date FROM habit_logs WHERE habit_id=? AND date >= ? ORDER BY date",
            (habit_id, thirty_days_ago),
        )
        return [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(f"❌ Ошибка получения выполнений за 30 дней: {e}")
        return []
    finally:
        cur.close()
        conn.close()


# ---------- CRUD REMINDERS ----------
def save_reminder(habit_id, time, repeat, days, vibration, sound, text):
    conn = get_connection()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT OR REPLACE INTO reminders (habit_id, time, repeat, days, vibration, sound, text)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (habit_id, time, repeat, days, vibration, sound, text))
        reminder_id = cur.lastrowid
        conn.commit()
        return reminder_id
    except Exception as e:
        print(f"❌ Ошибка сохранения напоминания: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()


def get_reminder(habit_id):
    conn = get_connection()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM reminders WHERE habit_id=?", (habit_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"❌ Ошибка получения напоминания: {e}")
        return None
    finally:
        cur.close()
        conn.close()


# ---------- CRUD SETTINGS ----------
def save_settings(dark_theme, primary_color):
    conn = get_connection()
    if conn is None:
        return
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT OR REPLACE INTO settings (id, dark_theme, primary_color)
            VALUES (1, ?, ?)
        """, (dark_theme, primary_color))
        conn.commit()
    except Exception as e:
        print(f"❌ Ошибка сохранения настроек: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def get_settings():
    conn = get_connection()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM settings WHERE id=1")
        row = cur.fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"❌ Ошибка получения настроек: {e}")
        return None
    finally:
        cur.close()
        conn.close()


# ---------- АВТОЗАПУСК ----------
if __name__ == "__main__":
    init_db()
