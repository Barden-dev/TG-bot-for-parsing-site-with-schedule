import sqlite3

con = sqlite3.connect("schedule_bot.db")
cursor = con.cursor()

def init_db():
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
    (user_id INTEGER PRIMARY KEY,
    group_name TEXT,
    use_12h_format INTEGER
    )
    ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS reminders
    (user_id INTEGER PRIMARY KEY,
    time TEXT,
    type TEXT
    )
    ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS reminders_days
    (user_id INTEGER PRIMARY KEY,
    type TEXT,
    days TEXT DEFAULT 'mon,tue,wed,thu,fri'
    )
    ''')
    con.commit()
    
    
# ЗДЕСЬ ПОЛУЧАЕМ ГРУППУ ПОЛЬЗОВАТЕЛЯ, ТАКЖЕ МОЖЕМ ИСПОЛЬЗОВАТЬ ДЛЯ ПРОВЕРКИ НАЛИЧИЯ ПОЛЬЗОВАТЕЛЯ В БАЗЕ ДАННЫХ
def user_group(userid):
    cursor.execute('SELECT group_name FROM users WHERE user_id = ?', (userid,))
    group = cursor.fetchone()
    if group == None:
        return False
    else:
        return group[0]

def change_user_group(userid, group):
    try:
        cursor.execute(f"INSERT INTO users (user_id, group_name) VALUES (?, ?)", (userid, group,))
        con.commit()
    except:
        cursor.execute(f"UPDATE users SET group_name = ? WHERE user_id = ?", (group, userid))
        con.commit()
        
def add_reminder(userid, time, type):
    try:
        cursor.execute(f"INSERT INTO reminders (user_id, time, type) VALUES (?, ?, ?)", (userid, time, type,))
        con.commit()
    except:
        cursor.execute(f"UPDATE reminders SET time = ?, type = ? WHERE user_id = ?", (time, type, userid))
        con.commit()
        
def remove_reminder(userid, time, type):
    cursor.execute(f"DELETE FROM reminders WHERE user_id = ? AND time = ? AND type = ?", (userid, time, type,))
    con.commit()
    
def get_user_reminders(userid):
    cursor.execute('SELECT time, type FROM reminders WHERE user_id = ?', (userid,))
    reminders = cursor.fetchall()
    return reminders


def get_users_id():
    cursor.execute('SELECT user_id FROM users')
    return cursor.fetchall()

def get_current_notification(time):
    #cursor.execute('SELECT * FROM reminders ORDER BY time')
    cursor.execute('SELECT user_id,time, type FROM reminders WHERE time = ? ORDER BY time', (time,))
    return cursor.fetchall()

def get_notification_days(userid):
    cursor.execute('SELECT * FROM reminders_days WHERE user_id = ?', (userid,))
    return cursor.fetchall()

def change_notification_days(userid, _type, day):
    try:
        cursor.execute(f"INSERT INTO reminders_days (user_id, type) VALUES (?, ?)", (userid, _type))
        con.commit()
    except:
        cursor.execute(f"UPDATE reminders_days SET days = ? WHERE user_id = ? AND type = ?", (day, userid, _type))
        con.commit()  

