from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def connect_db():
    """Establish a database connection and enable foreign keys."""
    conn = sqlite3.connect('groups_and_pages.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON')
    return conn, cursor

@app.route('/')
def index():
    """Display all groups and their pages."""
    conn, cursor = connect_db()

    # Query to fetch all groups and their pages (including groups without pages)
    cursor.execute('''
        SELECT g.group_id, g.name, p.page_id, p.text
        FROM groups g
        LEFT JOIN pages p ON g.group_id = p.group_id
        ORDER BY g.group_id, p.page_id
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    return render_template('index.html', data=rows)

@app.route('/add_group', methods=['GET', 'POST'])
def add_group():
    """Add a new group to the database and create a default page."""
    if request.method == 'POST':
        group_name = request.form['name']
        
        conn, cursor = connect_db()

        # Check if the group already exists
        cursor.execute("SELECT * FROM groups WHERE name = ?", (group_name,))
        existing_group = cursor.fetchone()

        if existing_group:
            # If group exists, close the connection and show a message
            conn.close()
            return "Group '{}' already exists!".format(group_name)


        # If the group is new, insert it
        cursor.execute("INSERT INTO groups (name, date_created) VALUES (?, ?)", 
                       (group_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        # Get the ID of the newly created group
        new_group_id = cursor.lastrowid

        # Automatically add a default page for the new group
        cursor.execute("INSERT INTO pages (group_id, text) VALUES (?, ?)", 
                       (new_group_id, 'Default page for ' + group_name))

        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('add_group.html')


@app.route('/delete_group/<int:group_id>', methods=['GET', 'POST'])
def delete_group(group_id):
    """Delete a group and its pages."""
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM groups WHERE group_id = ?", (group_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/add_page/<int:group_id>', methods=['GET', 'POST'])
def add_page(group_id):
    """Add a new page to a specific group."""
    if request.method == 'POST':
        page_text = request.form['text']
        conn, cursor = connect_db()
        cursor.execute("INSERT INTO pages (group_id, text) VALUES (?, ?)", 
                       (group_id, page_text))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_page.html', group_id=group_id)



if __name__ == '__main__':
    app.run(debug=True)
