from flask import Flask, request, jsonify, session
from flask_cors import CORS
from models import db, User
from config import Config
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.user_routes import student_bp
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)



CORS(app, supports_credentials=True, origins=["http://localhost:8080"])



app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "supersecretkey")
app.config["SESSION_TYPE"] = "filesystem"


def create_admin():
    try:
        admin_username = os.getenv("ADMIN_USERNAME")
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")

        if not admin_username or not admin_email or not admin_password:
            print("Admin credentials are missing in .env!")
            return

        existing_admin = User.query.filter_by(role='admin').first()
        if existing_admin:
            print("Admin already exists.")
            return

        admin_user = User(
            username=admin_username,
            email=admin_email,
            password_hash=generate_password_hash(admin_password),
            role='admin'
        )

        db.session.add(admin_user)
        db.session.commit()
        print("Admin created successfully!")
    except Exception as e:
        print(f"Error creating admin: {e}")

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(student_bp, url_prefix='/student')

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello World!'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True)
