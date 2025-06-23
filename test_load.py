import nl2sql

print("\n--- Choose a file to test loading ---")
file_path = input("Enter full path to .csv, .xlsx or .db file: ")

try:
    table = nl2sql.load_file_to_sqlite(file_path)
    print(f"\n✅ Successfully loaded! Table: {table}")
    print("Tables:", nl2sql.get_tables())
    print("Columns:", nl2sql.get_columns(table))

    # Test query generation
    test_query = "show all records"
    sql = nl2sql.convert_to_sql(test_query)
    print("\nGenerated SQL:", sql)

except Exception as e:
    print("\n❌ Failed to load file:", e)
