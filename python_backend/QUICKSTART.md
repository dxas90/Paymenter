# Paymenter Python Backend - Quick Start Guide

Get the Python backend running in under 5 minutes!

## Option 1: Local Development (Fastest)

### Prerequisites
- Python 3.8 or higher
- MySQL/MariaDB running
- 5 minutes of your time

### Steps

1. **Navigate to Python backend directory**:
   ```bash
   cd python_backend
   ```

2. **Create and configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and set your database credentials
   nano .env  # or use your favorite editor
   ```

3. **Run the startup script**:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

4. **Access the API**:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

Done! 🎉

## Option 2: Docker (Easiest)

### Prerequisites
- Docker and Docker Compose
- 5 minutes of your time

### Steps

1. **Navigate to Python backend directory**:
   ```bash
   cd python_backend
   ```

2. **Generate a secure secret key**:
   ```bash
   openssl rand -hex 32
   # Copy the output
   ```

3. **Create environment file**:
   ```bash
   echo "SECRET_KEY=paste-your-secret-key-here" > .env
   ```

4. **Start with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

5. **Access the API**:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Database: localhost:3306

Done! 🎉

To stop:
```bash
docker-compose down
```

To view logs:
```bash
docker-compose logs -f api
```

## Option 3: Manual Installation

### Prerequisites
- Python 3.8+
- MySQL/MariaDB
- pip

### Steps

1. **Create virtual environment**:
   ```bash
   cd python_backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run the server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

Done! 🎉

## First API Call

### 1. Register a user:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePassword123",
    "first_name": "Admin",
    "last_name": "User"
  }'
```

### 2. Login:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=SecurePassword123"
```

Save the `access_token` from the response.

### 3. Get your profile:
```bash
curl -X GET "http://localhost:8000/api/v1/profile/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Troubleshooting

### "Database connection failed"
- Ensure MySQL/MariaDB is running
- Check DATABASE_URL in .env
- Verify database exists

### "Import error"
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### "Port 8000 already in use"
- Change port: `uvicorn app.main:app --port 8001`
- Or stop other process using port 8000

### "Permission denied on start.sh"
- Make it executable: `chmod +x start.sh`

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Read the full README**: See [README.md](README.md)
3. **Migration Guide**: Check [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
4. **Configure for production**: See production deployment section in README

## Production Considerations

Before deploying to production:

- [ ] Generate a strong SECRET_KEY (use `openssl rand -hex 32`)
- [ ] Set up proper database credentials
- [ ] Configure CORS for your frontend domain
- [ ] Use a production-grade database
- [ ] Set up SSL/TLS (HTTPS)
- [ ] Configure proper logging
- [ ] Set up monitoring
- [ ] Use multiple workers: `uvicorn app.main:app --workers 4`

## Getting Help

- **Documentation**: http://localhost:8000/docs (when running)
- **Issues**: https://github.com/dxas90/Paymenter/issues
- **Discord**: https://discord.gg/paymenter-882318291014651924
- **Website**: https://paymenter.org

Happy coding! 🚀
