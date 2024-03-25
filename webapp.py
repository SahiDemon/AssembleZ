from flask import Flask, render_template, request
import psycopg2

app = Flask(__name__)

SCHEMA_NAME = "nanotek"

# Database connection details
DB_CONFIG = {
    "user": "postgres.cgojfztufkrckindwkuf",
    "password": "Sahiya_448866",
    "host": "aws-0-us-west-1.pooler.supabase.com",
    "port": "5432",
    "dbname": "postgres"
}

# Function to fetch data from the database based on category
def get_product_data(category):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = f"SELECT id, title, price, stock, image_url FROM {SCHEMA_NAME}.{category}"
    cursor.execute(query)
    products = cursor.fetchall()
    conn.close()
    return products

# Function to fetch a single product's details by ID
def get_product_data_by_id(category, product_id):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = f"SELECT id, title, price, stock, image_url FROM {SCHEMA_NAME}.{category} WHERE id = %s"
    cursor.execute(query, (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

# Homepage route
@app.route('/')
def home():
    return render_template('index.html')

# About page route
@app.route('/about')
def about():
    return render_template('about.html')

# Route for displaying products by category
@app.route('/products/<category>')
def display_products(category):
    products = get_product_data(category)
    category_titles = {
        "GraphicCards": "Graphic Cards",
        "MemoryRAM": "Memory RAM",
        "MotherBoards": "Motherboards",
        "Processors": "Processors",
        "Casings": "Casings"
    }
    return render_template('products.html', products=products, category_title=category_titles.get(category, "Unknown Category"), category=category)
# Route for displaying individual product details
@app.route('/product/<category>/<int:product_id>')
def product_detail(category, product_id):
    product = get_product_data_by_id(category, product_id)
    if not product:
        return "Product not found", 404
    return render_template('compare.html', product=product)

if __name__ == "__main__":
    app.run(debug=True)
