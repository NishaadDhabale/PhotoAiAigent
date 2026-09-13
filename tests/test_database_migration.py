from app.database import create_database, migrate_database, DATABASE_PATH
import sqlite3


create_database()
migrate_database()

connection = sqlite3.connect(DATABASE_PATH)

columns = connection.execute(
    "PRAGMA table_info(faces)"
).fetchall()

connection.close()

print("faces table columns:")

for column in columns:
    print(f"  {column[1]} -> {column[2]}")
    