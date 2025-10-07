"""
Tests for authentication endpoints.
"""
import pytest


def test_register_user(client):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["first_name"] == "Test"
    assert "password" not in data  # Password should not be returned


def test_login(client):
    """Test user login."""
    # First, register a user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "LoginPassword123",
            "first_name": "Login",
            "last_name": "Test"
        }
    )
    
    # Then, try to login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@example.com",
            "password": "LoginPassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "WrongPassword123"
        }
    )
    assert response.status_code == 401


def test_register_duplicate_email(client):
    """Test registering with a duplicate email."""
    user_data = {
        "email": "duplicate@example.com",
        "password": "Password123",
        "first_name": "Duplicate",
        "last_name": "User"
    }
    
    # First registration should succeed
    response1 = client.post("/api/v1/auth/register", json=user_data)
    assert response1.status_code == 201
    
    # Second registration with same email should fail
    response2 = client.post("/api/v1/auth/register", json=user_data)
    assert response2.status_code == 400
