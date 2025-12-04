from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DB = "database.db"

def query_db(query, args=(), one=False):
    """Utility function to query SQLite database"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(query, args)
    data = cur.fetchall()
    conn.commit()
    conn.close()
    return data[0] if one else data

# Signup route (will fail if user exists)
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    try:
        query_db("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": "User already exists"}), 409

# Login route
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    user = query_db("SELECT id, email, password, role FROM users WHERE email=?", (email,), one=True)
    
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404
    
    if user[2] != password:
        return jsonify({"success": False, "error": "Incorrect password"}), 401
    
    # Send role to decide page redirect
    return jsonify({"success": True, "role": user[3]})

# Products route
@app.route("/products")
def products():
    items = query_db("SELECT id, name, price FROM products")
    return jsonify(items)

if __name__ == "__main__":
    app.run(debug=True)
