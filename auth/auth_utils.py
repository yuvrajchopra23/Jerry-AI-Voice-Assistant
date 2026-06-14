import jwt 
import bcrypt 
import datetime
from config import JWT_SECRET

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed:str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def generate_token(user_id: str, username: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days = 7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm = "HS256")

def verify_token(token: str) -> dict:
    try:
        print(f"[JWT] Verifying with secret: '{JWT_SECRET}'")
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        print("[JWT] Token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"[JWT] Invalid token: {e}")
        return None