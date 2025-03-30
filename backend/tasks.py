from datetime import datetime, timedelta
from jinja2 import Template
import csv
import os

@celery.task
def send_daily_reminders():
    from app import create_app
    app, _ = create_app()
    with app.app_context():
        from models import User, Quiz, Score
        from extensions import mail
        
        now = datetime.utcnow()
        cutoff_time = now - timedelta(hours=24)
        
        # Get inactive users (no visits in last 24h)
        inactive_users = User.query.filter(
            User.last_visited_at < cutoff_time,
            User.role == 'student'
        ).all()

@celery.task
def generate_monthly_reports():
    from app import create_app
    app, _ = create_app()
    with app.app_context():
        from models import User, Score, Quiz, Chapter
        from extensions import mail
        
        first_day = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
        last_month = first_day - timedelta(days=1)
        
        for user in User.query.filter_by(role='student').all():
            scores = Score.query.filter(
                Score.user_id == user.id,
                Score.timestamp >= last_month.replace(month=last_month.month, day=1),
                Score.timestamp < first_day
            ).join(Quiz).join(Chapter).all()
            
            if scores:
                report_html = render_template('monthly_report.html',
                    user=user,
                    scores=scores,
                    month=last_month.strftime('%B %Y')
                )
                
                msg = Message(
                    f"Monthly Quiz Report - {last_month.strftime('%B %Y')}",
                    recipients=[user.email],
                    html=report_html
                )
                mail.send(msg)

def export_user_csv(user_id):
    from models import Score, Quiz, Chapter
    scores = Score.query.filter_by(user_id=user_id).join(Quiz).join(Chapter).all()
    
    filename = f"quiz_report_{user_id}_{datetime.utcnow().timestamp()}.csv"
    filepath = os.path.join(app.config['TEMP_DIR'], filename)
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Quiz ID', 'Chapter', 'Date', 'Score', 'Total', 'Percentage'])
        for score in scores:
            writer.writerow([
                score.quiz_id,
                score.quiz.chapter.name,
                score.timestamp.date(),
                score.total_scored,
                score.total_questions,
                f"{(score.total_scored/score.total_questions)*100:.2f}%"
            ])
    
    return filepath

@celery.task
def export_csv_task(user_id):
    from app import create_app
    app, _ = create_app()
    with app.app_context():
        from models import User
        from extensions import mail
        
        user = User.query.get(user_id)
        filepath = export_user_csv(user_id)
        
        msg = Message(
            "Your Quiz Export is Ready",
            recipients=[user.email]
        )
        msg.body = "Please find attached your quiz history export."
        with open(filepath, 'rb') as f:
            msg.attach("quiz_history.csv", "text/csv", f.read())
        
        mail.send(msg)
        os.remove(filepath)