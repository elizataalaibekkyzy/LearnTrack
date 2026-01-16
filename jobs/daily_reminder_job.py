"""
Daily reminder background job.

This job runs daily to:
1. Load all users and their course enrollments
2. Calculate course schedule statuses
3. Identify users who need reminder emails
4. Send reminder emails to users
5. Send summary reports to managers
"""
import json
from datetime import datetime
from typing import List, Dict
from collections import defaultdict

from models import User, CourseEnrollment, CourseSchedule, ScheduleStatus
from services import ScheduleStatusService, EmailService


class DailyReminderJob:
    """
    Background job that processes course reminders daily.
    
    Design Decisions:
    -----------------
    1. Batch Processing: Load all data at once for efficiency
    2. Stateless: Each run is independent, reads fresh data from JSON
    3. Logging: Comprehensive logging for monitoring and debugging
    4. Error Handling: Continue processing other users if one fails
    5. Summary Reports: Aggregate data for manager notifications
    
    Scalability Considerations:
    ---------------------------
    - For large datasets, implement pagination/chunking
    - Use database queries instead of loading all data into memory
    - Consider async processing for email sending
    - Implement retry logic for failed emails
    - Add rate limiting to prevent email service overload
    """
    
    def __init__(
        self,
        users_file: str = "data/users.json",
        enrollments_file: str = "data/course_enrollments.json",
        schedules_file: str = "data/course_schedules.json"
    ):
        """
        Initialize the daily reminder job.
        
        Args:
            users_file: Path to users JSON file
            enrollments_file: Path to enrollments JSON file
            schedules_file: Path to schedules JSON file
        """
        self.users_file = users_file
        self.enrollments_file = enrollments_file
        self.schedules_file = schedules_file
        
        self.users: List[User] = []
        self.enrollments_by_user: Dict[str, List[CourseEnrollment]] = {}
        self.schedules: List[CourseSchedule] = []
        
        self.status_service: ScheduleStatusService = None
        self.email_service = EmailService()
    
    def load_data(self) -> None:
        """Load all necessary data from JSON files."""
        print("Loading data from JSON files...")
        
        # Load users
        with open(self.users_file, 'r') as f:
            users_data = json.load(f)
            self.users = [User.from_dict(u) for u in users_data]
        print(f"Loaded {len(self.users)} users")
        
        # Load course schedules
        with open(self.schedules_file, 'r') as f:
            schedules_data = json.load(f)
            self.schedules = [CourseSchedule.from_dict(s) for s in schedules_data]
        print(f"Loaded {len(self.schedules)} course schedules")
        
        # Load enrollments
        with open(self.enrollments_file, 'r') as f:
            enrollments_data = json.load(f)
            for user_enrollment in enrollments_data:
                user_id = user_enrollment['user_id']
                enrollments = [
                    CourseEnrollment.from_dict(e)
                    for e in user_enrollment['enrollments']
                ]
                self.enrollments_by_user[user_id] = enrollments
        print(f"Loaded enrollments for {len(self.enrollments_by_user)} users")
        
        # Initialize status service
        self.status_service = ScheduleStatusService(self.schedules)
    
    def process_reminders(self, current_date: datetime = None) -> Dict:
        """
        Process reminders for all users.
        
        Args:
            current_date: The date to use for calculations (defaults to now)
        
        Returns:
            Dictionary with job execution statistics
        """
        if current_date is None:
            current_date = datetime.now()
        
        print(f"\n{'='*80}")
        print(f"Running Daily Reminder Job - {current_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        users_needing_reminders = []
        manager_summaries = defaultdict(list)
        
        # Process each user
        for user in self.users:
            enrollments = self.enrollments_by_user.get(user.user_id, [])
            
            if not enrollments:
                print(f"{user.name}: No enrollments found")
                continue
            
            # Calculate statuses
            statuses = self.status_service.calculate_user_status(enrollments, current_date)
            
            # Get courses needing reminders
            needs_reminder = [s for s in statuses if s.status == ScheduleStatus.NEEDS_REMINDER]
            
            if needs_reminder:
                users_needing_reminders.append((user, needs_reminder))
                print(f"{user.name}: {len(needs_reminder)} course(s) need attention")
            else:
                print(f"{user.name}: All courses on track")
            
            # Prepare manager summary
            summary = self.status_service.get_user_summary(enrollments, current_date)
            manager_summaries[user.manager_email].append({
                "user_name": user.name,
                "user_email": user.email,
                "completed_count": summary["completed"],
                "in_progress_count": summary["in_progress"],
                "needs_reminder_count": summary["needs_reminder"],
                "total_courses": summary["total_courses"]
            })
        
        # Send reminder emails
        print(f"\n{'-'*80}")
        print("Sending Reminder Emails...")
        print(f"{'-'*80}\n")
        
        email_stats = {"users_emailed": 0, "managers_emailed": 0}
        
        for user, courses in users_needing_reminders:
            if self.email_service.send_user_reminder(user, courses, ScheduleStatus.NEEDS_REMINDER):
                email_stats["users_emailed"] += 1
        
        # Send manager summaries
        print(f"\n{'-'*80}")
        print("Sending Manager Summaries...")
        print(f"{'-'*80}\n")
        
        for manager_email, summaries in manager_summaries.items():
            if self.email_service.send_manager_summary(manager_email, summaries):
                email_stats["managers_emailed"] += 1
        
        # Save email log
        self.email_service.save_email_log()
        
        # Compile job statistics
        job_stats = {
            "execution_date": current_date.isoformat(),
            "users_processed": len(self.users),
            "users_needing_reminders": len(users_needing_reminders),
            "reminder_emails_sent": email_stats["users_emailed"],
            "manager_summaries_sent": email_stats["managers_emailed"],
            "total_emails_sent": email_stats["users_emailed"] + email_stats["managers_emailed"]
        }
        
        return job_stats
    
    def run(self, current_date: datetime = None) -> Dict:
        """
        Execute the daily reminder job.
        
        Args:
            current_date: The date to use for calculations (defaults to now)
        
        Returns:
            Dictionary with job execution statistics
        """
        try:
            self.load_data()
            stats = self.process_reminders(current_date)
            
            print(f"\n{'='*80}")
            print("Job Execution Summary")
            print(f"{'='*80}")
            print(f"Users Processed: {stats['users_processed']}")
            print(f"Users Needing Reminders: {stats['users_needing_reminders']}")
            print(f"Reminder Emails Sent: {stats['reminder_emails_sent']}")
            print(f"Manager Summaries Sent: {stats['manager_summaries_sent']}")
            print(f"Total Emails Sent: {stats['total_emails_sent']}")
            print(f"{'='*80}\n")
            
            return stats
            
        except Exception as e:
            print(f"❌ Error running daily reminder job: {e}")
            raise


def schedule_job():
    """
    Schedule the job to run daily.
    
    Production Implementation Options:
    -----------------------------------
    1. Cron Job (Linux/Unix):
       - Add to crontab: `0 9 * * * /usr/bin/python3 /path/to/jobs/daily_reminder_job.py`
       - Runs every day at 9 AM
    
    2. Task Scheduler (Windows):
       - Create scheduled task to run Python script daily
    
    3. APScheduler (Python library):
       - Use BackgroundScheduler for in-process scheduling
       - Suitable for web applications
    
    4. Celery (Distributed Task Queue):
       - For high-volume, distributed systems
       - Integrates with message brokers (Redis, RabbitMQ)
    
    5. Cloud Services:
       - AWS Lambda + CloudWatch Events
       - Azure Functions + Timer Trigger
       - Google Cloud Scheduler + Cloud Functions
    
    6. Kubernetes CronJob:
       - For containerized applications
       - Native scheduling in K8s clusters
    
    Example with APScheduler:
    -------------------------
    from apscheduler.schedulers.background import BackgroundScheduler
    
    scheduler = BackgroundScheduler()
    job = DailyReminderJob()
    
    # Run every day at 9:00 AM
    scheduler.add_job(
        func=job.run,
        trigger='cron',
        hour=9,
        minute=0,
        id='daily_reminder_job'
    )
    
    scheduler.start()
    """
    pass


if __name__ == "__main__":
    """Run the job when executed directly."""
    job = DailyReminderJob()
    job.run()
