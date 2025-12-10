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

BACKEND_API_URL = 'http://134.209.41.148:5001/api'


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

@app.route('/not-watched')
@require_login
def not_watched():

    try:
        user_email = session.get('user_email')
        response = requests.get(f'{BACKEND_API_URL}/movies/not-watched?user_email={user_email}')
        if response.status_code == 200:
            data = response.json()
            movies = data.get('movies', [])
        else:
            movies = []
    except Exception as e:
        flash(f'Error loading movies: {str(e)}', 'error')
        movies = []
   
    
    return render_template('not_watched.html', movies=movies)

@app.route('/movie/<movie_id>')
@require_login
def movie_detail(movie_id):
    """Movie detail page"""
    # TODO: Backend integration - Uncomment when ready
    try:
        user_email = session.get('user_email')
        response = requests.get(f'{BACKEND_API_URL}/movies/{movie_id}?user_email={user_email}')
        if response.status_code == 200:
            data = response.json()
            movie = data.get('movie')
        else:
            flash('Movie not found', 'error')
            return redirect(url_for('not_watched'))
    except Exception as e:
        flash(f'Error loading movie: {str(e)}', 'error')
        return redirect(url_for('not_watched'))
    
    
    
    
    if not movie:
        flash('Movie not found', 'error')
        return redirect(url_for('not_watched'))
    
    return render_template('movie_detail.html', movie=movie)

@app.route('/movie/<movie_id>/rate', methods=['POST'])
@require_login
def rate_movie(movie_id):
    """Rate a movie and mark as watched"""
    rating = request.form.get('rating')
    

    try:
        user_email = session.get('user_email')
        response = requests.put(
            f'{BACKEND_API_URL}/movies/{movie_id}/rate',
            json={
                'user_email': user_email,
                'rating': float(rating),
                'has_watched': True
            }
        )
        if response.status_code == 200:
            flash('Movie rated successfully!', 'success')
        else:
            flash('Failed to rate movie', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
   
    return redirect(url_for('not_watched'))

@app.route('/watched')
@require_login
def watched():
  
    try:
        user_email = session.get('user_email')
        response = requests.get(f'{BACKEND_API_URL}/movies/watched?user_email={user_email}')
        if response.status_code == 200:
            data = response.json()
            movies = data.get('movies', [])
        else:
            movies = []
    except Exception as e:
        flash(f'Error loading movies: {str(e)}', 'error')
        movies = []
    
    
    return render_template('watched.html', movies=movies)

@app.route('/confirm', methods=['GET', 'POST'])
@require_login
def confirm_movie():
    """Confirm and add recommended movie to list"""
    if request.method == 'POST':
        # Get form data
        movie_name = request.form.get('movie_name')
        movie_description = request.form.get('movie_description')
        runtime = request.form.get('runtime')
        

        try:
            user_email = session.get('user_email')
            response = requests.post(
                f'{BACKEND_API_URL}/movies/add',
                json={
                    'movie_name': movie_name,
                    'movie_description': movie_description,
                    'runtime': int(runtime) if runtime else None,
                    'user_email': user_email,
                    'has_watched': False,
                    'rating': None
                }
            )
            if response.status_code == 201:
                flash('Movie added to your watchlist!', 'success')
                return redirect(url_for('not_watched'))
            else:
                flash('Failed to add movie', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        
        flash(f'"{movie_name}" added to your watchlist! (Development mode)', 'success')
        return redirect(url_for('not_watched'))
    
    # GET request - get movie details from query params or session
    movie_name = request.args.get('movie_name', 'Recommended Movie')
    movie_description = request.args.get('description', 'A great movie recommendation from our AI!')
    runtime = request.args.get('runtime', '120')
    
    return render_template('confirm.html', 
                         movie_name=movie_name,
                         movie_description=movie_description,
                         runtime=runtime)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
