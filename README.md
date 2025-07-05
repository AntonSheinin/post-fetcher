# Post Fetcher API

A FastAPI application that fetches posts and comments from an external API (JSONPlaceholder), stores them in MongoDB, and provides a REST API with JWT authentication for managing the data.

## Features

- **Automated Data Fetching**: Background task that periodically fetches posts and comments from JSONPlaceholder API
- **MongoDB Integration**: Stores posts and comments with proper indexing
- **JWT Authentication**: Secure endpoints with JWT token authentication
- **REST API**: CRUD operations for posts and comments
- **Interactive Documentation**: Swagger UI with authentication support
- **Docker Support**: Containerized application with Docker Compose

## Running with Docker

1. Start the application:
```bash
docker-compose up --build
```

2. Access the API:
- **Swagger UI**: http://localhost:8000/docs
- **API Base**: http://localhost:8000

### Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start MongoDB (using Docker):
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

3. Run the application:
```bash
python main.py
```

## API Endpoints

### Authentication
- `POST /auth/login` - Get JWT token (dev endpoint)
- `GET /auth/me` - Get current user info

### Posts & Comments
- `GET /posts/{post_id}` - Get specific post without comments
- `GET /posts/{post_id}/comments` - Get comments for a specific post
- `PUT /posts/{post_id}` - Update post content (requires authentication)
- `GET /posts/comments/{comment_id}` - Get specific comment
- `GET /posts/comments/search` - Search comments by text
- `GET /posts/count` - Get post count with optional date filtering

### Background Fetcher Management
- `GET /fetcher/start` - Start background fetcher
- `GET /fetcher/stop` - Stop background fetcher
- `GET /fetcher/status` - Get fetcher status

### Database Management
- `GET /mongo/all` - Get all records from database
- `GET /mongo/clear` - Clear all data from database

## Authentication

The API uses JWT token authentication for protected endpoints.

### Getting a Token

1. Go to Swagger UI: http://localhost:8000/docs
2. Use the `/auth/login` endpoint with any `user_id` (e.g., 123)
3. Copy the returned `access_token`

### Using the Token

1. Click the **"Authorize"** button in Swagger UI
2. Paste the token in the "Value" field
3. Click "Authorize"
4. Protected endpoints will now include the Authorization header

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POST_SOURCE_URL` | External API base URL | `https://jsonplaceholder.typicode.com` |
| `MONGODB_URL` | MongoDB connection string | `mongodb://mongodb:27017` |
| `DATABASE_NAME` | Database name | `posts_db` |
| `FETCH_INTERVAL_SECONDS` | Fetcher interval in seconds | `60` |
| `MAX_POSTS_PER_FETCH` | Maximum posts to fetch per cycle | `10` |
| `RANDOM_DATE_RANGE_DAYS` | Date range for random timestamps | `365` |
| `JWT_SECRET_KEY` | JWT signing secret | `MySecretJWTKey` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time in minutes | `30` |

## Background Processing

The application includes a background task that:
1. Fetches posts from JSONPlaceholder API
2. Fetches comments for each post
3. Generates random timestamps for posts and comments
4. Stores only new posts (checks existing `post_id`)
5. Respects the `MAX_POSTS_PER_FETCH` limit

### Managing the Background Task

- **Start**: `GET /fetcher/start`
- **Stop**: `GET /fetcher/stop`
- **Status**: `GET /fetcher/status`