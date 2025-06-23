import sqlite3

# Step 1: Read schema.sql file
try:
    with open('schema.sql', 'r') as file:
        schema_sql = file.read()
except FileNotFoundError:
    print("❌ schema.sql not found. Make sure it's in the same folder.")
    exit()

# Step 2: Connect to database.db (or create if doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Step 3: Execute the schema SQL script
try:
    cursor.executescript(schema_sql)
    conn.commit()
    print("✅ Successfully created 'database.db' using schema.sql!")
except Exception as e:
    print(f"❌ Failed to execute schema: {e}")
finally:
    conn.close()
