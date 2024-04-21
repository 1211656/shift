from src.domain.auth import Email, Password
from main import db


class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(Email, unique=True, nullable=False)
    password = db.Column(Password,unique=True, nullable=False)

