# Secure Web Application API

A Python Flask-based secure web application demonstrating core cybersecurity principles including Authentication, Authorization, Secure Data Storage, and SQL Injection prevention.

## Security Features Implemented

1. **Authentication & Authorization (JWT):** 
   - Uses JSON Web Tokens (JWT) for stateless, secure session management.
   - Protected routes utilize a custom `@token_required` decorator to verify token validity and expiration before granting access.
   *(Note: For enterprise OAuth integration like Google/GitHub login, external provider client IDs and secrets would be configured here using a library like `Authlib`)*.

2. **Secure Data Storage (Cryptography):**
   - Plaintext passwords are never stored. 
   - Utilizes `Werkzeug.security` to apply `pbkdf2:sha256` hashing with automatic salting before saving to the database.

3. **SQL Injection Prevention:**
   - Abandons raw SQL queries in favor of `Flask-SQLAlchemy` (an ORM). 
   - The ORM automatically parameterizes backend queries, effectively neutralizing SQL injection attack vectors.

## How to Run the Project

1. Open a terminal in this directory.
2. Create a virtual environment (optional but recommended): `python -m venv venv`
3. Activate the environment: 
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `python app.py`

## API Endpoints

- `POST /register` - Expects JSON `{"username": "your_name", "password": "your_password"}`
- `POST /login` - Expects JSON `{"username": "your_name", "password": "your_password"}`. Returns a JWT token.
- `GET /dashboard` - Requires Header `Authorization: Bearer <your_jwt_token>`. Returns protected data.