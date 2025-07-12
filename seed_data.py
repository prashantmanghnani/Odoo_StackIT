import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Users
users = [
    ('alice', 'alice@example.com', 'password1', 0, 0),
    ('bob', 'bob@example.com', 'password2', 0, 0),
    ('carol', 'carol@example.com', 'password3', 0, 0),
    ('dave', 'dave@example.com', 'password4', 0, 0),
    ('eve', 'eve@example.com', 'password5', 1, 0),  # admin
    ('frank', 'frank@example.com', 'password6', 0, 0),
    ('grace', 'grace@example.com', 'password7', 0, 0),
    ('heidi', 'heidi@example.com', 'password8', 0, 0),
    ('ivan', 'ivan@example.com', 'password9', 0, 0),
    ('judy', 'judy@example.com', 'password10', 0, 0),
]

cursor.execute('DELETE FROM users')
cursor.execute('DELETE FROM questions')
cursor.execute('DELETE FROM answers')
cursor.execute('DELETE FROM tags')
cursor.execute('DELETE FROM question_tags')
cursor.execute('DELETE FROM votes')
cursor.execute('DELETE FROM notifications')

user_ids = []
for username, email, pw, is_admin, is_banned in users:
    cursor.execute('INSERT INTO users (username, email, password_hash, is_admin, is_banned) VALUES (?, ?, ?, ?, ?)',
                   (username, email, generate_password_hash(pw), is_admin, is_banned))
    user_ids.append(cursor.lastrowid)

# Tags
tags = ['Python', 'Flask', 'SQL', 'JWT', 'HTML', 'CSS', 'JavaScript', 'Bootstrap', 'Jinja2', 'Security']
tag_ids = {}
for tag in tags:
    cursor.execute('INSERT INTO tags (name) VALUES (?)', (tag,))
    tag_ids[tag] = cursor.lastrowid

# Questions
questions = [
    ('How to use Flask sessions?', '<p>I want to store user data in Flask sessions. How do I do it?</p>', ["Flask", "Python"]),
    ('What is Jinja2?', '<p>Can someone explain what Jinja2 is and how it works with Flask?</p>', ["Jinja2", "Flask"]),
    ('How to hash passwords in Python?', '<p>What is the best way to hash passwords securely in Python?</p>', ["Python", "Security"]),
    ('How to connect to SQLite in Flask?', '<p>I need to connect my Flask app to SQLite. Any tips?</p>', ["Flask", "SQL"]),
    ('What is JWT and how to use it?', '<p>How does JWT work for authentication?</p>', ["JWT", "Security"]),
    ('How to use Bootstrap with Flask?', '<p>How do I add Bootstrap to my Flask templates?</p>', ["Bootstrap", "Flask"]),
    ('Difference between HTML and Jinja2?', '<p>What is the difference between HTML and Jinja2 templates?</p>', ["HTML", "Jinja2"]),
    ('How to add custom CSS in Flask?', '<p>How do I add my own CSS files to a Flask project?</p>', ["CSS", "Flask"]),
    ('How to use JavaScript in Flask templates?', '<p>How can I include JavaScript in my Flask app?</p>', ["JavaScript", "Flask"]),
    ('How to prevent SQL injection in Flask?', '<p>What are best practices to prevent SQL injection?</p>', ["SQL", "Security"]),
]

question_ids = []
for i, (title, body, qtags) in enumerate(questions):
    user_id = user_ids[i % len(user_ids)]
    created_at = (datetime.now() - timedelta(days=random.randint(0, 10))).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO questions (title, body_html, user_id, created_at) VALUES (?, ?, ?, ?)',
                   (title, body, user_id, created_at))
    qid = cursor.lastrowid
    question_ids.append(qid)
    for tag in qtags:
        cursor.execute('INSERT INTO question_tags (question_id, tag_id) VALUES (?, ?)', (qid, tag_ids[tag]))

# Answers
answers = [
    ('You can use Flask\'s session object.', 0),
    ('Jinja2 is a templating engine for Python.', 1),
    ('Use werkzeug.security for hashing.', 2),
    ('Use sqlite3 module in Python.', 3),
    ('JWT is a token format for authentication.', 4),
    ('Add Bootstrap CDN in your base.html.', 5),
    ('Jinja2 lets you use logic in templates.', 6),
    ('Link your CSS in the head of base.html.', 7),
    ('Use <script> tags in your templates.', 8),
    ('Use parameterized queries to prevent SQL injection.', 9),
    ('Sessions are signed cookies in Flask.', 0),
    ('You can use Flask-WTF for forms.', 1),
    ('bcrypt is a good password hasher.', 2),
    ('SQLAlchemy is a popular ORM.', 3),
    ('JWTs are often used with OAuth.', 4),
    ('You can use Flask-Bootstrap.', 5),
    ('Jinja2 supports template inheritance.', 6),
    ('Put your CSS in static/css.', 7),
    ('Use url_for to link JS files.', 8),
    ('Always validate user input.', 9),
]
for i, (body, qidx) in enumerate(answers):
    user_id = user_ids[(i+1) % len(user_ids)]
    created_at = (datetime.now() - timedelta(days=random.randint(0, 10))).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO answers (question_id, body_html, user_id, created_at) VALUES (?, ?, ?, ?)',
                   (question_ids[qidx], f'<p>{body}</p>', user_id, created_at))

conn.commit()
conn.close()
print('Seed data inserted.') 