from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import bleach
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.email = user_data['email']
        self.is_admin = user_data['is_admin']
        self.is_banned = user_data['is_banned']
        # Handle reputation field - it might not exist in old database
        try:
            self.reputation = user_data['reputation']
        except (KeyError, IndexError):
            self.reputation = 0
        self.created_at = user_data['created_at']
    
    @property
    def is_active(self):
        return not self.is_banned

# Database setup
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            is_banned BOOLEAN DEFAULT 0,
            reputation INTEGER DEFAULT 0,
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
            accepted_answer_id INTEGER,
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
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            answer_id INTEGER NOT NULL,
            value INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (answer_id) REFERENCES answers (id),
            UNIQUE(user_id, answer_id)
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
            FOREIGN KEY (question_id) REFERENCES questions (id),
            FOREIGN KEY (tag_id) REFERENCES tags (id),
            PRIMARY KEY (question_id, tag_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            related_id INTEGER,
            is_read BOOLEAN DEFAULT 0,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    user_data = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user_data:
        return User(user_data)
    return None

# Sanitize HTML content
def sanitize_html(html_content):
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                   'ul', 'ol', 'li', 'a', 'img', 'blockquote', 'code', 'pre']
    allowed_attributes = {
        'a': ['href'],
        'img': ['src', 'alt', 'width', 'height']
    }
    return bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attributes)

# Routes
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/questions')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    
    conn = get_db()
    
    # Get filter parameter
    filter_type = request.args.get('filter', 'newest')
    search_query = request.args.get('search', '')
    
    # Build query based on filter
    if filter_type == 'unanswered':
        base_query = '''
            SELECT q.*, u.username, 
                   (SELECT COUNT(*) FROM answers WHERE question_id = q.id) as answer_count,
                   GROUP_CONCAT(t.name) as tags
            FROM questions q
            LEFT JOIN users u ON q.user_id = u.id
            LEFT JOIN question_tags qt ON q.id = qt.question_id
            LEFT JOIN tags t ON qt.tag_id = t.id
            WHERE q.id NOT IN (SELECT DISTINCT question_id FROM answers)
        '''
        
        # Add search condition for unanswered
        if search_query:
            base_query += f" AND (q.title LIKE '%{search_query}%' OR t.name LIKE '%{search_query}%')"
    else:
        base_query = '''
            SELECT q.*, u.username, 
                   (SELECT COUNT(*) FROM answers WHERE question_id = q.id) as answer_count,
                   GROUP_CONCAT(t.name) as tags
            FROM questions q
            LEFT JOIN users u ON q.user_id = u.id
            LEFT JOIN question_tags qt ON q.id = qt.question_id
            LEFT JOIN tags t ON qt.tag_id = t.id
        '''
        
        # Add search condition for other filters
        if search_query:
            base_query += f" WHERE (q.title LIKE '%{search_query}%' OR t.name LIKE '%{search_query}%')"
    
    base_query += " GROUP BY q.id"
    
    if filter_type == 'newest':
        base_query += " ORDER BY q.created_at DESC"
    elif filter_type == 'votes':
        base_query += " ORDER BY (SELECT COALESCE(SUM(v.value), 0) FROM votes v JOIN answers a ON v.answer_id = a.id WHERE a.question_id = q.id) DESC"
    
    # Add pagination
    base_query += f" LIMIT {per_page} OFFSET {offset}"
    
    questions = conn.execute(base_query).fetchall()
    
    # Get total count for pagination
    if filter_type == 'unanswered':
        count_query = '''
            SELECT COUNT(DISTINCT q.id) as total
            FROM questions q
            LEFT JOIN question_tags qt ON q.id = qt.question_id
            LEFT JOIN tags t ON qt.tag_id = t.id
            WHERE q.id NOT IN (SELECT DISTINCT question_id FROM answers)
        '''
        
        if search_query:
            count_query += f" AND (q.title LIKE '%{search_query}%' OR t.name LIKE '%{search_query}%')"
    else:
        count_query = '''
            SELECT COUNT(DISTINCT q.id) as total
            FROM questions q
            LEFT JOIN question_tags qt ON q.id = qt.question_id
            LEFT JOIN tags t ON qt.tag_id = t.id
        '''
        
        if search_query:
            count_query += f" WHERE (q.title LIKE '%{search_query}%' OR t.name LIKE '%{search_query}%')"
    
    total = conn.execute(count_query).fetchone()['total']
    
    conn.close()
    
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('index.html', 
                         questions=questions, 
                         page=page, 
                         total_pages=total_pages,
                         filter_type=filter_type,
                         search_query=search_query)

