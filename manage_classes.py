import sqlite3
from datetime import datetime

def connect_db():
    """Establishes a connection to the database and returns the connection and cursor."""
    conn = sqlite3.connect('groups_and_pages.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON')  # Ensure foreign keys are enabled
    return conn, cursor

def create_tables():
    """Creates the groups and pages tables if they don't exist."""
    conn, cursor = connect_db()
    
    # Create 'groups' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            group_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date_created TEXT NOT NULL
        )
    ''')

    # Create 'pages' table with foreign key constraint
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            page_id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            text TEXT,
            FOREIGN KEY (group_id) REFERENCES groups (group_id) ON DELETE CASCADE
        )
    ''')

    print("Database and tables created successfully!")
    conn.commit()
    conn.close()

def insert_sample_data():
    """Inserts sample groups and pages into the database."""
    conn, cursor = connect_db()

    # Insert sample group data
    groups = [
        ('Group 1', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ('Group 2', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    ]
    cursor.executemany("INSERT INTO groups (name, date_created) VALUES (?, ?)", groups)

    # Insert sample pages data linked to groups
    pages = [
        (1, 'This is the first page of Group 1'),
        (1, 'This is the second page of Group 1'),
        (2, 'This is the first page of Group 2')
    ]
    cursor.executemany("INSERT INTO pages (group_id, text) VALUES (?, ?)", pages)

    print("Sample data inserted successfully!")
    conn.commit()
    conn.close()

def query_data():
    """Fetches and displays all pages with their associated group names."""
    conn, cursor = connect_db()

    # Query to join 'groups' and 'pages' to display pages with their group names
    cursor.execute('''
        SELECT groups.name, pages.page_id, pages.text
        FROM pages
        INNER JOIN groups ON pages.group_id = groups.group_id
    ''')

    # Fetch and print the results
    rows = cursor.fetchall()
    for row in rows:
        print(f"Group: {row[0]}, Page ID: {row[1]}, Text: {row[2]}")

    conn.close()

def delete_group(group_id):
    """Deletes a group and its associated pages based on the given group_id."""
    conn, cursor = connect_db()

    # Delete a group (and cascade delete its pages)
    cursor.execute("DELETE FROM groups WHERE group_id = ?", (group_id,))
    print(f"Group {group_id} and its pages deleted successfully!")

    conn.commit()
    conn.close()

# Run the functions in order
if __name__ == "__main__":
    create_tables()  # Create tables
    insert_sample_data()  # Insert sample data
    query_data()  # Query and display the data

    # Uncomment this line to test group deletion
    # delete_group(1)
