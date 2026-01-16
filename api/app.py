"""
Flask REST API for LearnTrack system.

This API serves data to the React frontend.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import User, CourseEnrollment, CourseSchedule
from services import ScheduleStatusService, EmailService

app = Flask(__name__)
# Enable CORS for React frontend with explicit configuration
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Global data stores
users_data = []
enrollments_data = {}
schedules_data = []
status_service = None


def load_data():
    """Load data from JSON files."""
    global users_data, enrollments_data, schedules_data, status_service
    
    # Get the base directory (parent of api directory)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    
    # Load users
    with open(os.path.join(data_dir, 'users.json'), 'r') as f:
        users_json = json.load(f)
        users_data = [User.from_dict(u) for u in users_json]
    
    # Load schedules
    with open(os.path.join(data_dir, 'course_schedules.json'), 'r') as f:
        schedules_json = json.load(f)
        schedules_data = [CourseSchedule.from_dict(s) for s in schedules_json]
    
    # Load enrollments
    with open(os.path.join(data_dir, 'course_enrollments.json'), 'r') as f:
        enrollments_json = json.load(f)
        for user_enrollment in enrollments_json:
            user_id = user_enrollment['user_id']
            enrollments = [
                CourseEnrollment.from_dict(e)
                for e in user_enrollment['enrollments']
            ]
            enrollments_data[user_id] = enrollments
    
    # Initialize status service
    status_service = ScheduleStatusService(schedules_data)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users."""
    users = [
        {
            'user_id': u.user_id,
            'name': u.name,
            'email': u.email,
            'manager_email': u.manager_email,
            'hire_date': u.hire_date.isoformat()
        }
        for u in users_data
    ]
    return jsonify(users)


@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user."""
    user = next((u for u in users_data if u.user_id == user_id), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user_id': user.user_id,
        'name': user.name,
        'email': user.email,
        'manager_email': user.manager_email,
        'hire_date': user.hire_date.isoformat()
    })


@app.route('/api/users/<user_id>/enrollments', methods=['GET'])
def get_user_enrollments(user_id):
    """Get enrollments for a specific user."""
    enrollments = enrollments_data.get(user_id, [])
    
    result = [
        {
            'course_id': e.course_id,
            'status': e.status.value,
            'enrollment_date': e.enrollment_date.isoformat(),
            'start_date': e.start_date.isoformat() if e.start_date else None,
            'completion_date': e.completion_date.isoformat() if e.completion_date else None,
            'days_since_enrollment': e.days_since_enrollment(datetime.now())
        }
        for e in enrollments
    ]
    
    return jsonify(result)


@app.route('/api/users/<user_id>/status', methods=['GET'])
def get_user_status(user_id):
    """Get course status for a specific user."""
    enrollments = enrollments_data.get(user_id, [])
    if not enrollments:
        return jsonify({'error': 'No enrollments found'}), 404
    
    current_date = datetime.now()
    statuses = status_service.calculate_user_status(enrollments, current_date)
    
    result = [
        {
            'course_id': s.course_id,
            'status': s.status.value,
            'days_overdue': s.days_overdue,
            'message': s.message,
            'enrollment': {
                'course_id': s.enrollment.course_id,
                'status': s.enrollment.status.value,
                'enrollment_date': s.enrollment.enrollment_date.isoformat(),
                'start_date': s.enrollment.start_date.isoformat() if s.enrollment.start_date else None,
                'completion_date': s.enrollment.completion_date.isoformat() if s.enrollment.completion_date else None
            } if s.enrollment else None,
            'schedule': {
                'days_to_complete': s.schedule.days_to_complete,
                'batch': s.schedule.batch
            }
        }
        for s in statuses
    ]
    
    return jsonify(result)


@app.route('/api/users/<user_id>/summary', methods=['GET'])
def get_user_summary(user_id):
    """Get summary of user's progress."""
    enrollments = enrollments_data.get(user_id, [])
    if not enrollments:
        return jsonify({'error': 'No enrollments found'}), 404
    
    current_date = datetime.now()
    summary = status_service.get_user_summary(enrollments, current_date)
    
    return jsonify(summary)


