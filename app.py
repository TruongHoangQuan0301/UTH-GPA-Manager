"""
Main Flask application for GPA Calculator.
"""
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from api.gpa_routes import gpa_bp
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key

# Register blueprints
app.register_blueprint(gpa_bp, url_prefix='/api')

def get_db_connection():
    """Create a database connection."""
    conn = sqlite3.connect(os.path.join('data', 'user_gpa.db'))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the SQLite database."""
    db_path = os.path.join('data', 'user_gpa.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create grades table
    c.execute('''CREATE TABLE IF NOT EXISTS grades
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  semester INTEGER NOT NULL,
                  subject TEXT NOT NULL,
                  credits INTEGER NOT NULL,
                  grade_10 REAL NOT NULL,
                  grade_4 REAL NOT NULL)''')
    
    # Create a default test user if none exists
    c.execute('SELECT * FROM users WHERE username = ?', ('test',))
    if c.fetchone() is None:
        c.execute('INSERT INTO users (username, password, full_name) VALUES (?, ?, ?)',
                 ('test', generate_password_hash('test'), 'Test User'))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/result')

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', 
                          (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            user_obj = User(user['id'], user['username'], 
                          user['password'], user['full_name'])
            login_user(user_obj, remember=request.form.get('remember', False))
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password', 'error')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password request."""
    if request.method == 'POST':
        email = request.form.get('email')
        if not validate_student_email(email):
            flash('Please enter a valid UTH student email address.', 'error')
            return render_template('forgot_password.html')
        
        conn = get_db_connection()
        user = conn.execute('SELECT id, username FROM users WHERE email = ?', 
                          (email,)).fetchone()
        conn.close()
        
        if user:
            token = generate_reset_token()
            reset_token_expiry = datetime.utcnow() + timedelta(hours=24)
            
            conn = get_db_connection()
            conn.execute('INSERT INTO reset_tokens (user_id, token, created_at) VALUES (?, ?, ?)',
                     (user['id'], token, reset_token_expiry))
            conn.commit()
            conn.close()
            
            reset_link = url_for('reset_password', token=token, _external=True)
            send_reset_email(email, user['username'], reset_link)
            flash('Password reset instructions have been sent to your email.', 'success')
            return redirect(url_for('login'))
        else:
            flash('No account found with that email address.', 'error')
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset."""
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token)
        
        conn = get_db_connection()
        token_data = conn.execute('''SELECT user_id, created_at FROM reset_tokens 
                    WHERE token = ? AND created_at > ?''', 
                    (token, datetime.utcnow())).fetchone()
        
        if token_data:
            user_id = token_data['user_id']
            hashed_password = generate_password_hash(password)
            
            conn.execute('UPDATE users SET password = ? WHERE id = ?',
                     (hashed_password, user_id))
            conn.execute('DELETE FROM reset_tokens WHERE token = ?', (token,))
            conn.commit()
            conn.close()
            
            flash('Your password has been reset successfully. Please login with your new password.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid or expired password reset link.', 'error')
            return redirect(url_for('forgot_password'))
    
    # Verify token validity for GET request
    conn = get_db_connection()
    token_valid = conn.execute('''SELECT created_at FROM reset_tokens 
                WHERE token = ? AND created_at > ?''', 
                (token, datetime.utcnow())).fetchone() is not None
    conn.close()
    
    if not token_valid:
        flash('Invalid or expired password reset link.', 'error')
        return redirect(url_for('forgot_password'))
    
    return render_template('reset_password.html', token=token)

@app.route('/result')
@login_required
def result():
    """Display GPA calculation results."""
    return render_template('result.html')

if __name__ == '__main__':
    # Create database if it doesn't exist
    if not os.path.exists(os.path.join('data', 'user_gpa.db')):
        init_db()
    
    # Run the application
    app.run(debug=True)