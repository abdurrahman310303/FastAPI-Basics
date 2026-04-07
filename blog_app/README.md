# Blog App

A complete blog application built with FastAPI, PostgreSQL, and JWT authentication.

## Features

- User registration and authentication
- JWT token-based authentication
- Create, read, update, and delete blog posts
- User-specific posts management
- Post search functionality
- Slug-based URLs for posts
- Published/draft post status
- Database migrations with Alembic

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL

### Installation

1. Create a virtual environment:
```bash
python -m venv blog_env
source blog_env/bin/activate  # On Windows: blog_env\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup PostgreSQL database:
```sql
CREATE DATABASE blog_db;
CREATE USER blog_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE blog_db TO blog_user;
```

4. Create environment file (.env):
```
DATABASE_URL=postgresql://blog_user:your_password@localhost/blog_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the application:
```bash
uvicorn main:app --reload
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user info

### Posts
- `GET /posts/` - Get all posts
- `GET /posts/search` - Search posts
- `GET /posts/my-posts` - Get current user's posts
- `POST /posts/` - Create new post
- `GET /posts/{post_id}` - Get post by ID
- `GET /posts/slug/{slug}` - Get post by slug
- `PUT /posts/{post_id}` - Update post
- `DELETE /posts/{post_id}` - Delete post

### Users
- `GET /users/` - Get all users
- `GET /users/{user_id}` - Get user by ID

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
blog_app/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── alembic/               # Database migrations
├── app/
│   ├── core/
│   │   ├── config.py      # Application configuration
│   │   └── dependencies.py # Authentication dependencies
│   ├── database/
│   │   ├── database.py    # Database connection
│   │   └── crud.py        # Database operations
│   ├── models/
│   │   └── models.py      # SQLAlchemy models
│   ├── routers/
│   │   ├── auth.py        # Authentication routes
│   │   ├── posts.py       # Post routes
│   │   └── users.py       # User routes
│   ├── schemas/
│   │   └── schemas.py     # Pydantic schemas
│   └── utils/
│       ├── auth.py        # Authentication utilities
│       └── helpers.py     # Helper functions
```