@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all course schedules."""
    courses = [
        {
            'course_id': s.course_id,
            'days_to_complete': s.days_to_complete,
            'batch': s.batch
        }
        for s in schedules_data
    ]
    return jsonify(courses)


@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard data for all users."""
    current_date = datetime.now()
    dashboard_data = []
    
    for user in users_data:
        enrollments = enrollments_data.get(user.user_id, [])
        if not enrollments:
            continue
        
        summary = status_service.get_user_summary(enrollments, current_date)
        statuses = status_service.calculate_user_status(enrollments, current_date)
        
        # Get courses needing attention
        needs_attention = [s for s in statuses if s.status.value == 'needs reminder']
        
        dashboard_data.append({
            'user_id': user.user_id,
            'name': user.name,
            'email': user.email,
            'hire_date': user.hire_date.isoformat(),
            'summary': summary,
            'needs_attention_count': len(needs_attention),
            'progress_percentage': (summary['completed'] / summary['total_courses'] * 100) if summary['total_courses'] > 0 else 0
        })
    
    return jsonify(dashboard_data)


@app.route('/api/email-logs', methods=['GET'])
def get_email_logs():
    """Get email logs."""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        email_log_path = os.path.join(base_dir, 'data', 'email_log.json')
        
        with open(email_log_path, 'r') as f:
            logs = json.load(f)
        
        # Add pagination support
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        start = (page - 1) * per_page
        end = start + per_page
        
        return jsonify({
            'logs': logs[start:end],
            'total': len(logs),
            'page': page,
            'per_page': per_page,
            'total_pages': (len(logs) + per_page - 1) // per_page
        })
    except FileNotFoundError:
        return jsonify({'logs': [], 'total': 0, 'page': 1, 'per_page': 10, 'total_pages': 0})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall system statistics."""
    current_date = datetime.now()
    
    total_users = len(users_data)
    total_enrollments = sum(len(enrollments) for enrollments in enrollments_data.values())
    
    # Calculate aggregate stats
    total_completed = 0
    total_needs_reminder = 0
    total_in_progress = 0
    
    for user in users_data:
        enrollments = enrollments_data.get(user.user_id, [])
        if enrollments:
            summary = status_service.get_user_summary(enrollments, current_date)
            total_completed += summary['completed']
            total_needs_reminder += summary['needs_reminder']
            total_in_progress += summary['in_progress']
    
    return jsonify({
        'total_users': total_users,
        'total_enrollments': total_enrollments,
        'total_courses': len(schedules_data),
        'completed_courses': total_completed,
        'courses_needing_attention': total_needs_reminder,
        'courses_in_progress': total_in_progress,
        'completion_rate': (total_completed / total_enrollments * 100) if total_enrollments > 0 else 0
    })


@app.route('/api/run-job', methods=['POST'])
def run_job():
    """Manually trigger the reminder job."""
    try:
        from jobs import DailyReminderJob
        job = DailyReminderJob()
        stats = job.run()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("Loading data...")
    load_data()
    print(f"Loaded {len(users_data)} users, {len(schedules_data)} courses")
    print("\nStarting Flask API server...")
    print("API will be available at: http://localhost:5001")
    print("\nAvailable endpoints:")
    print("  GET  /api/health")
    print("  GET  /api/users")
    print("  GET  /api/users/<user_id>")
    print("  GET  /api/users/<user_id>/enrollments")
    print("  GET  /api/users/<user_id>/status")
    print("  GET  /api/users/<user_id>/summary")
    print("  GET  /api/courses")
    print("  GET  /api/dashboard")
    print("  GET  /api/email-logs")
    print("  GET  /api/stats")
    print("  POST /api/run-job")
    print("\n" + "="*50)
    app.run(debug=True, host='0.0.0.0', port=5001)
