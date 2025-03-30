import os
from flask import Blueprint, request, jsonify,send_from_directory,after_this_request
from models import db, User, Quiz, Question, Score, Chapter, Subject
import jwt
from functools import wraps
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from tasks import export_csv_task, init_celery
from flask_mail import Message
from extensions import mail
from flask import current_app

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
# In get_available_quizzes route, add date_of_quiz:
@student_bp.route("/quizzes/available", methods=["GET"])
@student_required
def get_available_quizzes():
    quizzes = Quiz.query.filter(Quiz.date_of_quiz <= datetime.utcnow()).all()
    return jsonify([{
        "id": q.id,
        "date_of_quiz": q.date_of_quiz.isoformat(), 
        "chapter": q.chapter.name,
        "subject": q.chapter.subject.name,
        "duration": q.time_duration,
        "total_questions": len(q.questions)
    } for q in quizzes])


# Submit quiz answers
@student_bp.route("/quizzes/<int:quiz_id>/submit", methods=["POST"])
@student_required
def submit_quiz(quiz_id):
    try:
        data = request.get_json()
        user_id = verify_token(request.headers['Authorization'])["user_id"]
        
        if Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first():
            return jsonify({"error": "Already submitted"}), 400

        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        correct = sum(
            1 for q in questions 
            if str(data['answers'].get(str(q.id))) == str(q.correct_option)
        )

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

    except Exception as e:
        db.session.rollback()
        print(f"Submission error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

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

@student_bp.route("/results/<int:quiz_id>", methods=["GET"])
@student_required
def get_single_result(quiz_id):
    user_id = verify_token(request.headers['Authorization'])["user_id"]
    result = Score.query.options(
        joinedload(Score.quiz).joinedload(Quiz.chapter)
    ).filter_by(
        user_id=user_id,
        quiz_id=quiz_id
    ).first_or_404()

    return jsonify({
        "quiz": {
            "chapter": {
                "name": result.quiz.chapter.name
            }
        },
        "total_scored": result.total_scored,
        "total_questions": result.total_questions,
        "timestamp": result.timestamp.isoformat()
    })

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
    

@student_bp.route("/quizzes/<int:quiz_id>/start", methods=["GET"])
@student_required
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return jsonify({
        "questions": [{
            "id": q.id,
            "question": q.question_text,
            "options": [q.option_1, q.option_2, q.option_3, q.option_4]
        } for q in quiz.questions],
        "duration": quiz.time_duration ,
        "updated_at": quiz.date_of_quiz.isoformat()
    })

@student_bp.route("/performance", methods=["GET"])
@student_required
def get_student_performance():
    user_id = verify_token(request.headers['Authorization'])["user_id"]
    
    recent_attempts = db.session.query(
        Quiz.id,
        Chapter.name.label('chapter_name'),
        Score.total_scored,
        Score.total_questions,
        Score.timestamp
    ).join(Chapter, Quiz.chapter_id == Chapter.id).join(Score, Quiz.id == Score.quiz_id).filter(Score.user_id == user_id).order_by(Score.timestamp.desc()).limit(5).all()
    # Overall Performance
    scores = Score.query.filter_by(user_id=user_id).all()
    total_quizzes = len(scores)
    average_score = sum(s.total_scored for s in scores) / sum(s.total_questions for s in scores) * 100 if scores else 0
    
    subjects = db.session.query(
        Subject.name,
        func.avg(Score.total_scored).label('avg_score'),
        func.sum(Score.total_scored).label('total_correct'),
        func.sum(Score.total_questions).label('total_questions')
    ).join(Chapter, Subject.id == Chapter.subject_id).join(Quiz, Chapter.id == Quiz.chapter_id).join(Score, Quiz.id == Score.quiz_id).filter(Score.user_id == user_id).group_by(Subject.name).all()

    # Format response
    return jsonify({
        "overview": {
            "total_quizzes": total_quizzes,
            "average_score": round(average_score, 1),
            "total_correct": sum(s.total_scored for s in scores),
            "total_attempted": sum(s.total_questions for s in scores)
        },
        "subjects": [{
            "name": sub[0],
            "accuracy": round((sub[1]/sub[3])*100, 1) if sub[3] else 0,
            "total_questions": sub[3],
            "correct": sub[2]
        } for sub in subjects]
        ,
        "recent_attempts": [{
            "id": attempt.id,
            "chapter": attempt.chapter_name,
            "score": attempt.total_scored,
            "total": attempt.total_questions,
            "percentage": round((attempt.total_scored/attempt.total_questions)*100, 1),
            "date": attempt.timestamp.strftime('%Y-%m-%d')
        } for attempt in recent_attempts]
    })