@app.route('/ask', methods=['GET', 'POST'])
@login_required
def ask():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        tags = request.form.get('tags', '').split(',')
        
        if not title or not body:
            flash('Title and body are required!', 'error')
            return render_template('ask.html')
        
        # Sanitize HTML
        body_html = sanitize_html(body)
        
        conn = get_db()
        
        # Insert question
        cursor = conn.execute(
            'INSERT INTO questions (title, body_html, user_id) VALUES (?, ?, ?)',
            (title, body_html, current_user.id)
        )
        question_id = cursor.lastrowid
        
        # Handle tags
        tags = [tag.strip() for tag in tags if tag.strip()]
        for tag_name in tags:
            # Check if tag exists
            tag = conn.execute('SELECT id FROM tags WHERE name = ?', (tag_name,)).fetchone()
            if not tag:
                # Create new tag
                cursor = conn.execute('INSERT INTO tags (name) VALUES (?)', (tag_name,))
                tag_id = cursor.lastrowid
            else:
                tag_id = tag['id']
            
            # Link tag to question
            conn.execute('INSERT OR IGNORE INTO question_tags (question_id, tag_id) VALUES (?, ?)', 
                        (question_id, tag_id))
        
        conn.commit()
        conn.close()
        
        flash('Question posted successfully!', 'success')
        return redirect(url_for('question', question_id=question_id))
    
    return render_template('ask.html')

@app.route('/question/<int:question_id>')
def question(question_id):
    conn = get_db()
    
    # Get question details
    question = conn.execute('''
        SELECT q.*, u.username, GROUP_CONCAT(t.name) as tags
        FROM questions q
        LEFT JOIN users u ON q.user_id = u.id
        LEFT JOIN question_tags qt ON q.id = qt.question_id
        LEFT JOIN tags t ON qt.tag_id = t.id
        WHERE q.id = ?
        GROUP BY q.id
    ''', (question_id,)).fetchone()
    
    if not question:
        flash('Question not found!', 'error')
        return redirect(url_for('index'))
    
    # Get answers with vote counts and reputation
    answers = conn.execute('''
        SELECT a.*, u.username, u.reputation,
               (SELECT COALESCE(SUM(v.value), 0) FROM votes v WHERE v.answer_id = a.id) as vote_count
        FROM answers a
        LEFT JOIN users u ON a.user_id = u.id
        WHERE a.question_id = ?
        ORDER BY a.id = ? DESC, vote_count DESC, a.created_at ASC
    ''', (question_id, question['accepted_answer_id'])).fetchall()
    
    conn.close()
    
    return render_template('question.html', question=question, answers=answers)

@app.route('/answer', methods=['POST'])
@login_required
def post_answer():
    question_id = request.form.get('question_id')
    body = request.form.get('body')
    
    if not body:
        flash('Answer body is required!', 'error')
        return redirect(url_for('question', question_id=question_id))
    
    # Sanitize HTML
    body_html = sanitize_html(body)
    
    conn = get_db()
    
    # Insert answer
    conn.execute(
        'INSERT INTO answers (question_id, body_html, user_id) VALUES (?, ?, ?)',
        (question_id, body_html, current_user.id)
    )
    
    # Create notification for question author
    question = conn.execute('SELECT user_id FROM questions WHERE id = ?', (question_id,)).fetchone()
    if question and question['user_id'] != current_user.id:
        conn.execute('''
            INSERT INTO notifications (user_id, type, related_id, message)
            VALUES (?, ?, ?, ?)
        ''', (question['user_id'], 'answer', question_id, 
              f'{current_user.username} answered your question'))
    
    conn.commit()
    conn.close()
    
    flash('Answer posted successfully!', 'success')
    return redirect(url_for('question', question_id=question_id))

