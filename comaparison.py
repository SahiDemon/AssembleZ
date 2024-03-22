import psycopg2
from rapidfuzz import fuzz, process
import re

# Function to extract the first word of a title
def extract_first_word(title):
    return title.split()[0].lower()

def find_matches(gamestreet_titles, nanotek_titles, threshold=85):
    matches = []
    for gs_title in gamestreet_titles:
        gs_first_word = extract_first_word(gs_title)
        
        for nt_title in nanotek_titles:
            nt_first_word = extract_first_word(nt_title)
            
            # Check if the first word matches
            if gs_first_word == nt_first_word:
                # If the first words match, proceed with fuzzy matching
                gs_features = extract_key_features(gs_title)
                nt_features = extract_key_features(nt_title)
                
                # Calculate fuzzy match score between the full titles or extracted features
                score = fuzz.WRatio(gs_features, nt_features)
                
                if score > threshold:
                    matches.append((gs_title, nt_title, score))
    return matches

# Define the extract_key_features function if not defined previously
def extract_key_features(title):
    """Extract model numbers or significant keywords from a title."""
    pattern = r'\b[A-Z0-9]+(?:-[A-Z0-9]+)+\b'  # Adjust this pattern for your needs
    matches = re.findall(pattern, title, re.IGNORECASE)
    return ' '.join(matches)

# Database connection and fetching titles (placeholder code)
conn = psycopg2.connect(
    host="aws-0-us-west-1.pooler.supabase.com",
    port=5432,
    dbname="postgres",
    user="postgres.cgojfztufkrckindwkuf",
    password="Sahiya_448866"
)

def fetch_product_titles(schema, table):
    """Fetch product titles from a specified schema and table."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT title FROM {schema}.{table};")
        titles = [row[0] for row in cur.fetchall()]
    return titles

# Fetch product titles from your database
gamestreet_titles = fetch_product_titles('gamestreet', 'processors')
nanotek_titles = fetch_product_titles('nanotek', 'processors')

# Find matches between product titles
matches = find_matches(gamestreet_titles, nanotek_titles)

# Print the matches found
for gs_title, nt_title, score in matches:
    print(f"Match found: {gs_title} | {nt_title} | Score: {score}")

# Close the database connection
conn.close()
