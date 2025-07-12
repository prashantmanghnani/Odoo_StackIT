# StackIt – Modern Flask Q&A Platform

StackIt is a modern, beautiful Q&A platform inspired by Stack Overflow, built with Flask. It features user authentication, question/answer posting, search, and a responsive, visually appealing UI.

![StackIt Screenshot](static/screenshots/landing.png)

---

## ✨ Features

- **User Authentication**: Register, login, and logout with Flask-Login
- **Q&A System**: Ask questions and provide answers
- **Reputation System**: Users gain/lose reputation based on upvotes/downvotes
- **Voting System**: Upvote/downvote answers to affect user reputation
- **Admin Controls**: Admins can delete any answer or ban users
- **Search & Filter**: Find questions by title and tags
- **Modern UI**: Responsive design with Bootstrap 5, Google Fonts, and custom CSS
- **Landing Page**: Beautiful homepage with About, Features, and FAQ sections
- **Security**: Password hashing with Werkzeug
- **Database**: SQLite with sample data
- **Clean Code**: Well-structured Flask application

---

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/stackit.git
cd stackit
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Database & Sample Data

```bash
python setup.py
```

This will:
- Create the database tables
- Insert sample users, questions, and answers
- Create demo user credentials

### 5. Run the Application

```bash
python app.py
```

### 6. Access the Application

Open your browser and go to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🧑‍💻 Demo Users

The setup script creates several demo users. You can log in with any of these:

| Username | Password | Role |
|----------|----------|------|
| `alice` | `password1` | Regular User |
| `bob` | `password2` | Regular User |
| `eve` | `password5` | Admin User |

---

## 📝 How to Use

### For New Users

1. **Register**: Click "Sign Up" to create a new account
2. **Login**: Use the demo credentials or your registered account
3. **Ask Questions**: Click "Ask Question" to post your query
4. **Answer**: Click on any question to view and add answers
5. **Vote**: Upvote (▲) or downvote (▼) answers to affect user reputation
6. **Search**: Use the search bar to find specific questions
7. **Explore**: Check the landing page for features and FAQ

### Reputation System

- **Upvote (+10)**: Users gain 10 reputation points when their answer is upvoted
- **Downvote (-2)**: Users lose 2 reputation points when their answer is downvoted
- **Reputation Display**: User reputation is shown next to their username in answers
- **Admin Controls**: Admins can delete any answer and have higher reputation

### For Developers

1. **Database**: SQLite database (`database.db`) with sample data
2. **Templates**: Jinja2 templates in `templates/` directory
3. **Static Files**: CSS, JS, and images in `static/` directory
4. **Configuration**: Flask app configuration in `app.py`

---

## 🛠️ Project Structure

```
stackit/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── setup.py              # Database setup script
├── seed_data.py          # Sample data insertion
├── database.db           # SQLite database
├── templates/            # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   ├── landing.html
│   ├── login.html
│   ├── register.html
│   ├── ask.html
│   └── question.html
└── static/              # Static files
    ├── css/
    │   └── style.css
    ├── js/
    └── screenshots/
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

### Database

The application uses SQLite by default. The database file (`database.db`) will be created automatically when you run `setup.py`.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.7+, Flask 2.3.3, Flask-Login 0.6.3
- **Database**: SQLite3
- **Frontend**: Bootstrap 5, Google Fonts, Bootstrap Icons
- **Templates**: Jinja2
- **Security**: Werkzeug password hashing
- **Forms**: Flask-WTF, WTForms

---

## 🚀 Deployment

### Local Development

```bash
python app.py
```


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt


python app.py
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Flask community for the excellent framework
- Bootstrap team for the responsive UI components
- Stack Overflow for inspiration

---

## 📞 Support

If you encounter any issues:

1. Create a new issue with detailed information
2. Include your Python version and operating system

---

**Happy Coding! 🚀** 