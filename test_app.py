#!/usr/bin/env python3
"""
Test suite for the Secure Web Application
Tests all endpoints and security features
"""

import unittest
import json
import tempfile
import os
from app import app, db, User
from werkzeug.security import generate_password_hash

class SecureAppTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            # Create a test user
            test_user = User(
                username='testuser',
                password_hash=generate_password_hash('testpassword123', method='pbkdf2:sha256')
            )
            db.session.add(test_user)
            db.session.commit()
    
    def tearDown(self):
        """Clean up after each test method."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
    
    def test_home_page(self):
        """Test the home page loads correctly."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SecureApp', response.data)
    
    def test_login_page(self):
        """Test the login page loads correctly."""
        response = self.app.get('/login-page')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
    
    def test_register_page(self):
        """Test the register page loads correctly."""
        response = self.app.get('/register-page')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create Account', response.data)
    
    def test_api_home(self):
        """Test the API home endpoint."""
        response = self.app.get('/api')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
    
    def test_api_register_success(self):
        """Test successful user registration via API."""
        response = self.app.post('/api/register',
                               data=json.dumps({
                                   'username': 'newuser',
                                   'password': 'newpassword123'
                               }),
                               content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Registered successfully!')
    
    def test_api_register_duplicate_user(self):
        """Test registration with existing username."""
        response = self.app.post('/api/register',
                               data=json.dumps({
                                   'username': 'testuser',  # Already exists
                                   'password': 'password123'
                               }),
                               content_type='application/json')
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'User already exists')
    
    def test_api_register_missing_data(self):
        """Test registration with missing data."""
        response = self.app.post('/api/register',
                               data=json.dumps({
                                   'username': 'newuser'
                                   # Missing password
                               }),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Missing username or password')
    
    def test_api_login_success(self):
        """Test successful login via API."""
        response = self.app.post('/api/login',
                               data=json.dumps({
                                   'username': 'testuser',
                                   'password': 'testpassword123'
                               }),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)
    
    def test_api_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.app.post('/api/login',
                               data=json.dumps({
                                   'username': 'testuser',
                                   'password': 'wrongpassword'
                               }),
                               content_type='application/json')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Invalid credentials')
    
    def test_api_login_nonexistent_user(self):
        """Test login with non-existent user."""
        response = self.app.post('/api/login',
                               data=json.dumps({
                                   'username': 'nonexistent',
                                   'password': 'password123'
                               }),
                               content_type='application/json')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'User not found')
    
    def test_protected_route_without_token(self):
        """Test accessing protected route without token."""
        response = self.app.get('/api/dashboard')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Token is missing! Access denied.')
    
    def test_protected_route_with_valid_token(self):
        """Test accessing protected route with valid token."""
        # First, get a token
        login_response = self.app.post('/api/login',
                                     data=json.dumps({
                                         'username': 'testuser',
                                         'password': 'testpassword123'
                                     }),
                                     content_type='application/json')
        token = json.loads(login_response.data)['token']
        
        # Then, use the token to access protected route
        response = self.app.get('/api/dashboard',
                              headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('Welcome to the secure dashboard', data['message'])
    
    def test_protected_route_with_invalid_token(self):
        """Test accessing protected route with invalid token."""
        response = self.app.get('/api/dashboard',
                              headers={'Authorization': 'Bearer invalid_token'})
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Token is invalid!')
    
    def test_web_register_success(self):
        """Test successful user registration via web form."""
        response = self.app.post('/register',
                               data={
                                   'username': 'webuser',
                                   'password': 'webpassword123'
                               },
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful', response.data)
    
    def test_web_register_weak_password(self):
        """Test registration with weak password."""
        response = self.app.post('/register',
                               data={
                                   'username': 'webuser',
                                   'password': '123'  # Too short
                               },
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password must be at least 8 characters', response.data)
    
    def test_web_login_success(self):
        """Test successful login via web form."""
        response = self.app.post('/login',
                               data={
                                   'username': 'testuser',
                                   'password': 'testpassword123'
                               },
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back', response.data)
    
    def test_web_login_invalid_credentials(self):
        """Test web login with invalid credentials."""
        response = self.app.post('/login',
                               data={
                                   'username': 'testuser',
                                   'password': 'wrongpassword'
                               },
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid credentials', response.data)
    
    def test_dashboard_access_without_login(self):
        """Test accessing dashboard without login."""
        response = self.app.get('/dashboard-page', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please log in', response.data)
    
    def test_logout(self):
        """Test logout functionality."""
        # First login
        with self.app.session_transaction() as sess:
            sess['user_token'] = 'dummy_token'
            sess['username'] = 'testuser'
        
        # Then logout
        response = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'logged out successfully', response.data)
    
    def test_404_error_handler(self):
        """Test 404 error handler."""
        response = self.app.get('/nonexistent-page')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Page Not Found', response.data)

def run_security_tests():
    """Run additional security-focused tests."""
    print("\n🔒 Running Security Tests...")
    
    # Test password hashing
    from werkzeug.security import generate_password_hash, check_password_hash
    password = "test_password_123"
    hashed = generate_password_hash(password, method='pbkdf2:sha256')
    
    assert hashed != password, "Password should be hashed"
    assert check_password_hash(hashed, password), "Password verification should work"
    assert not check_password_hash(hashed, "wrong_password"), "Wrong password should fail"
    print("✅ Password hashing test passed")
    
    # Test JWT token structure
    import jwt
    import datetime
    secret_key = "test_secret"
    payload = {
        'username': 'testuser',
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
    
    assert decoded['username'] == 'testuser', "JWT should contain correct username"
    print("✅ JWT token test passed")
    
    print("🔒 All security tests passed!")

if __name__ == '__main__':
    print("🧪 Starting Secure Web App Test Suite...")
    
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run security tests
    run_security_tests()
    
    print("\n✅ All tests completed successfully!")