from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    # We store the hash, NEVER the plain text password
    password_hash = db.Column(db.String(256), nullable=False) 

    def __repr__(self):
        return f"<User {self.username}>"