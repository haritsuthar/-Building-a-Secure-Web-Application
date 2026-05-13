from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from models import db, User

app = Flask(__name__)

# SECURITY MEASURE: In a real production environment, this secret key 
# should be stored in environment variables (e.g., .env file), not hardcoded.
app.config['SECRET_KEY'] = 'your_super_secret_internship_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///secure_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create the database tables before the first request
with app.app_context():
    db.create_all()

# --- ENDPOINT: Home / Root ---
@app.route('/', methods=['GET'])
def home():
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

# --- ENDPOINT: Register a new user ---
@app.route('/register', methods=['POST'])
def register():
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

# --- ENDPOINT: Login and generate JWT ---
@app.route('/login', methods=['POST'])
def login():
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
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({'token': token})

    return jsonify({'message': 'Invalid credentials'}), 401

# --- ENDPOINT: Protected Route (Requires Authorization) ---
@app.route('/dashboard', methods=['GET'])
@token_required
def dashboard(current_user):
    return jsonify({
        'message': f'Welcome to the secure dashboard, {current_user.username}!',
        'sensitive_data': 'This data is only visible to authorized users with a valid JWT.'
    })

if __name__ == '__main__':
    app.run(debug=True)