# Flask e-Shop

A full-featured e-commerce web application built with Flask and styled with Bootstrap to mimic the look and feel of Amazon. The application includes user authentication, product browsing, a shopping cart, and an admin panel for product management.

## Features

*   **User Authentication:** Secure user registration, login, and logout functionality. Passwords are securely hashed.
*   **Product Catalog:**
    *   View featured products and deals on the homepage.
    *   Browse products by category (Electronics, Fashion, Home, Beauty).
*   **Shopping Cart:**
    *   Add/remove items to a persistent shopping cart for logged-in users.
    *   Adjust item quantities directly from the cart page.
*   **Admin Panel:**
    *   Restricted access for users with 'admin' permissions.
    *   Add new products to the store either manually through a form or by fetching data from the [dummyjson.com](https://dummyjson.com/products) API.
*   **Database Integration:** Uses Flask-SQLAlchemy with a MySQL database to manage users, products, and carts.

## Technology Stack

*   **Backend:** Python, Flask
*   **Database:** MySQL, SQLAlchemy
*   **Frontend:** HTML, CSS, Bootstrap 5
*   **Libraries:** Flask-Login (User Session Management), Flask-WTF (Forms), Werkzeug (Password Hashing), Requests (API Calls)

## Setup and Installation

Follow these steps to get the application running on your local machine.

**1. Clone the repository:**

```bash
git clone https://github.com/cyoussef21/flask-eshop.git
cd flask-eshop
```

**2. Create and activate a virtual environment:**

```bash
# For Unix/macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies:**

```bash
pip install -r requirements.txt
```

**4. Set up the database:**

This project is configured to use a MySQL database.
*   Ensure you have a MySQL server running.
*   Create a new database (e.g., `flask_eshop`).

**5. Configure Environment Variables:**

You need to set the following environment variables. You can do this by exporting them in your terminal session or by using a `.env` file (and a library like `python-dotenv`).

*   `FLASK_SECRET_KEY`: A random secret key for Flask sessions.
*   `DB_USER`: Your MySQL username.
*   `DB_PASSWORD`: Your MySQL password.
*   `DB_NAME`: The name of the database you created (e.g., `flask_eshop`).
*   `HASH_KEY`: A hashing algorithm like `sha256`.
*   `HASH_PREFIX`: The prefix to be added to the hashed password string, matching the method (e.g., `pbkdf2:sha256`).

**6. Initialize the Database Tables:**

Run a Python shell in your project directory and execute the following commands to create the necessary tables in your database.

```python
from main import app, db
with app.app_context():
    db.create_all()
```

**7. Run the application:**

```bash
python main.py
```

The application will be available at `http://127.0.0.1:5000`.

## Usage

### As a User

1.  Navigate to `http://127.0.0.1:5000`.
2.  Click "Create your account" to register.
3.  Log in with your new credentials.
4.  Browse products on the homepage or via the category links.
5.  Click "Add" on any product to add it to your shopping cart.
6.  Click the "Cart" icon in the navigation bar to view your cart, adjust quantities, or remove items.

### As an Admin

To access the admin panel, you must first manually update a user's permissions in the database.

1.  Register a user through the web interface.
2.  Connect to your MySQL database and find the user you just created in the `users` table.
3.  Update their `permissions` column from `'user'` to `'admin'`.
4.  Log in as this user. You will now see an "Admin Panel" link in the header.
5.  From the admin panel, you can:
    *   **Product Add (API):** Choose a product category to automatically fetch and add products from `dummyjson.com`.
    *   **Product Add (Manual):** Fill out a form to add a new product with all its details.