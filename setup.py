"""
Setup configuration for Building a Secure Web Application
A comprehensive Flask-based demonstration of cybersecurity principles
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="building-secure-web-application",
    version="1.0.0",
    author="Harit Suthar",
    author_email="your.email@example.com",
    description="A comprehensive Flask-based secure web application demonstrating cybersecurity principles",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/haritsuthar/-Building-a-Secure-Web-Application",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Flask",
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "oauth": [
            "Authlib>=1.3.0",
            "requests>=2.31.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "secure-web-app=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/*.html", "static/css/*.css", "static/js/*.js"],
    },
    keywords=[
        "flask",
        "security",
        "web-application",
        "authentication",
        "authorization",
        "jwt",
        "oauth",
        "csrf",
        "cybersecurity",
        "education",
        "demonstration",
    ],
    project_urls={
        "Bug Reports": "https://github.com/haritsuthar/-Building-a-Secure-Web-Application/issues",
        "Source": "https://github.com/haritsuthar/-Building-a-Secure-Web-Application",
        "Documentation": "https://github.com/haritsuthar/-Building-a-Secure-Web-Application#readme",
    },
)