@app.route('/vote', methods=['POST'])
@login_required
def vote():
    answer_id = request.form.get('answer_id')
    value = int(request.form.get('value'))
    
    if value not in [-1, 1]:
        return jsonify({'error': 'Invalid vote value'}), 400
    
    conn = get_db()
    
    # Get answer author for reputation calculation
    answer = conn.execute(
        'SELECT user_id FROM answers WHERE id = ?', (answer_id,)
    ).fetchone()
    
    if not answer:
        conn.close()
        return jsonify({'error': 'Answer not found'}), 404
    
    answer_author_id = answer['user_id']
    
    # Check if user already voted
    existing_vote = conn.execute(
        'SELECT value FROM votes WHERE user_id = ? AND answer_id = ?',
        (current_user.id, answer_id)
    ).fetchone()
    
    old_vote_value = 0
    if existing_vote:
        old_vote_value = existing_vote['value']
    
    if existing_vote:
        if existing_vote['value'] == value:
            # Remove vote
            conn.execute(
                'DELETE FROM votes WHERE user_id = ? AND answer_id = ?',
                (current_user.id, answer_id)
            )
            # Update reputation (remove old vote effect)
            if old_vote_value == 1:
                conn.execute(
                    'UPDATE users SET reputation = reputation - 10 WHERE id = ?',
                    (answer_author_id,)
                )
            elif old_vote_value == -1:
                conn.execute(
                    'UPDATE users SET reputation = reputation + 2 WHERE id = ?',
                    (answer_author_id,)
                )
        else:
            # Change vote
            conn.execute(
                'UPDATE votes SET value = ? WHERE user_id = ? AND answer_id = ?',
                (value, current_user.id, answer_id)
            )
            # Update reputation (remove old vote and add new vote effect)
            if old_vote_value == 1:
                conn.execute(
                    'UPDATE users SET reputation = reputation - 10 WHERE id = ?',
                    (answer_author_id,)
                )
            elif old_vote_value == -1:
                conn.execute(
                    'UPDATE users SET reputation = reputation + 2 WHERE id = ?',
                    (answer_author_id,)
                )
            
            if value == 1:
                conn.execute(
                    'UPDATE users SET reputation = reputation + 10 WHERE id = ?',
                    (answer_author_id,)
                )
            elif value == -1:
                conn.execute(
                    'UPDATE users SET reputation = reputation - 2 WHERE id = ?',
                    (answer_author_id,)
                )
    else:
        # New vote
        conn.execute(
            'INSERT INTO votes (user_id, answer_id, value) VALUES (?, ?, ?)',
            (current_user.id, answer_id, value)
        )
        # Update reputation
        if value == 1:
            conn.execute(
                'UPDATE users SET reputation = reputation + 10 WHERE id = ?',
                (answer_author_id,)
            )
        elif value == -1:
            conn.execute(
                'UPDATE users SET reputation = reputation - 2 WHERE id = ?',
                (answer_author_id,)
            )
    
    conn.commit()
    
    # Get updated vote count and reputation
    vote_count = conn.execute(
        'SELECT COALESCE(SUM(value), 0) as count FROM votes WHERE answer_id = ?',
        (answer_id,)
    ).fetchone()['count']
    
    updated_reputation = conn.execute(
        'SELECT reputation FROM users WHERE id = ?', (answer_author_id,)
    ).fetchone()['reputation']
    
    conn.close()
    
    return jsonify({
        'vote_count': vote_count,
        'reputation': updated_reputation
    })

