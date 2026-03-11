from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    username = db.Column(db.String(50), unique=True)
    email =db.Column(db.String(256), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))   # admin / manager / customer