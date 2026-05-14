"""
Building a Secure Web Application

A comprehensive Flask-based demonstration of cybersecurity principles including:
- Authentication & Authorization (JWT + OAuth)
- Secure Data Storage (Password Hashing)
- Attack Prevention (CSRF, XSS, SQL Injection)
- Input Validation & Security Monitoring

Author: Harit Suthar
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Harit Suthar"
__email__ = "your.email@example.com"
__description__ = "A comprehensive Flask-based secure web application demonstrating cybersecurity principles"

# Import main application components
from app import app, db
from models import User

__all__ = ["app", "db", "User"]