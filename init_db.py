import sqlite3

conn = sqlite3.connect("/var/www/html/CTFSystem/data/ctf.db")
c = conn.cursor()

# Create users table
c.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        points INTEGER DEFAULT 0
    )
"""
)

# Create challenges table
c.execute(
    """
    CREATE TABLE IF NOT EXISTS challenges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        solution TEXT NOT NULL,
        type TEXT NOT NULL,
        points INTEGER NOT NULL
    )
"""
)

# Insert sample challenges
# c.execute(
#     """
#     INSERT INTO challenges (title, description, solution, type, points) VALUES
#     ('Example Daily Challenge', 'Solve this simple problem.', 'correctsolution', 'daily', 10),
#     ('Example Level Challenge', 'Solve this complex problem.', 'correctsolution', 'level', 20)
# """
# )



conn.commit()
conn.close()
