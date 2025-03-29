
from flask import Blueprint, request, jsonify
from models import db, User, Quiz, Question, Score, Chapter, Subject
import jwt
from functools import wraps
from datetime import datetime

student_bp = Blueprint("student", __name__, url_prefix="/student")

ALGORITHM = "HS256"
SECRET_KEY = "geet"

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
            
        payload = verify_token(token)
        if not payload or payload.get("role") != "student":
            return jsonify({"error": "Unauthorized"}), 403
            
        return f(*args, **kwargs)
    return decorated_function

# --- Student Routes --- #

# Get available quizzes (student version)
@student_bp.route("/quizzes/available", methods=["GET"])
@student_required
def get_available_quizzes():
    quizzes = Quiz.query.filter(Quiz.date_of_quiz <= datetime.utcnow()).all()
    return jsonify([{
        "id": q.id,
        "chapter": q.chapter.name,
        "subject": q.chapter.subject.name,
        "duration": q.time_duration,
        "total_questions": len(q.questions)
    } for q in quizzes])

# Start a quiz (returns questions without answers)
@student_bp.route("/quizzes/<int:quiz_id>/start", methods=["GET"])
@student_required
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return jsonify([{
        "id": q.id,
        "question": q.question_text,
        "options": [q.option_1, q.option_2, q.option_3, q.option_4]
    } for q in quiz.questions])

# Submit quiz answers
@student_bp.route("/quizzes/<int:quiz_id>/submit", methods=["POST"])
@student_required
def submit_quiz(quiz_id):
    data = request.get_json()
    user_id = verify_token(request.headers['Authorization'])["user_id"]
    
    if Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first():
        return jsonify({"error": "Already submitted"}), 400

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    correct = sum(1 for q in questions if str(data.get(str(q.id))) == str(q.correct_option))

    score = Score(
        user_id=user_id,
        quiz_id=quiz_id,
        total_scored=correct,
        total_questions=len(questions)
    )
    db.session.add(score)
    db.session.commit()

    return jsonify({
        "score": correct,
        "total": len(questions),
        "percentage": round((correct / len(questions)) * 100, 2)
    })

@student_bp.route("/results", methods=["GET"])
@student_required
def get_results():
    user_id = verify_token(request.headers['Authorization'])["user_id"]
    scores = Score.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "quiz_id": s.quiz_id,
        "chapter": s.quiz.chapter.name,
        "score": f"{s.total_scored}/{s.total_questions}",
        "date": s.timestamp.isoformat()
    } for s in scores])

@student_bp.route("/profile", methods=["GET", "PUT"])
@student_required
def profile():
    user_id = verify_token(request.headers['Authorization'])["user_id"]
    user = User.query.get_or_404(user_id)
    
    if request.method == "GET":
        return jsonify({
            "username": user.username,
            "email": user.email,
            "dob": user.dob.isoformat() if user.dob else None
        })
    
    elif request.method == "PUT":
        data = request.get_json()
        if 'email' in data: 
            user.email = data['email']
        if 'dob' in data:
            user.dob = datetime.fromisoformat(data['dob'])
        db.session.commit()
        return jsonify({"message": "Profile updated"})
