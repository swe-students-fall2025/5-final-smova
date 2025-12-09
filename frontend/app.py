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

@app.route('/not-watched')
@require_login
def not_watched():
    """Not watched movies list page"""
    # TODO: Backend integration - Uncomment when ready
    """
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
    """
    
    # TEMPORARY: Mock data for development
    movies = [
        {
            'movie_id': '1',
            'movie_name': 'Inception',
            'movie_description': 'A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.',
            'runtime': 148,
            'has_watched': False
        },
        {
            'movie_id': '2',
            'movie_name': 'The Shawshank Redemption',
            'movie_description': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
            'runtime': 142,
            'has_watched': False
        },
        {
            'movie_id': '3',
            'movie_name': 'Interstellar',
            'movie_description': 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.',
            'runtime': 169,
            'has_watched': False
        }
    ]
    
    return render_template('not_watched.html', movies=movies)

@app.route('/movie/<movie_id>')
@require_login
def movie_detail(movie_id):
    """Movie detail page"""
    # TODO: Backend integration - Uncomment when ready
    """
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
    """
    
    # TEMPORARY: Mock data for development
    mock_movies = {
        '1': {
            'movie_id': '1',
            'movie_name': 'Inception',
            'movie_description': 'A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.',
            'runtime': 148,
            'has_watched': False,
            'rating': None
        },
        '2': {
            'movie_id': '2',
            'movie_name': 'The Shawshank Redemption',
            'movie_description': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
            'runtime': 142,
            'has_watched': False,
            'rating': None
        },
        '3': {
            'movie_id': '3',
            'movie_name': 'Interstellar',
            'movie_description': 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.',
            'runtime': 169,
            'has_watched': False,
            'rating': None
        },
        '4': {
            'movie_id': '4',
            'movie_name': 'The Dark Knight',
            'movie_description': 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.',
            'runtime': 152,
            'has_watched': True,
            'rating': 9.0
        },
        '5': {
            'movie_id': '5',
            'movie_name': 'Pulp Fiction',
            'movie_description': 'The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.',
            'runtime': 154,
            'has_watched': True,
            'rating': 8.5
        },
        '6': {
            'movie_id': '6',
            'movie_name': 'Forrest Gump',
            'movie_description': 'The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75.',
            'runtime': 142,
            'has_watched': True,
            'rating': 8.8
        }
    }
    
    movie = mock_movies.get(movie_id)
    
    if not movie:
        flash('Movie not found', 'error')
        return redirect(url_for('not_watched'))
    
    return render_template('movie_detail.html', movie=movie)

@app.route('/movie/<movie_id>/rate', methods=['POST'])
@require_login
def rate_movie(movie_id):
    """Rate a movie and mark as watched"""
    rating = request.form.get('rating')
    
    # TODO: Backend integration - Uncomment when ready
    """
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
    """
    
    # TEMPORARY: Development mode
    flash(f'Movie rated {rating}/10! (Development mode)', 'success')
    return redirect(url_for('not_watched'))

@app.route('/watched')
@require_login
def watched():
    """Watched movies list page"""
    # TODO: Backend integration - Uncomment when ready
    """
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
    """
    
    # TEMPORARY: Mock data for development
    movies = [
        {
            'movie_id': '4',
            'movie_name': 'The Dark Knight',
            'movie_description': 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests.',
            'runtime': 152,
            'has_watched': True,
            'rating': 9.0
        },
        {
            'movie_id': '5',
            'movie_name': 'Pulp Fiction',
            'movie_description': 'The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.',
            'runtime': 154,
            'has_watched': True,
            'rating': 8.5
        },
        {
            'movie_id': '6',
            'movie_name': 'Forrest Gump',
            'movie_description': 'The presidencies of Kennedy and Johnson, the Vietnam War, and other historical events unfold from the perspective of an Alabama man.',
            'runtime': 142,
            'has_watched': True,
            'rating': 8.8
        }
    ]
    
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
        
        # TODO: Backend integration - Uncomment when ready
        """
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
        """
        
        # TEMPORARY: Development mode
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
