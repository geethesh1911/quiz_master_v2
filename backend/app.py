from flask import Flask, jsonify
from flask_mail import Mail, Message
from flask_cors import CORS
from models import db, User
from config import Config
from tasks import init_celery, create_export_task
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from extensions import mail

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, supports_credentials=True, origins=["http://localhost:8080"])
    
    # Configure Flask-Mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = '23f2003015@ds.study.iitm.ac.in'
    app.config['MAIL_PASSWORD'] = 'szpkxpbuuqbupfjh'
    app.config['MAIL_DEFAULT_SENDER'] = '23f2003015@ds.study.iitm.ac.in'
    
    mail.init_app(app)
    
    # Initialize Celery and create task
    celery = init_celery(app)
    export_csv_task = create_export_task(celery)
    
    # Make task available to app context
    app.export_csv_task = export_csv_task
    
    # Register blueprints
    from routes.user_routes import student_bp
    app.register_blueprint(student_bp, url_prefix='/student')
    
    return app, celery

app, celery = create_app()

@app.route('/hello')
def hello():
    return jsonify({'message': 'Hello World!'})

@app.route('/send-test-email')
def send_test_email():
    try:
        msg = Message(
            subject="Test Email from Flask-Mail",
            recipients=["shivasaicharand@gmail.com"],
            body="This is a plain-text email body",
            html="<b>This is an HTML email body</b>"
        )
        mail.send(msg)
        return "Email sent successfully!"
    except Exception as e:
        return f"Failed to send email: {str(e)}"

def create_admin():
    try:
        admin_username = os.getenv("ADMIN_USERNAME")
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")

        existing_admin = User.query.filter_by(role='admin').first()
        if existing_admin:
            print("Admin exists")
            return

        admin_user = User(
            username=admin_username,
            email=admin_email,
            password_hash=generate_password_hash(admin_password),
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin created!")
    except Exception as e:
        print(f"Admin error: {e}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    
    app.run(debug=True)