@app.route('/accept_answer', methods=['POST'])
@login_required
def accept_answer():
    answer_id = request.form.get('answer_id')
    question_id = request.form.get('question_id')
    
    conn = get_db()
    
    # Check if user is question author
    question = conn.execute(
        'SELECT user_id FROM questions WHERE id = ?', (question_id,)
    ).fetchone()
    
    if not question or question['user_id'] != current_user.id:
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Update question to accept answer
    conn.execute(
        'UPDATE questions SET accepted_answer_id = ? WHERE id = ?',
        (answer_id, question_id)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/delete_answer', methods=['POST'])
@login_required
def delete_answer():
    answer_id = request.form.get('answer_id')
    
    conn = get_db()
    
    # Get answer details
    answer = conn.execute(
        'SELECT a.*, u.username FROM answers a JOIN users u ON a.user_id = u.id WHERE a.id = ?',
        (answer_id,)
    ).fetchone()
    
    if not answer:
        conn.close()
        return jsonify({'error': 'Answer not found'}), 404
    
    # Check if user is admin or answer author
    if not current_user.is_admin and answer['user_id'] != current_user.id:
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete the answer
    conn.execute('DELETE FROM answers WHERE id = ?', (answer_id,))
    
    # Also delete associated votes
    conn.execute('DELETE FROM votes WHERE answer_id = ?', (answer_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        user_data = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            if user_data['is_banned']:
                flash('Your account has been banned.', 'error')
                return render_template('login.html')
            
            user = User(user_data)
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not email or not password:
            flash('All fields are required!', 'error')
            return render_template('register.html')
        
        conn = get_db()
        
        # Check if username or email already exists
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?',
            (username, email)
        ).fetchone()
        
        if existing_user:
            conn.close()
            flash('Username or email already exists!', 'error')
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        conn.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/notifications')
@login_required
def notifications():
    conn = get_db()
    notifications = conn.execute('''
        SELECT * FROM notifications 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 20
    ''', (current_user.id,)).fetchall()
    
    # Mark as read
    conn.execute(
        'UPDATE notifications SET is_read = 1 WHERE user_id = ?',
        (current_user.id,)
    )
    conn.commit()
    conn.close()
    
    return jsonify([{
        'id': n['id'],
        'message': n['message'],
        'timestamp': n['timestamp'],
        'is_read': n['is_read']
    } for n in notifications])

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    conn = get_db()
    
    # Get statistics
    stats = {
        'total_users': conn.execute('SELECT COUNT(*) FROM users').fetchone()[0],
        'total_questions': conn.execute('SELECT COUNT(*) FROM questions').fetchone()[0],
        'total_answers': conn.execute('SELECT COUNT(*) FROM answers').fetchone()[0],
        'banned_users': conn.execute('SELECT COUNT(*) FROM users WHERE is_banned = 1').fetchone()[0]
    }
    
    # Get recent users
    recent_users = conn.execute('''
        SELECT * FROM users ORDER BY created_at DESC LIMIT 10
    ''').fetchall()
    
    # Get flagged content (questions with no answers for more than 7 days)
    flagged_questions = conn.execute('''
        SELECT q.*, u.username, 
               (SELECT COUNT(*) FROM answers WHERE question_id = q.id) as answer_count
        FROM questions q
        LEFT JOIN users u ON q.user_id = u.id
        WHERE q.id NOT IN (SELECT DISTINCT question_id FROM answers)
        AND q.created_at < datetime('now', '-7 days')
        ORDER BY q.created_at ASC
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_users=recent_users,
                         flagged_questions=flagged_questions)

@app.route('/admin/ban_user', methods=['POST'])
@login_required
def ban_user():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user_id = request.form.get('user_id')
    action = request.form.get('action')  # 'ban' or 'unban'
    
    conn = get_db()
    is_banned = 1 if action == 'ban' else 0
    conn.execute(
        'UPDATE users SET is_banned = ? WHERE id = ?',
        (is_banned, user_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 