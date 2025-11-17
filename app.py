from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
import json
import os
from pymongo import MongoClient
from bson import ObjectId
import certifi

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# JSON file for backend data storage
DATA_FILE = 'data.json'

# MongoDB Atlas configuration
MONGO_URI = "your_mongodb_connection_string_here"
DB_NAME = "flask_app"
COLLECTION_NAME = "user_data"

# Initialize MongoDB client
try:
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print("Connected to MongoDB Atlas successfully")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    collection = None

def initialize_data_file():
    """Create initial data file if it doesn't exist"""
    if not os.path.exists(DATA_FILE):
        initial_data = [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
            {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"}
        ]
        with open(DATA_FILE, 'w') as f:
            json.dump(initial_data, f, indent=4)

@app.route('/')
def index():
    """Render the main form page"""
    return render_template('index.html')

@app.route('/api')
def api_route():
    """API route that returns JSON data from backend file"""
    try:
        # Read data from JSON file
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        
        return jsonify({
            "status": "success",
            "data": data,
            "count": len(data)
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/submit', methods=['POST'])
def submit_form():
    """Handle form submission and insert data into MongoDB"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            email = request.form.get('email')
            age = request.form.get('age')
            city = request.form.get('city')
            
            # Validate required fields
            if not name or not email:
                flash("Name and Email are required fields!", "error")
                return render_template('index.html')
            
            # Create document for MongoDB
            user_data = {
                "name": name,
                "email": email,
                "age": int(age) if age else None,
                "city": city,
                "timestamp": datetime.datetime.utcnow()
            }
            
            # Insert into MongoDB
            if collection:
                result = collection.insert_one(user_data)
                print(f"Data inserted with ID: {result.inserted_id}")
            else:
                flash("Database connection error. Please try again later.", "error")
                return render_template('index.html')
            
            # Redirect to success page
            return redirect(url_for('success_page'))
            
        except Exception as e:
            flash(f"Error submitting data: {str(e)}", "error")
            return render_template('index.html')

@app.route('/success')
def success_page():
    """Display success page after form submission"""
    return render_template('success.html')

@app.route('/api/users')
def get_all_users():
    """API route to get all users from MongoDB"""
    try:
        if collection:
            users = list(collection.find({}, {'_id': 0}))  # Exclude ObjectId
            return jsonify({
                "status": "success",
                "data": users,
                "count": len(users)
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Database not connected"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    initialize_data_file()
    app.run(debug=True)
