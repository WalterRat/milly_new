import sqlite3

def db_config():
    conn = sqlite3.connect('roles.db')
    cursor = conn.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS Roles (master_id INTEGER PRIMARY KEY, role_id INT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS Channels (channel_id INTEGER PRIMARY KEY)')

    conn.commit()
    allowed_channels = cursor.execute('SELECT channel_id FROM Channels').fetchall()
    allowed_channels = list(x[0] for x in allowed_channels)
    conn.close()
    return allowed_channels

allowed_channels = db_config()

