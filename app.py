import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from models import db, User, Product, Order
from forms import ProductForm
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

    db.init_app(app)
    migrate = Migrate(app, db)
    mail = Mail(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    login_manager.login_message = "Пожалуйста, войдите, чтобы получить доступ к этой странице."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.cli.command('init-db')
    def init_db():
        with app.app_context():
            db.create_all()
            try:
                from populate_db import populate
                populate()
                print("База данных успешно заполнена!")
            except ImportError as e:
                print(f"Ошибка импорта populate_db: {e}")

    @app.before_request
    def update_last_activity():
        if current_user.is_authenticated:
            current_user.last_activity = datetime.utcnow()
            db.session.commit()

    @app.route('/admin_dashboard')
    @login_required
    def admin_dashboard():
        if current_user.role != 'admin':
            flash('У вас нет доступа к этой странице.', 'danger')
            return redirect(url_for('index'))
        users = User.query.all()
        products = Product.query.all()
        return render_template('admin_dashboard.html', users=users, products=products)

    @app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
    @login_required
    def edit_user(user_id):
        if current_user.role != 'admin':
            flash('У вас нет доступа к этой странице.', 'danger')
            return redirect(url_for('index'))
        user = User.query.get_or_404(user_id)
        if request.method == 'POST':
            user.username = request.form['username']
            user.email = request.form['email']
            user.role = request.form['role']
            db.session.commit()
            flash('Данные пользователя обновлены', 'success')
            return redirect(url_for('admin_dashboard'))
        return render_template('edit_user.html', user=user)

    @app.route('/delete_user/<int:user_id>')
    @login_required
    def delete_user(user_id):
        if current_user.role != 'admin':
            flash('У вас нет доступа к этой странице.', 'danger')
            return redirect(url_for('index'))
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash('Пользователь удален', 'danger')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin_delete_product/<int:product_id>')
    @login_required
    def admin_delete_product(product_id):
        if current_user.role != 'admin':
            flash('У вас нет доступа к этой странице.', 'danger')
            return redirect(url_for('index'))
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        flash('Товар удален', 'danger')
        return redirect(url_for('admin_dashboard'))

    @app.route('/')
    def index():
        if current_user.is_authenticated and current_user.role == 'seller':
            tshirts = Product.query.filter_by(category='Футболки', seller_id=current_user.id).all()
            belts = Product.query.filter_by(category='Ремни', seller_id=current_user.id).all()
            watches = Product.query.filter_by(category='Часы', seller_id=current_user.id).all()
            bags = Product.query.filter_by(category='Сумки', seller_id=current_user.id).all()
            return render_template('index.html', tshirts=tshirts, belts=belts, watches=watches, bags=bags, is_seller=True)
        else:
            tshirts = Product.query.filter_by(category='Футболки').all()
            belts = Product.query.filter_by(category='Ремни').all()
            watches = Product.query.filter_by(category='Часы').all()
            bags = Product.query.filter_by(category='Сумки').all()
            return render_template('index.html', tshirts=tshirts, belts=belts, watches=watches, bags=bags, is_seller=False)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            role = request.form['role']
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            try:
                db.session.add(user)
                db.session.commit()
                flash('Регистрация прошла успешно. Теперь вы можете войти.', 'success')
                return redirect(url_for('login'))
            except IntegrityError:
                db.session.rollback()
                flash('Аккаунт с таким email уже существует.', 'danger')
                return redirect(url_for('register'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user)
                flash('Вы успешно вошли в систему.', 'success')
                return redirect(url_for('index'))
            else:
                flash('Неверный логин или пароль.', 'danger')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Вы успешно вышли из системы.', 'success')
        return redirect(url_for('index'))

    @app.route('/edit_profile', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        if request.method == 'POST':
            current_user.username = request.form['username']
            current_user.email = request.form['email']
            if request.form['password']:
                current_user.set_password(request.form['password'])
            db.session.commit()
            flash('Ваш профиль был обновлен', 'success')
            return redirect(url_for('edit_profile'))
        return render_template('edit_profile.html')

    @app.route('/search', methods=['GET'])
    def search():
        query = request.args.get('q')
        products = Product.query.filter(Product.name.contains(query) | Product.short_description.contains(query)).all()
        return render_template('search_results.html', products=products)

    @app.route('/product/<int:product_id>')
    def product_detail(product_id):
        product = Product.query.get_or_404(product_id)
        return render_template('product_detail.html', product=product)

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route('/add_to_cart/<int:product_id>', methods=['POST'])
    @login_required
    def add_to_cart(product_id):
        product = Product.query.get_or_404(product_id)
        cart = session.get('cart', [])
        cart.append(product_id)
        session['cart'] = cart
        flash('Товар добавлен в корзину.', 'success')
        return redirect(url_for('cart'))

    @app.route('/remove_from_cart/<int:product_id>')
    @login_required
    def remove_from_cart(product_id):
        cart = session.get('cart', [])
        if product_id in cart:
            cart.remove(product_id)
            session['cart'] = cart
            flash('Товар удален из корзины.', 'success')
        else:
            flash('Товар не найден в корзине.', 'danger')
        return redirect(url_for('cart'))

    @app.route('/cart')
    @login_required
    def cart():
        cart = session.get('cart', [])
        products = Product.query.filter(Product.id.in_(cart)).all() if cart else []
        return render_template('cart.html', products=products)

    @app.route('/checkout', methods=['GET', 'POST'])
    @login_required
    def checkout():
        cart = session.get('cart', [])
        products = Product.query.filter(Product.id.in_(cart)).all() if cart else []

        if request.method == 'POST':
            size = request.form['size']
            address = request.form['address']
            phone = request.form['phone']
            email = request.form['email']  # Email покупателя

            for product in products:
                new_order = Order(
                    product_id=product.id,
                    user_id=current_user.id,
                    address=address,
                    phone=phone,
                    size=size,
                    email=email
                )
                db.session.add(new_order)
                db.session.commit()

            # Отправка подтверждающего письма
            msg = Message('Подтверждение заказа', sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f'Ваш заказ на {len(products)} товаров успешно оформлен.\n\nАдрес доставки: {address}\nНомер телефона: {phone}\nРазмер: {size}\n\nСпасибо за ваш заказ!'
            mail.send(msg)

            flash('Ваш заказ успешно оформлен. Подтверждение отправлено на ваш email.', 'success')
            session.pop('cart', None)
            return redirect(url_for('my_orders'))

        return render_template('checkout.html', products=products)

    @app.route('/my_orders')
    @login_required
    def my_orders():
        if current_user.role != 'buyer':
            flash('У вас нет доступа к этой странице.', 'danger')
            return redirect(url_for('index'))
        orders = Order.query.filter_by(user_id=current_user.id).all()
        return render_template('my_orders.html', orders=orders)

    @app.route('/cancel_order/<int:order_id>', methods=['POST'])
    @login_required
    def cancel_order(order_id):
        order = Order.query.get_or_404(order_id)
        if order.user_id != current_user.id:
            flash('У вас нет прав на отмену этого заказа.', 'danger')
            return redirect(url_for('my_orders'))
        db.session.delete(order)
        db.session.commit()
        flash('Заказ успешно отменён.', 'success')
        return redirect(url_for('my_orders'))

    @app.route('/seller_dashboard')
    @login_required
    def seller_dashboard():
        if current_user.role != 'seller':
            flash('У вас нет доступа к этой странице.', 'danger')
            return redirect(url_for('index'))
        products = Product.query.filter_by(seller_id=current_user.id).all()
        return render_template('seller_dashboard.html', products=products)

    @app.route('/my_products')
    @login_required
    def my_products():
        if current_user.role != 'seller':
            flash('У вас нет доступа к этой странице.', 'danger')
            return redirect(url_for('index'))
        products = Product.query.filter_by(seller_id=current_user.id).all()
        return render_template('my_products.html', products=products)

    def ensure_upload_folder_exists(filepath):
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)

    @app.route('/add_product/<category>', methods=['GET', 'POST'])
    @login_required
    def add_product(category):
        if current_user.role != 'seller':
            flash('У вас нет доступа к этой странице.', 'danger')
            return redirect(url_for('index'))
        form = ProductForm()
        if form.validate_on_submit():
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(filepath)
            product = Product(
                name=form.name.data,
                short_description=form.short_description.data,
                long_description=form.long_description.data,
                price=form.price.data,
                category=category,
                image_url=filename,  # Сохраняем только имя файла
                seller_id=current_user.id
            )
            db.session.add(product)
            db.session.commit()
            flash('Товар успешно добавлен.', 'success')
            return redirect(url_for('index'))
        return render_template('add_product.html', form=form, category=category)

    @app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
    @login_required
    def edit_product(product_id):
        product = Product.query.get_or_404(product_id)
        if product.seller_id != current_user.id:
            flash('У вас нет прав на редактирование этого товара.', 'danger')
            return redirect(url_for('my_products'))

        form = ProductForm(obj=product)
        if form.validate_on_submit():
            form.populate_obj(product)
            if form.image.data:
                filename = secure_filename(form.image.data.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                form.image.data.save(filepath)
                product.image_url = filename  # Сохраняем только имя файла
            db.session.commit()
            flash('Товар успешно обновлен.', 'success')
            return redirect(url_for('my_products'))
        return render_template('edit_product.html', form=form, product=product)

    @app.route('/delete_product/<int:product_id>', methods=['POST'])
    @login_required
    def delete_product(product_id):
        product = Product.query.get_or_404(product_id)
        if product.seller_id != current_user.id:
            flash('У вас нет прав на удаление этого товара.', 'danger')
            return redirect(url_for('my_products'))

        db.session.delete(product)
        db.session.commit()
        flash('Товар успешно удален.', 'success')
        return redirect(url_for('my_products'))

    @app.route('/buyer_dashboard')
    @login_required
    def buyer_dashboard():
        if current_user.role != 'buyer':
            flash('У вас нет доступа к этой странице.', 'danger')
            return redirect(url_for('index'))
        return render_template('buyer_dashboard.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
