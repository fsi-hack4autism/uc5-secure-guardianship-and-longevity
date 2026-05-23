"""
Tests for authentication endpoints
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestSignUp:
    """Sign up endpoint tests"""
    
    def test_signup_success(self):
        """Test successful user signup"""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "SecurePassword123!",
                "user_type": "guardian",
                "full_name": "New Guardian",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user_type"] == "guardian"
        assert data["token_type"] == "bearer"
    
    def test_signup_duplicate_email(self):
        """Test signup with existing email"""
        # First signup
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "duplicate@example.com",
                "password": "Password123!",
                "user_type": "beneficiary",
                "full_name": "First User",
            }
        )
        
        # Try duplicate
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "duplicate@example.com",
                "password": "Different123!",
                "user_type": "guardian",
                "full_name": "Second User",
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.text
    
    def test_signup_invalid_user_type(self):
        """Test signup with invalid user type"""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "Password123!",
                "user_type": "invalid_type",
                "full_name": "Test User",
            }
        )
        
        assert response.status_code == 400


class TestSignIn:
    """Sign in endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup_user(self):
        """Create test user before each test"""
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "testuser@example.com",
                "password": "TestPassword123!",
                "user_type": "guardian",
                "full_name": "Test Guardian",
            }
        )
    
    def test_signin_success(self):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/signin",
            json={
                "email": "testuser@example.com",
                "password": "TestPassword123!",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user_type"] == "guardian"
    
    def test_signin_invalid_email(self):
        """Test login with invalid email"""
        response = client.post(
            "/api/v1/auth/signin",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePassword123!",
            }
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.text
    
    def test_signin_invalid_password(self):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/signin",
            json={
                "email": "testuser@example.com",
                "password": "WrongPassword123!",
            }
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.text


class TestHealth:
    """Health check endpoint tests"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
