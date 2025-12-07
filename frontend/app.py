"""
Frontend Flask Application for Movie Recommendation System
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:5001/api')


def is_logged_in():
    """Check if user is logged in"""
    return 'user_email' in session


def require_login(func):
    """Decorator to require login for routes"""
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/')
def index():
    """Redirect to login if not logged in, otherwise go to home"""
    if is_logged_in():
        return redirect(url_for('home'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # TODO: Integrate with backend when ready
        # Uncomment below when backend API is ready:
        """
        try:
            response = requests.post(f'{BACKEND_API_URL}/auth/login', 
                                    json={'email': email, 'password': password})
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    session['user_email'] = email
                    flash('Login successful!', 'success')
                    return redirect(url_for('home'))
            flash('Invalid credentials', 'error')
        except Exception as e:
            flash(f'Error connecting to server: {str(e)}', 'error')
        """
        
        # TEMPORARY: Development mode
        if email and password:
            session['user_email'] = email
            flash('Login successful! (Development mode)', 'success')
            return redirect(url_for('home'))
        else:
            flash('Please enter both email and password', 'error')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([fname, lname, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        # TODO: Integrate with backend when ready
        # Uncomment below when backend API is ready:
        """
        try:
            response = requests.post(f'{BACKEND_API_URL}/auth/register',
                                    json={'fname': fname, 'lname': lname, 
                                          'email': email, 'password': password})
            if response.status_code == 201:
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            flash('Registration failed', 'error')
        except Exception as e:
            flash(f'Error connecting to server: {str(e)}', 'error')
        """
        
        # TEMPORARY: Development mode
        flash('Registration successful! Please login. (Development mode)', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))


@app.route('/home')
@require_login
def home():
    """Main chatbot page"""
    return render_template('home.html', user_email=session.get('user_email'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
