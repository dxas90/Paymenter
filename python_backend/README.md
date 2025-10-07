# Paymenter Python Backend

This is a Python reimplementation of the Paymenter billing system backend using FastAPI.

## Features

- **FastAPI Framework**: Modern, fast, and well-documented Python web framework
- **RESTful API**: Complete REST API with authentication
- **OAuth2 Authentication**: Secure token-based authentication
- **Database Support**: SQLAlchemy ORM with MySQL/MariaDB support
- **API Documentation**: Auto-generated interactive API docs (Swagger UI)
- **Admin API**: Complete admin endpoints for managing users, services, invoices, and tickets

## Requirements

- Python 3.8 or higher
- MySQL/MariaDB database
- pip (Python package manager)

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   cd python_backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and secret key
   ```

5. **Generate a secure secret key**:
   ```bash
   openssl rand -hex 32
   # Copy the output and paste it as SECRET_KEY in .env
   ```

## Database Setup

The Python backend uses the same database schema as the PHP Laravel backend. You can either:

1. **Use existing Laravel database**: Just point DATABASE_URL to your existing Paymenter database
2. **Create a new database**: Create migrations using Alembic (future enhancement)

## Running the Application

### Development Server

Run the development server with auto-reload:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server

For production, use uvicorn with multiple workers:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, you can access:

- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI schema**: http://localhost:8000/api/v1/openapi.json

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login and get access token
- `POST /api/v1/auth/register` - Register a new user

### Admin - Users
- `GET /api/v1/admin/users` - List all users
- `POST /api/v1/admin/users` - Create a new user
- `GET /api/v1/admin/users/{user_id}` - Get user details
- `PUT /api/v1/admin/users/{user_id}` - Update user
- `DELETE /api/v1/admin/users/{user_id}` - Delete user

### Admin - Services
- `GET /api/v1/admin/services` - List all services
- `POST /api/v1/admin/services` - Create a new service
- `GET /api/v1/admin/services/{service_id}` - Get service details
- `PUT /api/v1/admin/services/{service_id}` - Update service
- `DELETE /api/v1/admin/services/{service_id}` - Delete service

### Admin - Invoices
- `GET /api/v1/admin/invoices` - List all invoices
- `POST /api/v1/admin/invoices` - Create a new invoice
- `GET /api/v1/admin/invoices/{invoice_id}` - Get invoice details
- `PUT /api/v1/admin/invoices/{invoice_id}` - Update invoice
- `DELETE /api/v1/admin/invoices/{invoice_id}` - Delete invoice

### Admin - Tickets
- `GET /api/v1/admin/tickets` - List all tickets
- `POST /api/v1/admin/tickets` - Create a new ticket
- `GET /api/v1/admin/tickets/{ticket_id}` - Get ticket details
- `PUT /api/v1/admin/tickets/{ticket_id}` - Update ticket
- `DELETE /api/v1/admin/tickets/{ticket_id}` - Delete ticket
- `POST /api/v1/admin/tickets/{ticket_id}/messages` - Add message to ticket

## Authentication

The API uses OAuth2 with JWT tokens. To authenticate:

1. **Get an access token**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user@example.com&password=yourpassword"
   ```

2. **Use the token in requests**:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/admin/users" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

## Project Structure

```
python_backend/
├── app/
│   ├── api/
│   │   ├── dependencies.py      # Shared dependencies (auth, etc.)
│   │   └── v1/
│   │       ├── endpoints/       # API endpoint modules
│   │       │   ├── auth.py
│   │       │   ├── users.py
│   │       │   ├── services.py
│   │       │   ├── invoices.py
│   │       │   └── tickets.py
│   │       └── router.py        # API router configuration
│   ├── core/
│   │   ├── config.py           # Configuration and settings
│   │   ├── database.py         # Database connection
│   │   └── security.py         # Security utilities
│   ├── models/
│   │   └── models.py           # SQLAlchemy models
│   ├── schemas/
│   │   └── schemas.py          # Pydantic schemas
│   └── main.py                 # FastAPI application
├── tests/                       # Test files (future)
├── .env.example                # Example environment variables
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Development

### Adding New Endpoints

1. Create a new endpoint file in `app/api/v1/endpoints/`
2. Define your routes using FastAPI decorators
3. Import and include the router in `app/api/v1/router.py`

### Adding New Models

1. Define your model in `app/models/models.py` using SQLAlchemy
2. Create corresponding Pydantic schemas in `app/schemas/schemas.py`
3. Create migrations (future enhancement with Alembic)

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (future enhancement)
pytest
```

## Docker Support (Future Enhancement)

A Dockerfile for the Python backend can be created for containerized deployment.

## Comparison with Laravel Backend

| Feature | Laravel (PHP) | FastAPI (Python) |
|---------|--------------|------------------|
| Framework | Laravel 12 | FastAPI |
| Language | PHP 8.2+ | Python 3.8+ |
| ORM | Eloquent | SQLAlchemy |
| API Docs | Scramble | Built-in (OpenAPI) |
| Authentication | Passport | OAuth2 + JWT |
| Performance | Good | Excellent (async) |
| Typing | Limited | Full (type hints) |

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- All endpoints are properly documented
- Tests are included for new features

## License

MIT License - Same as the main Paymenter project
