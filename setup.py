#!/usr/bin/env python3
"""
StackIt Setup Script
Initializes the database and creates demo data
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def init_db():
    """Initialize the database with all required tables"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body_html TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            body_html TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (question_id) REFERENCES questions (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_tags (
            question_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (question_id, tag_id),
            FOREIGN KEY (question_id) REFERENCES questions (id),
            FOREIGN KEY (tag_id) REFERENCES tags (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question_id INTEGER,
            answer_id INTEGER,
            vote_type INTEGER NOT NULL, -- 1 for upvote, -1 for downvote
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (question_id) REFERENCES questions (id),
            FOREIGN KEY (answer_id) REFERENCES answers (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database tables created successfully!")

def insert_demo_data():
    """Insert demo users, questions, and answers"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute('DELETE FROM users')
    cursor.execute('DELETE FROM questions')
    cursor.execute('DELETE FROM answers')
    cursor.execute('DELETE FROM tags')
    cursor.execute('DELETE FROM question_tags')
    cursor.execute('DELETE FROM votes')
    cursor.execute('DELETE FROM notifications')
    
    # Demo users (including the requested demo user)
    users = [
        ('demo', 'demo@stackit.com', 'demo123', 0, 0, 150),  # Main demo user with reputation
        ('alice', 'alice@example.com', 'password1', 0, 0, 85),
        ('bob', 'bob@example.com', 'password2', 0, 0, 120),
        ('carol', 'carol@example.com', 'password3', 0, 0, 95),
        ('dave', 'dave@example.com', 'password4', 0, 0, 200),
        ('eve', 'eve@example.com', 'password5', 1, 0, 500),  # admin with high reputation
        ('frank', 'frank@example.com', 'password6', 0, 0, 75),
        ('grace', 'grace@example.com', 'password7', 0, 0, 110),
        ('heidi', 'heidi@example.com', 'password8', 0, 0, 60),
        ('ivan', 'ivan@example.com', 'password9', 0, 0, 180),
        ('judy', 'judy@example.com', 'password10', 0, 0, 90),
    ]
    
    user_ids = []
    for username, email, pw, is_admin, is_banned, reputation in users:
        cursor.execute('INSERT INTO users (username, email, password_hash, is_admin, is_banned, reputation) VALUES (?, ?, ?, ?, ?, ?)',
                       (username, email, generate_password_hash(pw), is_admin, is_banned, reputation))
        user_ids.append(cursor.lastrowid)
    
    # Tags
    tags = ['Python', 'Flask', 'SQL', 'JWT', 'HTML', 'CSS', 'JavaScript', 'Bootstrap', 'Jinja2', 'Security', 'Web Development', 'API']
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
        ('What is the best way to structure a Flask app?', '<p>I\'m new to Flask. How should I organize my project structure?</p>', ["Flask", "Web Development"]),
        ('How to create REST APIs with Flask?', '<p>I want to build a REST API using Flask. Any guidance?</p>', ["Flask", "API"]),
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
        ('You can use Flask\'s session object. Import it from flask and use it like a dictionary.', 0),
        ('Jinja2 is a templating engine for Python. It allows you to use Python-like expressions in HTML.', 1),
        ('Use werkzeug.security for hashing. It provides secure password hashing functions.', 2),
        ('Use sqlite3 module in Python. Flask can work with it directly.', 3),
        ('JWT is a token format for authentication. It\'s self-contained and stateless.', 4),
        ('Add Bootstrap CDN in your base.html. Include the CSS and JS files.', 5),
        ('Jinja2 lets you use logic in templates. HTML is just markup.', 6),
        ('Link your CSS in the head of base.html. Use url_for to reference static files.', 7),
        ('Use <script> tags in your templates. You can also link external JS files.', 8),
        ('Use parameterized queries to prevent SQL injection. Never use string formatting.', 9),
        ('Use the factory pattern. Create an app factory function for better organization.', 10),
        ('Use Flask-RESTful or create your own endpoints. Define routes with proper HTTP methods.', 11),
        ('Sessions are signed cookies in Flask. They store data on the client side.', 0),
        ('You can use Flask-WTF for forms. It provides CSRF protection.', 1),
        ('bcrypt is a good password hasher. It\'s slow and secure.', 2),
        ('SQLAlchemy is a popular ORM. It provides database abstraction.', 3),
        ('JWTs are often used with OAuth. They contain user information.', 4),
        ('You can use Flask-Bootstrap. It provides Bootstrap integration.', 5),
        ('Jinja2 supports template inheritance. Use extends and block tags.', 6),
        ('Put your CSS in static/css. Flask serves static files automatically.', 7),
        ('Use url_for to link JS files. It generates correct URLs.', 8),
        ('Always validate user input. Use Flask-WTF for form validation.', 9),
        ('Separate concerns. Keep routes, models, and templates organized.', 10),
        ('Use Blueprint for larger apps. It helps organize routes.', 11),
    ]
    
    for i, (body, qidx) in enumerate(answers):
        user_id = user_ids[(i+1) % len(user_ids)]
        created_at = (datetime.now() - timedelta(days=random.randint(0, 10))).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('INSERT INTO answers (question_id, body_html, user_id, created_at) VALUES (?, ?, ?, ?)',
                       (question_ids[qidx], f'<p>{body}</p>', user_id, created_at))
    
    conn.commit()
    conn.close()
    print("✅ Demo data inserted successfully!")

def main():
    """Main setup function"""
    print("🚀 Setting up StackIt...")
    print("=" * 50)
    
    # Initialize database
    print("📊 Creating database tables...")
    init_db()
    
    # Insert demo data
    print("📝 Inserting demo data...")
    insert_demo_data()
    
    print("=" * 50)
    print("✅ Setup completed successfully!")
    print("\n🎉 StackIt is ready to use!")
    print("\n📋 Demo Users:")
    print("   Username: demo, Password: demo123")
    print("   Username: alice, Password: password1")
    print("   Username: bob, Password: password2")
    print("   Username: eve, Password: password5 (Admin)")
    print("\n🚀 To start the application:")
    print("   python app.py")
    print("\n🌐 Then visit: http://127.0.0.1:5000")

if __name__ == '__main__':
    main() 