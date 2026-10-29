import sqlite3
c=sqlite3.connect('data/genassess.db')
print(c.execute("SELECT id,name,email,role FROM users WHERE email='tejashwinipuppala05@gmail.com'").fetchall())