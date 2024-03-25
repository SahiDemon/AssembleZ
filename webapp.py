from flask import Flask, render_template, url_for
import psycopg2
import re
from rapidfuzz import fuzz

app = Flask(__name__)

# Database connection details
DB_CONFIG = {
    "user": "postgres.cgojfztufkrckindwkuf",
    "password": "Sahiya_448866",
    "host": "aws-0-us-west-1.pooler.supabase.com",
    "port": "5432",
    "dbname": "postgres"
}

# Function to connect to the database
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# Define Jinja2 filter within the app context
@app.template_filter('format_description')
def format_description(description):
    formatted = "<div class=\"product-description\">"
    lines = description.split("\n")
    for line in lines:
        if line.strip():
            key_value = line.split(":", 1)
            if len(key_value) == 2:
                key, value = key_value
                formatted += f"<div><strong>{key.strip()}:</strong> {value.strip()}</div>"
            else:
                formatted += f"<div>{line.strip()}</div>"
    formatted += "</div>"
    return formatted
# Extract key features from a title for matching
def extract_key_features(title):
    pattern = r'\b[A-Z0-9]+(?:-[A-Z0-9]+)+\b'
    matches = re.findall(pattern, title, re.IGNORECASE)
    return ' '.join(matches)

# Verify if two products match
def verify_match(nt_product, gs_product):
    if not nt_product or not gs_product:
        return False
    nt_title = nt_product[1]
    gs_title = gs_product[1]
    nt_features = extract_key_features(nt_title)
    gs_features = extract_key_features(gs_title)
    score = fuzz.WRatio(nt_features, gs_features)
    return score >= 85  # Adjust the threshold as needed

# Fetch product titles from a specified schema and table
def fetch_product_titles(schema, category):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(f"SELECT id, title, price, stock, image_url , product_info FROM {schema}.{category};")
        products = cur.fetchall()
    conn.close()
    return products

# Get combined product data, handling duplicates
def get_combined_product_data(category):
    nanotek_products = fetch_product_titles('nanotek', category)
    gamestreet_products = fetch_product_titles('gamestreet', category)
    combined_products = [{"nanotek": nt_product, "gamestreet": None} for nt_product in nanotek_products]
    
    matched_gamestreet_ids = set()
    for gs_product in gamestreet_products:
        for combined_product in combined_products:
            nt_product = combined_product["nanotek"]
            if verify_match(nt_product, gs_product):
                combined_product["gamestreet"] = gs_product
                matched_gamestreet_ids.add(gs_product[0])
                break

    for gs_product in gamestreet_products:
        if gs_product[0] not in matched_gamestreet_ids:
            combined_products.append({"nanotek": None, "gamestreet": gs_product})

    return combined_products

# Function to get product details from both schemas and verify match
def get_product_details(category, product_id):
    details = get_combined_product_data(category)
    for detail in details:
        nt_product = detail["nanotek"]
        gs_product = detail["gamestreet"]
        if nt_product and nt_product[0] == product_id:
            return detail
        if gs_product and gs_product[0] == product_id:
            return detail
    return {"nanotek": None, "gamestreet": None}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/products/<category>')
def display_products(category):
    combined_products = get_combined_product_data(category)
    category_titles = {
        "GraphicCards": "Graphic Cards",
        "MemoryRAM": "Memory RAM",
        "MotherBoards": "Motherboards",
        "Processors": "Processors",
        "Casings": "Casings"
    }
    return render_template('products.html', combined_products=combined_products, category_title=category_titles.get(category, "Unknown Category"), category=category)

@app.route('/product/<category>/<int:product_id>')
def product_detail(category, product_id):
    product_details = get_product_details(category, product_id)
    if not product_details["nanotek"] and not product_details["gamestreet"]:
        return "Product not found", 404
    return render_template('compare.html', product=product_details)

if __name__ == "__main__":
    app.run(debug=True)
