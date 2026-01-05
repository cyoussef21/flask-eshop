import os
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from forms import LoginForm, RegisterForm, ProductForm
# FLASK Imports
from flask import Flask, render_template, url_for, redirect, flash, abort
from flask import request as flask_request
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# SQLAlchemy Imports
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, Float, ForeignKey, func
from functools import wraps

HASH_KEY = os.getenv('HASH_KEY')
HASH_PREFIX = os.getenv('HASH_PREFIX')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
bootstrap = Bootstrap5(app)

# LOGIN CONFIG
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@localhost/{db_name}"
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    permissions: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    def __init__(self, email, permissions, name, password):
        self.email = email
        self.permissions = permissions
        self.password = password
        self.name = name

    def get_id(self):
        return str(self.user_id)


class Products(db.Model):
    __tablename__ = "products"
    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    discount: Mapped[float] = mapped_column(Float, nullable=True)
    thumbnail: Mapped[str] = mapped_column(String(200), nullable=False)
    image: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)


class Cart(db.Model):
    __tablename__ = 'carts'
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), primary_key=True)
    discounted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.permissions != 'admin':
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            flash("There is already an account registered under this email, please log in instead.")
            return redirect(url_for('login'))
        else:
            hs_password = generate_password_hash(form.password.data, HASH_KEY, salt_length=2)
            password = hs_password.removeprefix(HASH_PREFIX)
            new_user = User(
                email=email,
                password=password,
                name=form.name.data,
                permissions='user'
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home_page'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if not user:
            flash("There is no user registered under this email, please try again.")
        elif not check_password_hash(f"{HASH_PREFIX}{user.password}", form.password.data):
            flash("The password you typed for this email is incorrect, please try again.")
        else:
            login_user(user)
            return redirect(url_for('home_page'))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_page'))


@app.route("/", methods=['GET'])
def home_page():
    product_list = db.session.execute(
        db.select(Products).order_by(func.random()).limit(10).where(Products.stock > 0)).scalars().all()
    products = product_list[:6]
    deals = product_list[6:]
    return render_template('index.html', products=products, deals=deals)


@app.route("/<string:category>")
def category_page(category):
    products = db.session.execute(
        db.select(Products).order_by(func.random()).limit(8).where(Products.category == category, Products.stock > 0)).scalars().all()
    return render_template('category.html', products=products, category=category)


@app.route("/cart")
@login_required
def cart_page():
    cart = db.session.execute(db.select(Products, Cart.quantity).join(Cart).where(Cart.user_id == current_user.user_id))
    cart_items = cart.all()
    return render_template('cart.html', cart=cart_items)


@app.route("/cart-add")
@login_required
def cart_add():
    user_id = current_user.user_id
    product_id = int(flask_request.args.get("product_id"))
    discounted = bool(flask_request.args.get("discounted"))

    cart_item = db.session.execute(
        db.select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)).scalar()
    product = db.session.execute(db.select(Products).where(Products.product_id == product_id)).scalar()

    if product.stock == 0:
        flash("You cannot add to cart, currently out of stock.")
        return redirect(url_for('cart_page'))
    elif cart_item:
        product.stock -= 1
        cart_item.quantity += 1
        db.session.commit()
    else:
        new_item = Cart(
            user_id=user_id,
            product_id=product_id,
            discounted=discounted,
            quantity=1
        )
        db.session.add(new_item)
        product.stock -= 1
        db.session.commit()
    return redirect(url_for('cart_page'))


@app.route('/cart-delete')
@login_required
def cart_delete():
    user_id = current_user.user_id
    product_id = int(flask_request.args.get('product_id'))

    cart_item = db.session.execute(
        db.select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)).scalar()
    product = db.session.execute(db.select(Products).where(Products.product_id == product_id)).scalar()

    if cart_item.quantity == 1:
        product.stock += 1
        db.session.delete(cart_item)
        db.session.commit()
    else:
        product.stock += 1
        cart_item.quantity -= 1
        db.session.commit()
    return redirect(url_for('cart_page'))


@app.route('/admin-panel')
@admin_only
def admin_panel():
    return render_template('admin.html')


@app.route('/add-product-manual', methods=['GET', 'POST'])
@admin_only
def add_product_manual():
    form = ProductForm()
    form.category.choices = [('electronics', 'Electronics'), ('fashion', 'Fashion'),
                             ('home', 'Home'), ('beauty', 'Beauty')]
    if form.validate_on_submit():

        product = db.session.execute(db.select(Products).where(Products.name == form.name.data)).scalar()
        if product:
            flash(f"{product.name} already exists, please try again.")
            return redirect(url_for('add_product_manual'))
        else:
            new_product = Products(
                name=form.name.data.title(),
                description=form.description.data,
                price=form.price.data,
                discount=form.discount.data,
                thumbnail=form.thumbnail.data,
                image=form.image.data,
                category=form.category.data,
                stock=form.stock.data,
            )
            db.session.add(new_product)
            db.session.commit()
            flash(f"{form.name.data.title()} successfully added!")
            return redirect(url_for('admin_panel'))
    return render_template('manual.html', form=form)


@app.route("/add-product-api", methods=['GET', 'POST'])
@admin_only
def add_product_api():
    categories = [('beauty', 'beauty'), ('fragrances', 'beauty'), ('skin-care', 'beauty'),
                  ('furniture', 'home'), ('home-decoration', 'home'), ('kitchen-accessories', 'home'),
                  ('laptops', 'electronics'), ('mobile-accessories', 'electronics'), ('smartphones', 'electronics'),
                  ('tablets', 'electronics'), ('mens-shirts', 'fashion'), ('mens-shoes', 'fashion'),
                  ('mens-watches', 'fashion'), ('sports-accessories', 'fashion'), ('sunglasses', 'fashion'),
                  ('tops', 'fashion'), ('womens-bags', 'fashion'), ('womens-dresses', 'fashion'),
                  ('womens-jewellery', 'fashion'), ('womens-shoes', 'fashion'), ]
    if flask_request.method == 'POST':
        product_type = flask_request.form.get('product_type')
        category = flask_request.form.get('category')
        response = requests.get(f'https://dummyjson.com/products/category/{product_type}')
        data = response.json()['products']

        for product in data:

            product_query = db.session.execute(db.select(Products).where(Products.name == product['title'])).scalar()
            if product_query:
                flash(f"{product_query.name} already exists.")
                continue
            else:
                new_product = Products(
                    name=product['title'],
                    description=product['description'],
                    price=product['price'],
                    discount=product['discountPercentage'] / 100,
                    thumbnail=product['thumbnail'],
                    image=product['images'][0],
                    category=category,
                    stock=product['stock'],
                )

                db.session.add(new_product)
                db.session.commit()
                flash(f"{new_product.name} successfully added!")
            return redirect(url_for('admin_panel'))
    return render_template('api.html', categories=categories)


if __name__ == "__main__":
    app.run(debug=False)
