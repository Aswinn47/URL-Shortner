# app.py
from flask import render_template
from flask import Flask, request, redirect, jsonify
from models import db, URL  # This will come from models.py
from utils import generate_short_code  # This will come from utils.py

app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create the database tables when the app starts
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')


# ➤ Route to shorten URLs
@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    original_url = data.get('url')

    if not original_url:
        return jsonify({'error': 'Missing URL'}), 400

    # Generate a unique short code
    short_code = generate_short_code()
    while URL.query.filter_by(short_code=short_code).first():
        short_code = generate_short_code()

    # Save to database
    new_url = URL(original_url=original_url, short_code=short_code)
    db.session.add(new_url)
    db.session.commit()

    # Create the short URL using the current host
    short_url = request.host_url + short_code
    return jsonify({'short_url': short_url})

# ➤ Route to redirect using the short code
@app.route('/<short_code>')
def redirect_to_original(short_code):
    url_entry = URL.query.filter_by(short_code=short_code).first()
    if url_entry:
        url_entry.clicks += 1
        db.session.commit()
        return redirect(url_entry.original_url)
    else:
        return jsonify({'error': 'Short URL not found'}), 404

# ➤ Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
