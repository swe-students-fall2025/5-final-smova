# Movie Recommender

[![Backend CI/CD](https://github.com/software-students-fall2024/4-containers-swe/actions/workflows/backend-ci-cd.yml/badge.svg)](https://github.com/software-students-fall2024/4-containers-swe/actions/workflows/backend-ci-cd.yml)
[![Frontend CI/CD](https://github.com/software-students-fall2024/4-containers-swe/actions/workflows/frontend-ci-cd.yml/badge.svg)](https://github.com/software-students-fall2024/4-containers-swe/actions/workflows/frontend-ci-cd.yml)

An AI-powered movie recommendation system that helps users discover and manage their movie watchlist. The application uses Google's Gemini AI for intelligent recommendations and Weaviate vector database for semantic movie search through a RAG (Retrieval-Augmented Generation) pipeline.

## Features

- **AI-Powered Recommendations**: Chat with Gemini AI to get personalized movie suggestions based on your preferences
- **User Authentication**: Secure registration and login system with JWT token authentication
- **Watchlist Management**: Maintain separate "Watched" and "Not Watched" lists
- **Movie Rating**: Rate movies you've watched and track your viewing history
- **Semantic Search**: Advanced movie discovery using Weaviate's vector database for contextual search
- **Movie Details**: View comprehensive information about each movie including descriptions, runtime, and ratings
- **Conversation History**: Persistent chat conversations with the AI recommender

## Team Members
- [Aayan Mathur](https://github.com/aayanmathur)
- [Matthew Membreno](https://github.com/m9membreno)
- [Vaishnavi Suresh](https://github.com/vaishnavi-suresh)
- [Susan Wang](https://github.com/sw5556)

## Docker Images

This application uses containerized deployment. Docker images are built automatically via CI/CD pipelines:

- **Backend API**: `movie-recommender-backend:latest`
- **Frontend Application**: `movie-recommender-frontend:latest`

The application is deployed directly on a Digital Ocean droplet using Docker containers.

## Live Deployment

**Production URL**: http://134.209.41.148:8000

- **Frontend**: http://134.209.41.148:8000
- **Backend API**: http://134.209.41.148:5001/api
- **Weaviate**: http://134.209.41.148:8080

## Architecture

The application consists of four main containerized subsystems:

### 1. Frontend (Flask Web Application)
- **Technology**: Python Flask with Jinja2 templates
- **Port**: 8000
- **Purpose**: Serves the user interface and handles client-side interactions

### 2. Backend (Flask REST API)
- **Technology**: Python Flask
- **Port**: 5001
- **Purpose**: Handles authentication, movie data management, and AI chat integration
- **API Documentation**: See [API Endpoints](#-api-endpoints) section

### 3. MongoDB
- **Version**: 7.0
- **Port**: 27017
- **Purpose**: Document database storing user accounts, movies, ratings, and chat conversations
- **Collections**: `users`, `movies`, `messages`, `conversations`

### 4. Weaviate Vector Database
- **Version**: 1.34.4
- **Port**: 8080
- **Purpose**: Vector database with semantic search capabilities for movie recommendations
- **Module**: text2vec-contextionary for natural language processing

## Prerequisites

Before running this project, ensure you have:

- **Python 3.11** or higher
- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Google Gemini API Key** - Get one from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Git**

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/software-students-fall2024/4-containers-swe.git
cd 4-containers-swe
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:
```bash
cp backend/.env.example .env
```

Edit the `.env` file with your configuration:
```env
# MongoDB
MONGO_URI=mongodb://mongo:27017
TESTING=0

# Flask
FLASK_SECRET_KEY=your-secret-key-change-this-to-random-string
JWT_SECRET_KEY=your-jwt-secret-change-this-to-random-string
JWT_EXPIRATION_HOURS=24

# API
API_PORT=5001
API_HOST=0.0.0.0

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key-here

# CORS
CORS_ORIGINS=http://localhost:8000,http://frontend:8000

# Weaviate
WEAVIATE_URL=http://weaviate:8080
```

**Important**: Replace the following values:
- `FLASK_SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- `JWT_SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- `GEMINI_API_KEY`: Your actual Gemini API key from Google AI Studio

### 3. Start All Services
```bash
docker-compose up --build
```

This command will:
- Build Docker images for frontend and backend
- Pull MongoDB and Weaviate images
- Start all containers with proper networking
- Initialize databases

**Services will be available at:**
- Frontend: http://localhost:8000
- Backend API: http://localhost:5001
- MongoDB: localhost:27017
- Weaviate: http://localhost:8080

### 4. Seed the Movie Database (Required)

The application requires movie data to be seeded into Weaviate for recommendations to work. This loads the `mt0rm0/movie_descriptors` dataset into the vector database.

**Option A: Using Docker (Recommended)**
```bash
docker exec -it movie-app-backend python scripts/seed_db.py
```

**Option B: Locally**
```bash
cd backend
pip install -r requirements.txt
python scripts/seed_db.py
```

This process may take a few minutes as it loads movie descriptions into the vector database.

### 5. Access the Application

Open your browser and navigate to http://localhost:8000

1. **Register** a new account
2. **Log in** with your credentials
3. **Chat** with the AI to get movie recommendations
4. **Confirm** recommended movies to add them to your watchlist
5. **Rate** movies after watching them

## Running Tests

### Backend Tests
```bash
cd backend
python -m pip install -r requirements.txt
python -m pytest tests/ --cov=. --cov-report=term-missing
```

**Current Coverage**: >80% 

**Test Categories:**
- Authentication routes (`test_auth_routes.py`)
- Movie management routes (`test_movies_routes.py`)
- Chat functionality (`test_chat_routes.py`)
- Data Access Layer (`test_DAL.py`)
- Validators (`test_validators.py`)
- Authentication helpers (`test_auth_helpers.py`)

### Frontend Tests
```bash
cd frontend
python -m pip install -r requirements.txt
python -m pytest tests/ --cov=app --cov-report=term-missing
```

**Current Coverage**: >80% 

### Running Tests in Docker
```bash
# Backend tests
docker-compose run backend python -m pytest tests/ --cov=. --cov-report=term

# Frontend tests
docker-compose run app python -m pytest tests/ --cov=app --cov-report=term
```

## Project Structure
```
.
├── backend/                      # Flask REST API Backend
│   ├── routes/
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── movies.py            # Movie management endpoints
│   │   └── chat.py              # AI chat endpoints
│   ├── utils/
│   │   ├── auth_helpers.py      # JWT and password utilities
│   │   └── validators.py        # Input validation
│   ├── tests/                   # Backend unit tests (>80% coverage)
│   │   ├── test_auth_routes.py
│   │   ├── test_movies_routes.py
│   │   ├── test_chat_routes.py
│   │   ├── test_DAL.py
│   │   ├── test_validators.py
│   │   └── conftest.py
│   ├── scripts/
│   │   └── seed_db.py           # Weaviate database seeding
│   ├── DAL.py                   # Data Access Layer
│   ├── ml_client.py             # Gemini AI integration
│   ├── app.py                   # Flask application entry point
│   ├── config.py                # Configuration management
│   ├── Dockerfile               # Backend container definition
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Environment variables template
│
├── frontend/                     # Flask Web Application
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── home.html
│   │   ├── not_watched.html
│   │   ├── watched.html
│   │   ├── movie_detail.html
│   │   └── confirm.html
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css       # Application styling
│   │   └── js/
│   │       └── script.js        # Client-side JavaScript
│   ├── tests/                   # Frontend unit tests (>80% coverage)
│   │   └── test_app.py
│   ├── app.py                   # Flask application entry point
│   ├── Dockerfile               # Frontend container definition
│   └── requirements.txt         # Python dependencies
│
├── .github/
│   └── workflows/               # CI/CD Pipeline Definitions
│       ├── backend-ci-cd.yml    # Backend build, test, deploy
│       └── frontend-ci-cd.yml   # Frontend build, test, deploy
│
├── docker-compose.yaml          # Multi-container orchestration
├── schema.js                    # MongoDB schema definitions
├── .gitignore
└── README.md
```

## Development Setup

### Running Services Individually (Without Docker)

#### Prerequisites for Local Development
```bash
# Install Python dependencies
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt

# Ensure MongoDB and Weaviate are running
# Option 1: Use Docker for databases only
docker-compose up mongo weaviate contextionary

# Option 2: Install MongoDB and Weaviate locally
```

#### Backend Development Server
```bash
cd backend
python app.py
# Runs on http://localhost:5001
```

#### Frontend Development Server
```bash
cd frontend
python app.py
# Runs on http://localhost:8000
```

### Hot Reload for Development

The Docker Compose configuration supports volume mounting for development. To enable hot reload:
```yaml
# In docker-compose.yaml, add volumes to backend/frontend services:
volumes:
  - ./backend:/app
  - ./frontend:/app
```

## API Endpoints

### Authentication

#### POST `/api/auth/register`
Register a new user account.

**Request:**
```json
{
  "fname": "John",
  "lname": "Doe",
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "User registered successfully"
}
```

**Response (Error):**
```json
{
  "success": false,
  "message": "Email already exists"
}
```

#### POST `/api/auth/login`
Authenticate user and receive JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (Success):**
```json
{
  "success": true,
  "user_email": "user@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (Error):**
```json
{
  "success": false,
  "message": "Invalid credentials"
}
```

### Movies

#### GET `/api/movies/not-watched`
Retrieve user's unwatched movies.

**Query Parameters:**
- `user_email` (required): User's email address

**Response:**
```json
{
  "success": true,
  "movies": [
    {
      "movie_id": 1,
      "movie_name": "Inception",
      "movie_description": "A thief who steals corporate secrets...",
      "has_watched": false,
      "rating": null
    }
  ]
}
```

#### GET `/api/movies/watched`
Retrieve user's watched movies with ratings.

**Query Parameters:**
- `user_email` (required): User's email address

**Response:**
```json
{
  "success": true,
  "movies": [
    {
      "movie_id": 2,
      "movie_name": "The Matrix",
      "movie_description": "A computer hacker learns...",
      "has_watched": true,
      "rating": 5
    }
  ]
}
```

#### GET `/api/movies/<movie_id>`
Get details for a specific movie.

**Response:**
```json
{
  "success": true,
  "movie": {
    "movie_id": 1,
    "movie_name": "Inception",
    "movie_description": "A thief who steals corporate secrets...",
    "has_watched": false,
    "rating": null
  }
}
```

#### POST `/api/movies/add`
Add a new movie to user's list.

**Request:**
```json
{
  "user_email": "user@example.com",
  "movie_name": "Inception",
  "movie_description": "A thief who steals corporate secrets...",
  "has_watched": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Movie added successfully",
  "movie_id": 1
}
```

#### PUT `/api/movies/<movie_id>/rate`
Rate a watched movie.

**Request:**
```json
{
  "rating": 5,
  "user_email": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Movie rated successfully"
}
```

### Chat

#### POST `/api/chat/message`
Send message to AI recommender and get response.

**Request:**
```json
{
  "user_email": "user@example.com",
  "message": "I want to watch a sci-fi thriller",
  "convo_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "response": "Based on your preference for sci-fi thrillers, I recommend...",
  "movie_recommendation": {
    "movie_name": "Inception",
    "movie_description": "A thief who steals corporate secrets..."
  }
}
```

## 🗄️ Database Schema

### MongoDB Collections

#### Users Collection
```javascript
{
  fname: String,
  lname: String,
  email: {
    type: String,
    required: true,
    unique: true
  },
  password: String  // bcrypt hashed
}
```

#### Movies Collection
```javascript
{
  movie_name: String,
  movie_id: {
    type: Number,
    required: true,
    unique: true
  },
  movie_description: String,
  has_watched: Boolean,
  rating: Number,  // 1-5 stars
  user_email: String  // Foreign key to users
}
```

#### Messages Collection
```javascript
{
  timestamp: {
    type: Date,
    default: Date.now
  },
  content: String,
  role: ["user", "model"],
  convo_id: {
    type: Number,
    required: true
  }
}
```

#### Conversations Collection
```javascript
{
  user_email: String,
  convo_id: {
    type: Number,
    required: true,
    unique: true
  },
  messages: [Message]
}
```

### Weaviate Schema

#### Movies Class
```javascript
{
  class: "Movies",
  properties: [
    {
      name: "title",
      dataType: ["text"]
    },
    {
      name: "description",
      dataType: ["text"]
    }
  ],
  vectorizer: "text2vec-contextionary"
}
```

## Environment Variables Reference

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `MONGO_URI` | MongoDB connection string | Yes | - | `mongodb://mongo:27017` |
| `TESTING` | Enable test mode (uses mock data) | No | `0` | `0` or `1` |
| `FLASK_SECRET_KEY` | Flask session encryption key | Yes | - | 32+ character random string |
| `JWT_SECRET_KEY` | JWT token signing key | Yes | - | 32+ character random string |
| `JWT_EXPIRATION_HOURS` | JWT token validity period | No | `24` | `24` |
| `API_PORT` | Backend API port | No | `5001` | `5001` |
| `API_HOST` | Backend API host | No | `0.0.0.0` | `0.0.0.0` |
| `GEMINI_API_KEY` | Google Gemini API key | Yes | - | From Google AI Studio |
| `CORS_ORIGINS` | Allowed frontend origins | Yes | - | `http://localhost:8000` |
| `WEAVIATE_URL` | Weaviate instance URL | Yes | - | `http://weaviate:8080` |
| `BACKEND_API_URL` | Backend API URL (frontend) | Yes | - | `http://backend:5001/api` |

### How to Get API Keys

#### Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key to your `.env` file

## CI/CD Pipeline

### GitHub Actions Workflows

The project uses GitHub Actions for continuous integration and deployment:

#### Backend Pipeline (`backend-ci-cd.yml`)
**Triggers:** Push or PR to `main`/`master` branches affecting `backend/` directory

**Steps:**
1. **Test**: Run pytest with >80% coverage requirement
2. **Build**: Create Docker image and push to registry
3. **Deploy**: Deploy to Digital Ocean droplet via SSH

#### Frontend Pipeline (`frontend-ci-cd.yml`)
**Triggers:** Push or PR to `main`/`master` branches affecting `frontend/` directory

**Steps:**
1. **Test**: Run pytest with >80% coverage requirement
2. **Build**: Create Docker image and push to registry
3. **Deploy**: Deploy to Digital Ocean droplet via SSH

### Required Secrets

Configure these secrets in GitHub repository settings:

- `DOCKERHUB_USERNAME`: Docker Hub username
- `DOCKERHUB_TOKEN`: Docker Hub access token
- `DIGITALOCEAN_HOST`: Droplet IP address
- `DIGITALOCEAN_USERNAME`: SSH username (typically `root`)
- `DIGITALOCEAN_SSH_KEY`: Private SSH key for droplet access
- `DIGITALOCEAN_PORT`: SSH port (default: 22)
- `MONGO_URI`: Production MongoDB URI
- `FLASK_SECRET_KEY`: Production Flask secret
- `JWT_SECRET_KEY`: Production JWT secret
- `GEMINI_API_KEY`: Production Gemini API key
- `WEAVIATE_URL`: Production Weaviate URL
- `CORS_ORIGINS`: Production frontend URL
- `BACKEND_API_URL`: Production backend URL

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
lsof -i :8000
lsof -i :5001

# Kill the process or stop conflicting containers
docker-compose down
```

#### Database Connection Error
```bash
# Ensure MongoDB is running
docker ps | grep mongo

# Check MongoDB logs
docker logs movie-app-mongodb

# Restart MongoDB container
docker-compose restart mongo
```

#### Weaviate Not Responding
```bash
# Check Weaviate logs
docker logs movie-app-weaviate

# Weaviate takes time to start, wait 30-60 seconds
docker-compose up -d weaviate
sleep 60
```

#### "Module not found" Errors
```bash
# Reinstall dependencies
cd backend
pip install -r requirements.txt

cd ../frontend
pip install -r requirements.txt
```

#### Tests Failing
```bash
# Ensure test environment variables are set
export TESTING=1
export MONGO_URI=mongodb://localhost:27017
export FLASK_SECRET_KEY=test-key
export JWT_SECRET_KEY=test-jwt-key
export GEMINI_API_KEY=mock-key-for-tests

# Run tests with verbose output
pytest -v tests/
```

## Development Guidelines

### Adding New Features

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Write tests first (TDD approach recommended)
3. Implement the feature
4. Ensure tests pass with >80% coverage
5. Update documentation
6. Submit a pull request

### Code Style

- **Python**: Follow PEP 8 style guide
- **JavaScript**: Use ES6+ syntax
- **HTML/CSS**: Follow BEM naming convention
- **Commits**: Use conventional commit messages

### Testing Requirements

- Maintain minimum 80% code coverage
- Write unit tests for all new functions
- Include integration tests for API endpoints
- Mock external services (Gemini AI, Weaviate) in tests

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Google Gemini AI** for powering intelligent movie recommendations
- **Weaviate** for vector database and semantic search capabilities
- **HuggingFace** for the `mt0rm0/movie_descriptors` dataset
- **Docker** for containerization support
- **Digital Ocean** for hosting infrastructure
- **NYU** for academic guidance and support

## Support

For questions or issues:
- Open an issue on GitHub
- Contact team members via GitHub profiles
- Check existing documentation and troubleshooting guide

---

**Built by Team Smova**