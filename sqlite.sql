

cursor.execute("DROP TABLE IF EXISTS claims")
cursor.execute("DROP TABLE IF EXISTS lost_items")

cursor.execute("""
CREATE TABLE lost_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    category TEXT NOT NULL,
    color TEXT NOT NULL,
    location_found TEXT NOT NULL,
    date_found DATE NOT NULL,
    image BLOB
)
""")

cursor.execute("""
CREATE TABLE claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    student_name TEXT NOT NULL,
    bus_route TEXT NOT NULL,
    claim_date TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (item_id) REFERENCES lost_items(id)
)
""")

connect.commit()
