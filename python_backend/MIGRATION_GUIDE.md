# Python Backend Migration Guide

This guide helps you migrate from the PHP/Laravel backend to the Python/FastAPI backend or run both in parallel.

## Architecture Overview

### PHP/Laravel Backend
- **Framework**: Laravel 12
- **Language**: PHP 8.2+
- **ORM**: Eloquent
- **Web Server**: PHP-FPM + Nginx/Apache
- **Authentication**: Laravel Passport (OAuth2)
- **Frontend**: Livewire components

### Python/FastAPI Backend
- **Framework**: FastAPI
- **Language**: Python 3.8+
- **ORM**: SQLAlchemy
- **Web Server**: Uvicorn (ASGI)
- **Authentication**: OAuth2 with JWT
- **Frontend**: Compatible with existing frontend (API only)

## Database Compatibility

Both backends use the **same database schema**, which means:
- You can switch between backends without data migration
- You can run both backends simultaneously (useful for gradual migration)
- All tables, relationships, and constraints are identical

## API Endpoint Mapping

The Python backend provides equivalent endpoints to the Laravel backend:

### Authentication
| Laravel | Python FastAPI |
|---------|----------------|
| `POST /oauth/token` | `POST /api/v1/auth/login` |
| `POST /register` | `POST /api/v1/auth/register` |

### Profile
| Laravel | Python FastAPI |
|---------|----------------|
| `GET /api/me` | `GET /api/v1/profile/me` |

### Admin - Users
| Laravel | Python FastAPI |
|---------|----------------|
| `GET /api/v1/admin/users` | `GET /api/v1/admin/users` |
| `POST /api/v1/admin/users` | `POST /api/v1/admin/users` |
| `GET /api/v1/admin/users/{id}` | `GET /api/v1/admin/users/{id}` |
| `PUT /api/v1/admin/users/{id}` | `PUT /api/v1/admin/users/{id}` |
| `DELETE /api/v1/admin/users/{id}` | `DELETE /api/v1/admin/users/{id}` |

### Admin - Services
| Laravel | Python FastAPI |
|---------|----------------|
| `GET /api/v1/admin/services` | `GET /api/v1/admin/services` |
| `POST /api/v1/admin/services` | `POST /api/v1/admin/services` |
| `GET /api/v1/admin/services/{id}` | `GET /api/v1/admin/services/{id}` |
| `PUT /api/v1/admin/services/{id}` | `PUT /api/v1/admin/services/{id}` |
| `DELETE /api/v1/admin/services/{id}` | `DELETE /api/v1/admin/services/{id}` |

### Admin - Orders, Invoices, Tickets
Similar mappings apply for all other resources.

## Migration Strategies

### Strategy 1: Complete Migration (Recommended for new installations)

1. **Fresh Installation**:
   ```bash
   cd python_backend
   cp .env.example .env
   # Edit .env with your database credentials
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Database**: Use existing Paymenter database or create a new one with the same schema

3. **Test**: Verify all endpoints work correctly

4. **Deploy**: Replace PHP backend with Python backend

### Strategy 2: Parallel Operation (Recommended for existing installations)

Run both backends simultaneously during migration:

1. **PHP Backend**: Keep running on port 80/443
2. **Python Backend**: Run on a different port (e.g., 8000)
3. **Gradually migrate services** to use the Python API
4. **Monitor both** backends for consistency
5. **Switch completely** when ready

Example Nginx configuration:
```nginx
# PHP Backend
location /api/php/ {
    proxy_pass http://localhost:9000;
}

