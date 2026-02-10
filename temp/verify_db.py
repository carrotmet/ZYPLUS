import sqlite3

conn = sqlite3.connect('D:/github.com/carrotmet/zyplusv2/data/career_guidance.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
print('Tables in database:')
for t in tables:
    print(f'  - {t[0]}')
conn.close()
