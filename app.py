from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
    app.config['SESSION_TYPE'] = 'filesystem'

    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    login_manager.login_message = "Пожалуйста, войдите, чтобы получить доступ к этой странице."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    return app

app = create_app()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_description = db.Column(db.String(200), nullable=False)
    long_description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    category = db.Column(db.String(50), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller = db.relationship('User', backref=db.backref('products', lazy=True))

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
    product = Product.query.get(product_id)
    if product:
        if 'cart' not in session:
            session['cart'] = []
        session['cart'].append(product.id)
        session.modified = True
        flash('Товар добавлен в корзину.', 'success')
    else:
        flash('Товар не найден.', 'danger')
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
        # Сохраните заказ в базе данных и очистите корзину
        flash('Ваш заказ был успешно оформлен.', 'success')
        session.pop('cart', None)
        return redirect(url_for('index'))
    return render_template('checkout.html')

if __name__ == '__main__':
    app.run(debug=True)
