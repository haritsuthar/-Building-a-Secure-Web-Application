# 🐍 Building a Secure Web Application (Python Flask)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-green?logo=flask&logoColor=white)
![Security](https://img.shields.io/badge/Security-JWT%20%7C%20OAuth%20%7C%20CSRF-red?logo=security&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?logo=opensource&logoColor=white)

**Objective**: Create a simple web application and implement security measures like authentication, authorization, and secure data storage.

**Tools**: Flask (Python), OAuth, JWT, SQL injection prevention, CSRF protection, and modern security practices.

A comprehensive **Python Flask-based** demonstration of cybersecurity principles in web development, showcasing industry-standard security implementations.

## 🚀 Features

### 🔐 Security Features
- **JWT Authentication**: Stateless, secure session management with JSON Web Tokens
- **Password Security**: PBKDF2-SHA256 hashing with automatic salting
- **CSRF Protection**: Cross-Site Request Forgery protection enabled
- **SQL Injection Prevention**: ORM-based queries with Flask-SQLAlchemy
- **Input Validation**: Client-side and server-side validation
- **Session Management**: Secure session handling with automatic expiration
- **Rate Limiting**: Built-in protection against brute force attacks
- **XSS Protection**: Input sanitization and output encoding

### 🎨 Frontend Features
- **Modern UI**: Responsive design with Bootstrap 5
- **Interactive Dashboard**: Real-time data loading and user management
- **Password Strength Indicator**: Visual feedback for password security
- **Security Status Display**: Real-time security feature monitoring
- **Error Handling**: Comprehensive error pages with user-friendly messages
- **Accessibility**: WCAG compliant interface elements

### 🔧 Technical Features
- **RESTful API**: Complete API endpoints for all functionality
- **Web Interface**: Full-featured web application with forms
- **Database Integration**: SQLite with SQLAlchemy ORM
- **Testing Suite**: Comprehensive unit and security tests
- **Error Handling**: Robust error handling and logging
- **Development Tools**: Hot reload and debugging support

## 📋 API Endpoints

### Public Endpoints
- `GET /` - Home page
- `GET /login-page` - Login form
- `GET /register-page` - Registration form
- `GET /api` - API status

### Authentication Endpoints
- `POST /api/register` - User registration (JSON)
- `POST /api/login` - User authentication (JSON)
- `POST /register` - User registration (Form)
- `POST /login` - User authentication (Form)
- `GET /logout` - User logout

### Protected Endpoints
- `GET /dashboard-page` - User dashboard (Web)
- `GET /api/dashboard` - Protected data (API)

## 🛠 Installation & Setup

### Prerequisites
- **Python 3.8 or higher** 🐍
- pip (Python package installer)
- Git (for cloning the repository)

### Quick Start (Python)

1. **Clone the repository**
   ```bash
   git clone https://github.com/haritsuthar/-Building-a-Secure-Web-Application.git
   cd -Building-a-Secure-Web-Application
   ```

2. **Create a Python virtual environment (recommended)**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

5. **Run the Python Flask application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Web Interface: http://localhost:5000
   - API Base: http://localhost:5000/api
   - Security Demo: http://localhost:5000/security-demo

### Alternative Installation Methods

#### Using pip (Python Package)
```bash
pip install -e .
secure-web-app
```

#### Using Docker
```bash
docker build -t secure-web-app .
docker run -p 5000:5000 secure-web-app
```

#### Using Docker Compose
```bash
docker-compose up -d
```

### 🧪 Running Tests

```bash
# Run the comprehensive test suite
python test_app.py

# The test suite includes:
# - Unit tests for all endpoints
# - Security feature validation
# - Authentication flow testing
# - Error handling verification
```

## 🔒 Security Implementation Details

### Authentication & Authorization
- **JWT Tokens**: 2-hour expiration with HS256 algorithm
- **Session Management**: Secure server-side session handling
- **Token Validation**: Automatic token verification on protected routes
- **Authorization Decorator**: Reusable `@token_required` decorator

### Password Security
- **Hashing Algorithm**: PBKDF2-SHA256 with automatic salting
- **Strength Validation**: Minimum 8 characters with complexity requirements
- **Storage**: Only hashed passwords stored, never plaintext
- **Verification**: Secure password comparison using Werkzeug

### CSRF Protection
- **Flask-WTF Integration**: Automatic CSRF token generation
- **Form Protection**: All forms include CSRF tokens
- **API Protection**: CSRF headers for API requests
- **Token Validation**: Server-side token verification

### SQL Injection Prevention
- **ORM Usage**: Flask-SQLAlchemy for all database operations
- **Parameterized Queries**: Automatic query parameterization
- **Input Sanitization**: User input validation and sanitization
- **No Raw SQL**: Elimination of raw SQL query construction

## 🎯 Usage Examples

### Web Interface Usage

1. **Registration**
   - Navigate to `/register-page`
   - Fill in username (3-50 characters)
   - Create strong password (8+ characters)
   - Password strength indicator provides real-time feedback

2. **Login**
   - Navigate to `/login-page`
   - Enter credentials
   - Automatic redirect to dashboard on success

3. **Dashboard**
   - View user profile and security status
   - Access protected data
   - Monitor session information
   - Test API endpoints

### API Usage

#### Register a new user
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "password": "securepassword123"}'
```

#### Login and get JWT token
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "password": "securepassword123"}'
```

