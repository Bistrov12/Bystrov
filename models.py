from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(64), default='buyer')
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    short_description = db.Column(db.String(128))
    long_description = db.Column(db.Text)
    price = db.Column(db.Float)
    category = db.Column(db.String(64))
    image_url = db.Column(db.String(128))
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    seller = db.relationship('User', backref='products')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    size = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product')
    user = db.relationship('User')
    email = db.Column(db.String(120), nullable=False)  # Добавлено поле email

    def __init__(self, product_id, user_id, address, phone, size, email):
        self.product_id = product_id
        self.user_id = user_id
        self.address = address
        self.phone = phone
        self.size = size
        self.email = email
        self.created_at = datetime.utcnow()