# Python Backend
location /api/v1/ {
    proxy_pass http://localhost:8000;
}
```

### Strategy 3: Feature-by-Feature Migration

1. Start with **read-only endpoints** (GET requests)
2. Verify data consistency
3. Migrate **write endpoints** (POST, PUT, DELETE)
4. Test thoroughly
5. Switch over when confident

## Performance Comparison

### Benchmarks (approximate)

| Metric | PHP/Laravel | Python/FastAPI |
|--------|-------------|----------------|
| Requests/sec | ~100-500 | ~1000-3000 |
| Response time | 50-200ms | 10-50ms |
| Memory usage | 50-100MB | 30-60MB |
| Concurrency | Limited | Excellent (async) |

*Note: Actual performance depends on configuration and workload*

## Feature Parity

### Implemented in Python Backend
- ✅ User authentication (OAuth2 + JWT)
- ✅ User management (CRUD)
- ✅ Service management (CRUD)
- ✅ Order management (CRUD)
- ✅ Invoice management (CRUD)
- ✅ Ticket management (CRUD)
- ✅ Ticket messages
- ✅ Admin authorization
- ✅ CORS configuration
- ✅ Database ORM (SQLAlchemy)
- ✅ API documentation (Swagger UI)
- ✅ Docker support

### Not Yet Implemented (Future Work)
- ⚠️ Email notifications
- ⚠️ Payment gateway integrations
- ⚠️ Cron jobs/scheduled tasks
- ⚠️ Extension system
- ⚠️ Two-factor authentication
- ⚠️ Social login
- ⚠️ Advanced reporting
- ⚠️ Audit logging
- ⚠️ File uploads
- ⚠️ Webhooks

## Code Examples

### Authentication in PHP/Laravel
```php
Route::post('/oauth/token', [
    'uses' => 'Laravel\Passport\Http\Controllers\AccessTokenController@issueToken',
]);
```

### Authentication in Python/FastAPI
```python
@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Authentication logic
    return {"access_token": token, "token_type": "bearer"}
```

### Creating a User in PHP/Laravel
```php
public function store(CreateUserRequest $request)
{
    $user = User::create($request->validated());
    return new UserResource($user);
}
```

### Creating a User in Python/FastAPI
```python
@router.post("/", response_model=User)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    db_user = UserModel(**user_data.model_dump())
    db.add(db_user)
    db.commit()
    return db_user
```

## Testing Both Backends

### Test PHP Backend
```bash
# Login
curl -X POST http://localhost/api/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=user@example.com&password=password"

# Get users
curl http://localhost/api/v1/admin/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Python Backend
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password"

# Get users
curl http://localhost:8000/api/v1/admin/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Troubleshooting

### Python Backend Issues

**Issue**: Database connection error
```
Solution: Check DATABASE_URL in .env file
Verify MySQL/MariaDB is running
Ensure database exists
```

**Issue**: Import errors
```
Solution: Ensure all dependencies are installed
pip install -r requirements.txt
Check Python version (3.8+)
```

**Issue**: Authentication fails
```
Solution: Verify SECRET_KEY in .env
Check token expiration settings
Ensure user exists and password is correct
```

### PHP Backend Issues

**Issue**: Composer dependencies
```
Solution: Run composer install
Check PHP version (8.2+)
```

**Issue**: Laravel passport
```
Solution: Run php artisan passport:install
Check oauth tables exist
```

## Monitoring & Logging

### Python Backend
- Logs to stdout/stderr (use with systemd, docker logs, etc.)
- Can integrate with logging libraries (loguru, python-json-logger)
- Built-in health check endpoint: `/health`

### PHP Backend
- Laravel logs in `storage/logs/laravel.log`
- Web server logs (nginx, apache)
- Debug bar available in development

## Production Deployment

### Python Backend with Docker
```bash
cd python_backend
docker build -t paymenter-python .
docker run -p 8000:8000 --env-file .env paymenter-python
```

### Python Backend with Systemd
```ini
[Unit]
Description=Paymenter Python Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/paymenter/python_backend
Environment="PATH=/var/www/paymenter/python_backend/venv/bin"
ExecStart=/var/www/paymenter/python_backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Python Backend with Nginx
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Support & Contributing

For issues specific to the Python backend:
1. Check the [Python Backend README](README.md)
2. Open an issue on GitHub
3. Join the Discord community

For general Paymenter questions:
- Visit https://paymenter.org
- Check the documentation
- Join Discord: https://discord.gg/paymenter-882318291014651924

## Next Steps

1. **Try the Python backend** locally
2. **Compare API responses** between PHP and Python
3. **Report any inconsistencies**
4. **Contribute improvements**
5. **Share your experience**

The Python backend is a complete reimplementation designed to provide better performance and maintainability while maintaining full compatibility with the existing Paymenter ecosystem.
