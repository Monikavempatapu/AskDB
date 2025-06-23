import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

print("ID | Username | Password")
print("-" * 30)
for row in rows:
    print(row)

conn.close()
