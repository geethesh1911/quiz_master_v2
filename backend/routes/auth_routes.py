from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User, Subject
from flask_cors import cross_origin
import jwt
from datetime import datetime
auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    return "@" in email and "." in email and email.index("@") < email.rindex(".")

def is_strong_password(password):
    if len(password) < 8:
        return False
    has_upper = has_lower = has_digit = has_special = False
    special_characters = "!@#$%^&*(),.?\":{}|<>"

    for char in password:
        if char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char.isdigit():
            has_digit = True
        elif char in special_characters:
            has_special = True

    return has_upper and has_lower and has_digit and has_special

@auth_bp.route('/signup', methods=['POST'])
@cross_origin()
def signup():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', 'student').strip().lower()  # Default role is 'student'

    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 400

    if not is_strong_password(password):
        return jsonify({
            'error': 'Password must be at least 8 characters long, contain an uppercase letter, '
                     'a lowercase letter, a digit, and a special character'
        }), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    hashed_password = generate_password_hash(password)

    new_user = User(username=username, email=email, password_hash=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()


    return jsonify({'message': 'User registered successfully', 'role': new_user.role}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    user.last_visited_at = datetime.utcnow()
    db.session.commit()

    token = jwt.encode({'user_id': user.id, 'role': user.role}, 'geet', algorithm='HS256')

    return jsonify({
        'message': 'Login successful',
        'role': user.role,
        "token": token
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():

    return jsonify({'message': 'Logout successful'}), 200

def is_authenticated():
    """ Helper function to check if user is logged in """
    return 'user_id'
