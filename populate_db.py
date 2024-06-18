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

        # Проверка существующих товаров
        if Product.query.count() == 0:
            products = [
                Product(
                    name='Футболка 1',
                    short_description='Описание футболки 1',
                    long_description='',
                    price=1000.0,
                    category='Футболки',
                    image_url='tshirts/tshirt1.png',
                    seller_id=admin.id
                ),
                Product(
                    name='Футболка 2',
                    short_description='Описание футболки 2',
                    long_description='',
                    price=1200.0,
                    category='Футболки',
                    image_url='tshirts/tshirt2.png',
                    seller_id=admin.id
                ),
                Product(
                    name='Футболка 3',
                    short_description='Описание футболки 3',
                    long_description='',
                    price=1100.0,
                    category='Футболки',
                    image_url='tshirts/tshirt3.png',
                    seller_id=admin.id
                ),
                Product(
                    name='Футболка 4',
                    short_description='Описание футболки 4',
                    long_description='',
                    price=1300.0,
                    category='Футболки',
                    image_url='tshirts/tshirt4.png',
                    seller_id=admin.id
                ),
                Product(
                    name='Ремень 1',
                    short_description='Описание ремня 1',
                    long_description='',
                    price=800.0,
                    category='Ремни',
                    image_url='belts/belt1.png',
                    seller_id=admin.id
                ),
                Product(
                    name='Ремень 2',
                    short_description='Описание ремня 2',
                    long_description='',
                    price=900.0,
                    category='Ремни',
                    image_url='belts/belt2.png',
                    seller_id=admin.id
                ),
                Product(
                    name='Ремень 3',
                    short_description='Описание ремня 3',
                    long_description='',
                    price=850.0,
                    category='Ремни',
                    image_url='belts/belt3.png',
                    seller_id=admin.id
                ),
                Product(
                    name='Ремень 4',
                    short_description='Описание ремня 4',
                    long_description='',
                    price=950.0,
                    category='Ремни',
                    image_url='belts/belt4.png',
                    seller_id=admin.id
                ),
                Product(
                    name='Часы 1',
                    short_description='Описание часов 1',
                    long_description='',
                    price=5000.0,
                    category='Часы',
                    image_url='watches/watches1.png',
                    seller_id=admin.id
                ),
                Product(
                    name='Часы 2',
                    short_description='Описание часов 2',
                    long_description='',
                    price=6000.0,
                    category='Часы',
                    image_url='watches/watches2.png',
                    seller_id=admin.id
                ),
                Product(
                    name='Часы 3',
                    short_description='Описание часов 3',
                    long_description='',
                    price=7000.0,
                    category='Часы',
                    image_url='watches/watches3.png',
                    seller_id=admin.id
                ),
                Product(
                    name='Часы 4',
                    short_description='Описание часов 4',
                    long_description='',
                    price=4000.0,
                    category='Часы',
                    image_url='watches/watches4.png',
                    seller_id=admin.id
                ),
                Product(
                    name='Сумка 1',
                    short_description='Описание сумки 1',
                    long_description='',
                    price=1000.0,
                    category='Сумки',
                    image_url='bags/bags1.png',
                    seller_id=admin.id
                ),
                Product(
                    name='Сумка 2',
                    short_description='Описание сумки 2',
                    long_description='',
                    price=1200.0,
                    category='Сумки',
                    image_url='bags/bags2.png',
                    seller_id=admin.id
                ),
                Product(
                    name='Сумка 3',
                    short_description='Описание сумки 3',
                    long_description='',
                    price=1100.0,
                    category='Сумки',
                    image_url='bags/bags3.png',
                    seller_id=admin.id
                ),
                Product(
                    name='Сумка 4',
                    short_description='Описание сумки 4',
                    long_description='',
                    price=1300.0,
                    category='Сумки',
                    image_url='bags/bags4.png',
                    seller_id=admin.id
                )
            ]

            for product in products:
                db.session.add(product)

            db.session.commit()
            print("База данных успешно заполнена!")

if __name__ == "__main__":
    populate()
