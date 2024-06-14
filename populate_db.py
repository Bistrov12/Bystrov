from werkzeug.security import generate_password_hash
from app import create_app, db, User, Product
from datetime import datetime
import random

app = create_app()

with app.app_context():
    # Удаляем и создаем заново все таблицы
    db.drop_all()
    db.create_all()

    # Создание пользователя-администратора
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin', method='pbkdf2:sha256', salt_length=16),
            role='admin'
        )
        db.session.add(admin)

    # Создание пользователей-продавцов
    sellers = []
    for i in range(2):  # Создаем двух продавцов для примера
        username = f'seller{i}'
        if not User.query.filter_by(username=username).first():
            seller = User(
                username=username,
                email=f'{username}@example.com',
                password_hash=generate_password_hash('password', method='pbkdf2:sha256', salt_length=16),
                role='seller'
            )
            sellers.append(seller)
            db.session.add(seller)

    db.session.commit()

    # Добавление товаров для каждого продавца
    categories = ['Футболки', 'Ремни']
    products = [
        {'name': 'Футболка 1', 'category': 'Футболки', 'price': 19.99, 'image_url': 'http://placehold.it/150x150'},
        {'name': 'Футболка 2', 'category': 'Футболки', 'price': 24.99, 'image_url': 'http://placehold.it/150x150'},
        {'name': 'Футболка 3', 'category': 'Футболки', 'price': 29.99, 'image_url': 'http://placehold.it/150x150'},
        {'name': 'Футболка 4', 'category': 'Футболки', 'price': 14.99, 'image_url': 'http://placehold.it/150x150'},
        {'name': 'Ремень 1', 'category': 'Ремни', 'price': 9.99, 'image_url': 'http://placehold.it/150x150'},
        {'name': 'Ремень 2', 'category': 'Ремни', 'price': 12.99, 'image_url': 'http://placehold.it/150x150'},
        {'name': 'Ремень 3', 'category': 'Ремни', 'price': 15.99, 'image_url': 'http://placehold.it/150x150'},
        {'name': 'Ремень 4', 'category': 'Ремни', 'price': 11.99, 'image_url': 'http://placehold.it/150x150'}
    ]

    for seller in sellers:
        for product_info in products:
            product = Product(
                name=product_info['name'],
                short_description='Краткое описание ' + product_info['name'],
                long_description='Длинное описание ' + product_info['name'],
                price=product_info['price'],
                image_url=product_info['image_url'],
                category=product_info['category'],
                seller_id=seller.id,
                approved=True  # Автоматически одобряем для простоты
            )
            db.session.add(product)

    db.session.commit()

    # Создание пользователей-покупателей
    for i in range(10):
        username = f'buyer{i}'
        if not User.query.filter_by(username=username).first():
            buyer = User(
                username=username,
                email=f'{username}@example.com',
                password_hash=generate_password_hash('password', method='pbkdf2:sha256', salt_length=16),
                role='buyer'
            )
            db.session.add(buyer)

    db.session.commit()
    print("Database populated with sample data")
