from app import create_app, db
from models import User, Product

def populate():
    app = create_app()
    with app.app_context():
        db.create_all()

        # Проверка существующего пользователя
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()

        # Создание нескольких товаров с изображениями
        products = [
            Product(
                name='Новая футболка 1',
                short_description='Короткое описание новой футболки 1',
                long_description='Длинное описание новой футболки 1',
                price=1000.0,
                category='Футболки',
                image_url='tshirts/tshirt1.png',
                seller_id=admin.id,
                approved=True
            ),
            Product(
                name='Новая футболка 2',
                short_description='Короткое описание новой футболки 2',
                long_description='Длинное описание новой футболки 2',
                price=1200.0,
                category='Футболки',
                image_url='tshirts/tshirt2.png',
                seller_id=admin.id,
                approved=True
            ),
            Product(
                name='Новая футболка 3',
                short_description='Короткое описание новой футболки 3',
                long_description='Длинное описание новой футболки 3',
                price=1100.0,
                category='Футболки',
                image_url='tshirts/tshirt3.png',
                seller_id=admin.id,
                approved=True
            ),
            Product(
                name='Новая футболка 4',
                short_description='Короткое описание новой футболки 4',
                long_description='Длинное описание новой футболки 4',
                price=1300.0,
                category='Футболки',
                image_url='tshirts/tshirt4.png',
                seller_id=admin.id,
                approved=True
            ),
            Product(
                name='Новый ремень 1',
                short_description='Короткое описание нового ремня 1',
                long_description='Длинное описание нового ремня 1',
                price=800.0,
                category='Ремни',
                image_url='belts/belt1.png',
                seller_id=admin.id,
                approved=True
            ),
            Product(
                name='Новый ремень 2',
                short_description='Короткое описание нового ремня 2',
                long_description='Длинное описание нового ремня 2',
                price=900.0,
                category='Ремни',
                image_url='belts/belt2.png',
                seller_id=admin.id,
                approved=True
            ),
            Product(
                name='Новый ремень 3',
                short_description='Короткое описание нового ремня 3',
                long_description='Длинное описание нового ремня 3',
                price=850.0,
                category='Ремни',
                image_url='belts/belt3.png',
                seller_id=admin.id,
                approved=True
            ),
            Product(
                name='Новый ремень 4',
                short_description='Короткое описание нового ремня 4',
                long_description='Длинное описание нового ремня 4',
                price=950.0,
                category='Ремни',
                image_url='belts/belt4.png',
                seller_id=admin.id,
                approved=True
            )
        ]

        for product in products:
            db.session.add(product)

        db.session.commit()
        print("База данных успешно заполнена!")

if __name__ == "__main__":
    populate()
