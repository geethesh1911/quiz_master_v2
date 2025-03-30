from flask import Blueprint, request, jsonify
from models import db, User, Subject, Chapter, Quiz, Question
import jwt
from functools import wraps
from sqlalchemy import func
from models import Score
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

ALGORITHM = "HS256"
SECRET_KEY = "geet"

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# Decorator to protect admin routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
            
        payload = verify_token(token)
        if not payload or payload.get("role") != "admin":
            return jsonify({"error": "Unauthorized"}), 403
            
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/subjects", methods=["GET", "POST"])
@admin_required
def handle_subjects():
    if request.method == "GET":
        subjects = Subject.query.all()
        return jsonify([{"id": sub.id, "name": sub.name, "description": sub.description} for sub in subjects])
    
    elif request.method == "POST":
        data = request.get_json()
        if not data or not data.get("name"):
            return jsonify({"error": "Subject name required"}), 400
        
        try:
            subject = Subject(
                name=data["name"],
                description=data.get("description", "") 
            )
            db.session.add(subject)
            db.session.commit()
            return jsonify({"message": "Subject added"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Error: {str(e)}"}), 500

@admin_bp.route("/subjects/<int:subject_id>", methods=["PUT", "DELETE"])
@admin_required
def manage_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({"error": "Subject not found"}), 404

    if request.method == "PUT":
        data = request.get_json()
        subject.name = data.get("name", subject.name)
        subject.description = data.get("description", subject.description)
        db.session.commit()
        return jsonify({"message": "Subject updated"}), 200
        
    elif request.method == "DELETE":
        db.session.delete(subject)
        db.session.commit()
        return jsonify({"message": "Subject deleted"}), 200

@admin_bp.route("/subjects/<int:subject_id>/chapters", methods=["POST"])
@admin_required
def add_chapter(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({"error": "Subject not found"}), 404

    data = request.get_json()
    chapter = Chapter(
        name=data["name"],
        description=data.get("description", ""),
        subject_id=subject_id
    )
    db.session.add(chapter)
    db.session.commit()
    return jsonify({"message": "Chapter added"}), 201

# Get chapters for a subject
@admin_bp.route("/subjects/<int:subject_id>/chapters", methods=["GET"])
@admin_required
def get_chapters(subject_id):
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    chapters_data = []
    for chapter in chapters:
        total_questions = sum(len(quiz.questions) for quiz in chapter.quizzes)
        chapters_data.append({
            "id": chapter.id,
            "name": chapter.name,
            "description": chapter.description,
            "total_questions": total_questions
        })
    return jsonify(chapters_data), 200

# Chapter management endpoints
@admin_bp.route("/chapters/<int:chapter_id>", methods=["PUT", "DELETE"])
@admin_required
def manage_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        return jsonify({"error": "Chapter not found"}), 404

    if request.method == "PUT":
        data = request.get_json()
        chapter.name = data.get("name", chapter.name)
        chapter.description = data.get("description", chapter.description)
        db.session.commit()
        return jsonify({"message": "Chapter updated"}), 200
        
    elif request.method == "DELETE":
        db.session.delete(chapter)
        db.session.commit()
        return jsonify({"message": "Chapter deleted"}), 200
    

# Quiz routes
@admin_bp.route("/quizzes", methods=["GET"])
@admin_required
def get_quizzes():
    quizzes = Quiz.query.all()
    quizzes_data = []
    for quiz in quizzes:
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)
        quizzes_data.append({
            "id": quiz.id,
            "chapter_id": quiz.chapter_id,
            "chapter_name": chapter.name,
            "subject_id": chapter.subject_id,
            "subject_name": subject.name,
            "date": quiz.date_of_quiz.isoformat(),
            "duration": quiz.time_duration,
            "remarks": quiz.remarks,
            "questions": [{
                "id": q.id,
                "title": q.title,
                "text": q.question_text,
                "options": [q.option_1, q.option_2, q.option_3, q.option_4],
                "correct": q.correct_option
            } for q in quiz.questions]
        })
    return jsonify(quizzes_data), 200

@admin_bp.route("/quizzes", methods=["POST"])
@admin_required
def create_quiz():
    data = request.get_json()
    try:
        quiz = Quiz(
            chapter_id=data["chapter_id"],
            time_duration=data.get("duration", 30),
            remarks=data.get("remarks", "")
        )
        db.session.add(quiz)
        db.session.commit()
        return jsonify({"message": "Quiz created", "id": quiz.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Question routes
@admin_bp.route("/questions", methods=["POST"])
@admin_required
def create_question():
    data = request.get_json()
    try:
        question = Question(
            title=data["title"],
            question_text=data["text"],
            option_1=data["options"][0],
            option_2=data["options"][1],
            option_3=data["options"][2],
            option_4=data["options"][3],
            correct_option=data["correct"],
            quiz_id=data["quiz_id"]
        )
        db.session.add(question)
        db.session.commit()
        return jsonify({"message": "Question added"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@admin_bp.route("/questions/<int:question_id>", methods=["PUT", "DELETE"])
@admin_required
def manage_question(question_id):
    question = Question.query.get(question_id)
    if not question:
        return jsonify({"error": "Question not found"}), 404

    if request.method == "PUT":
        data = request.get_json()
        options = data.get("options", [])
        
        # Update question fields
        question.title = data.get("title", question.title)
        question.question_text = data.get("text", question.question_text)
        question.correct_option = data.get("correct", question.correct_option)
        
        # Update options only if 4 are provided
        if len(options) == 4:
            question.option_1 = options[0]
            question.option_2 = options[1]
            question.option_3 = options[2]
            question.option_4 = options[3]
        else:
            return jsonify({"error": "Exactly 4 options required"}), 400

        db.session.commit()
        return jsonify({"message": "Question updated"}), 200

    elif request.method == "DELETE":
        db.session.delete(question)
        db.session.commit()
        return jsonify({"message": "Question deleted"}), 200


@admin_bp.route("/dashboard-stats", methods=["GET"])
@admin_required
def get_dashboard_stats():
    # Overall Statistics
    total_students = User.query.filter_by(role='student').count()
    total_quizzes = Quiz.query.count()
    total_questions = Question.query.count()
    
    # Performance Metrics
    avg_scores = db.session.query(
        func.avg(Score.total_scored).label('avg_score'),
        func.avg(Score.total_scored * 100.0 / Score.total_questions).label('avg_percentage')
    ).first()

    # Subject Breakdown
    subject_stats = db.session.query(
        Subject.name,
        func.count(Quiz.id).label('quiz_count'),
        func.avg(Score.total_scored * 100.0 / Score.total_questions).label('avg_score')
    ).join(Chapter, Subject.id == Chapter.subject_id).join(Quiz, Chapter.id == Quiz.chapter_id).join(Score, Quiz.id == Score.quiz_id).group_by(Subject.name).all()

    # Recent Activity
    recent_attempts = Score.query.order_by(Score.timestamp.desc()).limit(10).all()

    return jsonify({
        "overview": {
            "students": total_students,
            "quizzes": total_quizzes,
            "questions": total_questions,
            "avg_score": round(avg_scores.avg_score, 1) if avg_scores.avg_score else 0,
            "avg_percentage": round(avg_scores.avg_percentage, 1) if avg_scores.avg_percentage else 0
        },
        "subjects": [{
            "name": sub[0],
            "quizzes": sub[1],
            "avg_score": round(sub[2], 1) if sub[2] else 0
        } for sub in subject_stats],
        "recent_activity": [{
            "user_id": ra.user_id,
            "quiz_id": ra.quiz_id,
            "score": ra.total_scored,
            "total": ra.total_questions,
            "timestamp": ra.timestamp.isoformat()
        } for ra in recent_attempts]
    })