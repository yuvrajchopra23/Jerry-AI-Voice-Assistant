from flask import Blueprint, request, jsonify
from db.mongo import users_col, memory_col
from auth.auth_utils import hash_password, check_password, generate_token, verify_token
from bson import ObjectId

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username", "").strip().lower()
    password = data.get("password", "").strip()
    email = data.get("email", "").strip().lower()

    if not username or not password or not email:
        return jsonify({"error": "All fields are required"}), 400
    
    if len (password) < 6:
        return jsonify({"error": "password must be at Least 6 characters Long"}), 400
    
    if users_col.find_one({"username": username}):
        return jsonify({"error": "username already exists"}), 400
    
    if users_col.find_one({"email": email}):
        return jsonify({"error": "email already exists"}), 400
    
    user = {
        "username": username,
        "password": hash_password(password),
        "email": email,
        "created_at": str(__import__("datetime").datetime.utcnow())
    }
    result = users_col.insert_one(user)
    user_id = str(result.inserted_id)

    memory_col.insert_one({
        "user_id": user_id,
        "websites": {},
        "apps": {},
        "history": [],
        "learned_commands": {}
    })

    token = generate_token(user_id)
    return jsonify({
        "message": "User created successfully",
        "token": token,
        "username": username,
        "user_id": user_id
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip().lower()
    password = data.get("password", "").strip()

    print(f"[LOGIN] Attempting: '{username}'")  # add this

    user = users_col.find_one({
        "$or": [{"username": username}, {"email": username}]
    })

    print(f"[LOGIN] User found: {user}")  # add this

    if not user:
        print("[LOGIN] No user found")  # add this
        return jsonify({"error": "Invalid username or password."}), 401

    password_match = check_password(password, user["password"])
    print(f"[LOGIN] Password match: {password_match}")  # add this

    if not password_match:
        return jsonify({"error": "Invalid username or password."}), 401

    user_id = str(user["_id"])
    token = generate_token(user_id, user["username"])
    print(f"[LOGIN] Token generated successfully for {user['username']}")

    return jsonify({
        "message": "Login successful.",
        "token": token,
        "username": user["username"],
        "user_id": user_id
    }), 200
    
@auth_bp.route("/verify", methods=["GET"])

def verify():
    token = request.headers.get("Authorization", "").replace("bearer", "")
    if not token:
        return jsonify({"error": "token is required"}), 401
    
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "invalid or expired token"}), 401
    
    return jsonify({
        "message": "token is valid",
        "username": payload["username"],
        "user_id": payload["user_id"]
    }), 200