#### Access protected data
```bash
curl -X GET http://localhost:5000/api/dashboard \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

## 📁 Project Structure

```
secure-web-app/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── test_app.py           # Comprehensive test suite
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Home page
│   ├── login.html        # Login form
│   ├── register.html     # Registration form
│   ├── dashboard.html    # User dashboard
│   └── error.html        # Error pages
├── static/               # Static assets
│   ├── css/
│   │   └── custom.css    # Custom styles
│   └── js/
│       └── security.js   # Security utilities
└── instance/             # Instance-specific files
    └── secure_app.db     # SQLite database
```

## 🔧 Configuration

### Environment Variables (Production)
```bash
# Set these in production
export SECRET_KEY="your-super-secret-production-key"
export DATABASE_URL="your-production-database-url"
export FLASK_ENV="production"
```

### Security Configuration
- **Secret Key**: Change the default secret key in production
- **Database**: Configure production database (PostgreSQL recommended)
- **HTTPS**: Enable HTTPS in production environment
- **CORS**: Configure CORS headers for API access

## 🚀 Deployment

### Production Checklist
- [ ] Change SECRET_KEY to a secure random value
- [ ] Use production database (PostgreSQL/MySQL)
- [ ] Enable HTTPS/SSL
- [ ] Configure proper CORS headers
- [ ] Set up proper logging
- [ ] Configure rate limiting
- [ ] Set up monitoring and alerts

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 🧪 Testing

The application includes a comprehensive test suite covering:

- **Unit Tests**: All endpoints and functions
- **Security Tests**: Password hashing, JWT tokens, CSRF protection
- **Integration Tests**: Complete user workflows
- **Error Handling**: All error scenarios
- **API Tests**: All REST endpoints

Run tests with: `python test_app.py`

## 🔍 Security Audit

### Implemented Protections
✅ **Authentication**: JWT-based with secure token handling  
✅ **Authorization**: Role-based access control  
✅ **Password Security**: PBKDF2-SHA256 hashing  
✅ **CSRF Protection**: Flask-WTF integration  
✅ **SQL Injection**: ORM-based queries  
✅ **XSS Protection**: Input sanitization  
✅ **Session Security**: Secure session management  
✅ **Input Validation**: Client and server-side  
✅ **Error Handling**: Secure error responses  
✅ **Rate Limiting**: Brute force protection  

### Security Headers (Production Recommended)
- Content Security Policy (CSP)
- X-Frame-Options
- X-Content-Type-Options
- Strict-Transport-Security (HSTS)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite
5. Submit a pull request

## 📄 License

This project is for educational purposes and demonstrates secure web development practices.

## 🆘 Support

For issues or questions:
1. Check the test suite for examples
2. Review the security implementation details
3. Examine the comprehensive error handling
4. Test with the provided API examples

---

**⚠️ Security Notice**: This application demonstrates security best practices but should be thoroughly audited before production use. Always keep dependencies updated and follow security guidelines for your specific deployment environment.