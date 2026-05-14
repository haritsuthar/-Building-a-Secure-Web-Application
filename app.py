from flask import Flask, request, jsonify, make_response, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from datetime import timezone
from functools import wraps
from models import db, User
import os
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
import secrets

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CSRF protection and secure sessions
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# OAuth Configuration
oauth = OAuth(app)

# SECURITY MEASURE: Environment-based configuration
# In production, these should be set as environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///secure_app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# OAuth Configuration (GitHub example - can be extended to Google, etc.)
app.config['GITHUB_CLIENT_ID'] = os.getenv('GITHUB_CLIENT_ID')
app.config['GITHUB_CLIENT_SECRET'] = os.getenv('GITHUB_CLIENT_SECRET')

# Configure OAuth providers
if app.config['GITHUB_CLIENT_ID'] and app.config['GITHUB_CLIENT_SECRET']:
    github = oauth.register(
        name='github',
        client_id=app.config['GITHUB_CLIENT_ID'],
        client_secret=app.config['GITHUB_CLIENT_SECRET'],
        server_metadata_url='https://api.github.com/.well-known/openid_configuration',
        client_kwargs={
            'scope': 'user:email'
        }
    )
else:
    github = None

db.init_app(app)

# Create the database tables before the first request
with app.app_context():
    db.create_all()

# --- ENDPOINT: Home / Root ---
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# --- ENDPOINT: Login Page ---
@app.route('/login-page', methods=['GET'])
def login_page():
    return render_template('login.html')

# --- ENDPOINT: Register Page ---
@app.route('/register-page', methods=['GET'])
def register_page():
    return render_template('register.html')

# --- ENDPOINT: Dashboard Page ---
@app.route('/dashboard-page', methods=['GET'])
def dashboard_page():
    if 'user_token' not in session:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')

# --- ENDPOINT: Security Demonstration Page ---
@app.route('/security-demo', methods=['GET'])
def security_demo():
    return render_template('security_demo.html')

# --- API ENDPOINT: Home / Root ---
@app.route('/api', methods=['GET'])
def api_home():
    return jsonify({
        "status": "success",
        "message": "Secure Web App API is running! Use Thunder Client to test /register and /login."
    })

# --- SECURITY MEASURE: JWT Authorization Decorator ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check if token is passed in the headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing! Access denied.'}), 401

        try:
            # Decode the JWT to verify the user
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(username=data['username']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

# --- API ENDPOINT: Register a new user ---
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing username or password'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'User already exists'}), 409

    # SECURITY MEASURE: Secure Data Storage (Password Hashing)
    # PBKDF2:sha256 is a strong hashing algorithm with a salt
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    new_user = User(username=data['username'], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registered successfully!'}), 201

# --- WEB ENDPOINT: Register a new user ---
@app.route('/register', methods=['POST'])
def register():
    data = request.form
    
    if not data.get('username') or not data.get('password'):
        flash('Missing username or password', 'error')
        return redirect(url_for('register_page'))

    if User.query.filter_by(username=data['username']).first():
        flash('User already exists', 'error')
        return redirect(url_for('register_page'))

    # Password strength validation
    password = data['password']
    if len(password) < 8:
        flash('Password must be at least 8 characters long', 'error')
        return redirect(url_for('register_page'))

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    
    new_user = User(username=data['username'], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    flash('Registration successful! Please log in.', 'success')
    return redirect(url_for('login_page'))

# --- API ENDPOINT: Login and generate JWT ---
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(username=data['username']).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    # SECURITY MEASURE: Authentication Verification
    if check_password_hash(user.password_hash, data['password']):
        # Generate JWT token valid for 30 minutes
        token = jwt.encode({
            'username': user.username,
            'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({'token': token})

    return jsonify({'message': 'Invalid credentials'}), 401

# --- WEB ENDPOINT: Login and create session ---
@app.route('/login', methods=['POST'])
def login():
    data = request.form

    if not data.get('username') or not data.get('password'):
        flash('Missing username or password', 'error')
        return redirect(url_for('login_page'))

    user = User.query.filter_by(username=data['username']).first()

    if not user:
        flash('User not found', 'error')
        return redirect(url_for('login_page'))

    if check_password_hash(user.password_hash, data['password']):
        # Generate JWT token for session
        token = jwt.encode({
            'username': user.username,
            'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=2)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        session['user_token'] = token
        session['username'] = user.username
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(url_for('dashboard_page'))

    flash('Invalid credentials', 'error')
    return redirect(url_for('login_page'))

# --- WEB ENDPOINT: Logout ---
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

# --- OAUTH ENDPOINTS ---
@app.route('/auth/<provider>')
def oauth_login(provider):
    """Initiate OAuth login with specified provider"""
    if provider == 'github' and github:
        redirect_uri = url_for('oauth_callback', provider=provider, _external=True)
        return github.authorize_redirect(redirect_uri)
    else:
        flash(f'{provider.title()} OAuth is not configured.', 'error')
        return redirect(url_for('login_page'))

@app.route('/auth/<provider>/callback')
def oauth_callback(provider):
    """Handle OAuth callback"""
    if provider == 'github' and github:
        try:
            token = github.authorize_access_token()
            user_info = github.parse_id_token(token)
            
            # Get additional user info from GitHub API
            resp = github.get('user', token=token)
            github_user = resp.json()
            
            # Check if user exists
            user = User.query.filter_by(oauth_provider=provider, oauth_id=str(github_user['id'])).first()
            
            if not user:
                # Create new user
                user = User(
                    username=github_user['login'],
                    email=github_user.get('email'),
                    oauth_provider=provider,
                    oauth_id=str(github_user['id']),
                    avatar_url=github_user.get('avatar_url')
                )
                db.session.add(user)
                db.session.commit()
                flash(f'Account created successfully with {provider.title()}!', 'success')
            else:
                # Update existing user info
                user.avatar_url = github_user.get('avatar_url')
                user.email = github_user.get('email')
                user.last_login = datetime.datetime.now(timezone.utc)
                db.session.commit()
                flash(f'Welcome back, {user.username}!', 'success')
            
            # Create session
            jwt_token = jwt.encode({
                'username': user.username,
                'user_id': user.id,
                'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=2)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            
            session['user_token'] = jwt_token
            session['username'] = user.username
            session['oauth_provider'] = provider
            
            return redirect(url_for('dashboard_page'))
            
        except Exception as e:
            flash(f'OAuth authentication failed: {str(e)}', 'error')
            return redirect(url_for('login_page'))
    else:
        flash(f'{provider.title()} OAuth is not configured.', 'error')
        return redirect(url_for('login_page'))

# --- API ENDPOINT: Protected Route (Requires Authorization) ---
@app.route('/api/dashboard', methods=['GET'])
@token_required
def api_dashboard(current_user):
    return jsonify({
        'message': f'Welcome to the secure dashboard, {current_user.username}!',
        'sensitive_data': 'This data is only visible to authorized users with a valid JWT.'
    })

# --- ERROR HANDLERS ---
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_code=404,
                         error_title="Page Not Found",
                         error_message="The page you're looking for doesn't exist."), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html',
                         error_code=500,
                         error_title="Internal Server Error",
                         error_message="Something went wrong on our end. Please try again later."), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('error.html',
                         error_code=403,
                         error_title="Access Forbidden",
                         error_message="You don't have permission to access this resource."), 403

@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('error.html',
                         error_code=401,
                         error_title="Unauthorized",
                         error_message="Please log in to access this resource."), 401

if __name__ == '__main__':
    app.run(debug=True)