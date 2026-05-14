from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    # We store the hash, NEVER the plain text password
    password_hash = db.Column(db.String(256), nullable=True)  # Nullable for OAuth users
    
    # OAuth fields
    oauth_provider = db.Column(db.String(50), nullable=True)  # 'github', 'google', etc.
    oauth_id = db.Column(db.String(100), nullable=True)  # Provider's user ID
    avatar_url = db.Column(db.String(200), nullable=True)
    
    # Security fields
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime, nullable=True)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<User {self.username}>"
    
    def is_locked(self):
        """Check if account is locked due to failed login attempts"""
        if self.locked_until:
            from datetime import datetime, timezone
            return datetime.now(timezone.utc) < self.locked_until
        return False
    
    def lock_account(self, minutes=30):
        """Lock account for specified minutes"""
        from datetime import datetime, timezone, timedelta
        self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        db.session.commit()
    
    def unlock_account(self):
        """Unlock account and reset failed attempts"""
        self.locked_until = None
        self.failed_login_attempts = 0
        db.session.commit()