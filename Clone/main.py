import os
from sqlalchemy.sql.functions import current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
# FLASK Imports
from flask import Flask, render_template, url_for, redirect, flash
from flask import request as flask_request
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from forms import LoginForm, RegisterForm
#SQLAlchemy Imports
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, Float, ForeignKey, func
from typing import List
from functools import wraps

HASH_KEY = os.getenv('HASH_KEY')

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

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{db_user}:{db_password}@localhost/{db_name}"
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Create Databases

class User(UserMixin, db.Model):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_permissions: Mapped[str] = mapped_column(String(20), nullable=False)
    user_email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    user_password: Mapped[str] = mapped_column(String(200), nullable=False)
    user_name: Mapped[str] = mapped_column(String(100), nullable=False)

    def __init__(self, email, permissions, name, password):
        self.user_email = email
        self.user_permissions = permissions
        self.user_password = password
        self.user_name = name

    def get_id(self):
        return f"{self.user_id}"

class Products(db.Model):
    __tablename__ = "products"
    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    product_description: Mapped[str] = mapped_column(String(500), nullable=False)
    product_price: Mapped[float] = mapped_column(Float, nullable=False)
    product_discount: Mapped[float] = mapped_column(Float, nullable=True)
    product_thumbnail: Mapped[str] = mapped_column(String(100), nullable=False)
    product_image: Mapped[str] = mapped_column(String(100), nullable=False)
    product_category: Mapped[str] = mapped_column(String(30))

class Cart(db.Model):
    __tablename__ = 'carts'
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), primary_key=True)
    discounted: Mapped[bool] = mapped_column(Boolean, nullable=False)


# Set up tables and admin
# with app.app_context():
#     db.create_all()
#
# new_user = User(name='Charlie', permissions='admin', email='charlieyoussef21@gmail.com',
#                     password=generate_password_hash('12345678', "pbkdf2:sha256",salt_length=2))
# db.session.add(new_user)
# db.session.commit()

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        user = db.session.execute(db.select(User).where(User.user_email == email)).scalar()
        if user:
            flash("There is already an account registered under this email, please log in instead.")
            return redirect(url_for('login'))
        hs_password = generate_password_hash(
            form.password.data, HASH_KEY, salt_length=2)
        password = hs_password.split(':')[2]
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
        user = db.session.execute(db.select(User).where(User.user_email == email)).scalar()
        if not user:
            flash("There is no user registered under this email, please try again.")
        elif not check_password_hash(f"{HASH_KEY}:{user.user_password}", form.password.data):
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

@app.route("/")
def home_page():
    product_list = db.session.execute(db.select(Products).order_by(func.random()).limit(12)).scalars().all()
    products = product_list[:6]
    deals = product_list[6:]
    return render_template('index.html', products=products, deals=deals)

@app.route("/<string:category>")
def category_page(category):
    products = db.session.execute(db.select(Products).where(Products.product_category == category)).scalars().all()
    return render_template('category.html', products=products, category=category)

@app.route("/cart/<int:user_id>")
@login_required
def cart_page(user_id):
    cart = db.session.execute(db.select(Cart).where(Cart.user_id == user_id)).scalars().all()
    cart_items = []
    for item in cart:
        product = db.session.execute(db.select(Products).where(Products.product_id == item.product_id)).scalar()
        cart_items.append(product)
    return render_template('cart.html', cart=cart_items, user_id=user_id)

@app.route("/cart-add")
@login_required
def cart_add():
    user_id = int(flask_request.args.get("user_id"))
    product_id = int(flask_request.args.get("product_id"))
    discounted = bool(flask_request.args.get("discounted"))
    new_item = Cart(
        user_id=user_id,
        product_id=product_id,
        discounted=discounted
    )
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('cart_page', user_id=user_id))


@app.route('/cart-delete')
@login_required
def cart_delete():
    user_id = int(flask_request.args.get('user_id'))
    product_id = int(flask_request.args.get('product_id'))
    cart_item = db.session.execute(db.select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)).scalar()
    db.session.delete(cart_item)
    db.session.commit()
    return redirect(url_for('cart_page', user_id=user_id))


@app.route("/add-products")
def add_products():
    response = requests.get('https://dummyjson.com/products/category/home-decoration')
    data = response.json()['products']

    for product in data:
        name = product['title']
        description = product['description']
        price = product['price']
        discount = product['discountPercentage'] / 100
        thumbnail = product['thumbnail']
        image = product['images'][0]
        category = 'home'

        new_product = Products(
            product_name=name,
            product_description=description,
            product_price=price,
            product_discount=discount,
            product_thumbnail=thumbnail,
            product_image=image,
            product_category=category
        )

        db.session.add(new_product)
        db.session.commit()
    return redirect(url_for('home_page'))

if __name__ == "__main__":
    app.run(debug=True)