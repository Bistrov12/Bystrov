from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Product, Order
from sqlalchemy.exc import IntegrityError

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db)

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
                from populate_db import populate  # Убедитесь, что имя файла совпадает
                populate()
                print("База данных успешно заполнена!")
            except ImportError as e:
                print(f"Ошибка импорта populate_db: {e}")

    @app.route('/my_orders')
    @login_required
    def my_orders():
        orders = Order.query.filter_by(user_id=current_user.id).all()
        return render_template('my_orders.html', orders=orders)

    @app.route('/')
    def index():
        tshirts = Product.query.filter_by(category='Футболки', approved=True).all()
        belts = Product.query.filter_by(category='Ремни', approved=True).all()
        return render_template('index.html', tshirts=tshirts, belts=belts)

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
        return render_template('index.html', products=products)

    @app.route('/add_to_cart/<int:product_id>')
    @login_required
    def add_to_cart(product_id):
        product = Product.query.get_or_404(product_id)
        cart = session.get('cart', [])
        cart.append(product_id)
        session['cart'] = cart
        flash('Товар добавлен в корзину.', 'success')
        return redirect(url_for('index'))

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
        if request.method == 'POST':
            size = request.form.get('size')
            address = request.form.get('address')
            phone = request.form.get('phone')
            cart = session.get('cart', [])

            for product_id in cart:
                product = Product.query.get(product_id)
                order = Order(user_id=current_user.id, product_id=product.id, address=address, phone=phone, size=size)
                db.session.add(order)

            db.session.commit()
            flash('Ваш заказ был успешно оформлен.', 'success')
            session.pop('cart', None)
            return redirect(url_for('index'))

        cart = session.get('cart', [])
        products = Product.query.filter(Product.id.in_(cart)).all() if cart else []
        return render_template('checkout.html', products=products)

    @app.route('/seller_dashboard')
    @login_required
    def seller_dashboard():
        if current_user.role != 'seller':
            flash('У вас нет доступа к этой странице.', 'danger')
            return redirect(url_for('index'))
        products = Product.query.filter_by(seller_id=current_user.id).all()
        return render_template('seller_dashboard.html', products=products)

    @app.route('/add_product', methods=['GET', 'POST'])
    @login_required
    def add_product():
        if current_user.role != 'seller':
            flash('У вас нет доступа к этой странице.', 'danger')
            return redirect(url_for('index'))
        if request.method == 'POST':
            name = request.form['name']
            short_description = request.form['short_description']
            long_description = request.form['long_description']
            price = request.form['price']
            category = request.form['category']
            image_url = request.form['image_url']
            product = Product(
                name=name,
                short_description=short_description,
                long_description=long_description,
                price=price,
                category=category,
                image_url=image_url,
                seller_id=current_user.id
            )
            db.session.add(product)
            db.session.commit()
            flash('Товар успешно добавлен.', 'success')
            return redirect(url_for('seller_dashboard'))
        return render_template('add_product.html')

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
