from flask import Flask, render_template
import psycopg2
import sqlite3

app = Flask(__name__)

# Function to fetch data from the database based on category
def get_product_data(category):
    conn = psycopg2.connect(user="postgres.cgojfztufkrckindwkuf", password="Sahiya_448866", host="aws-0-us-west-1.pooler.supabase.com", port="5432", dbname="postgres")
    cursor = conn.cursor()
    cursor.execute(f"SELECT title, price, stock, image_url FROM {category}")
    products = cursor.fetchall()
    conn.close()
    return products


# Define a route for the homepage
@app.route('/')
def home():
    return render_template('index.html')

# Define a route to display the product information for a specific category
@app.route('/products/<category>')
def display_products(category):
    # Get product data based on the category
    products = get_product_data(category)

    # Determine a suitable title for the category
    category_titles = {
        "GraphicCards": "Graphic Cards",
        "MemoryRAM": "Memory RAM",
        "MotherBoards": "Motherboards",
        "Processors": "Processors"
    }

    # Render an HTML template to display the product data with category title
    return render_template('products.html', products=products, category_title=category_titles.get(category, "Unknown Category"))

if __name__ == "__main__":
    app.run(debug=True)
