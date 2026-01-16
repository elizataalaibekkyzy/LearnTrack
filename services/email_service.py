"""
Email notification service for sending course reminders.

This service handles sending emails to users and managers based on
course schedule status.
"""
from typing import List, Dict
from datetime import datetime
import json
from models import User, CourseScheduleStatus, ScheduleStatus
from services.email_templates import EmailTemplateFactory


class EmailService:
    """
    Service for sending email notifications.
    
    In a production environment, this would integrate with an actual email
    service (e.g., SendGrid, AWS SES, SMTP). For this implementation,
    we log the emails to demonstrate the functionality.
    """
    
    def __init__(self, log_file: str = "data/email_log.json"):
        """
        Initialize the email service.
        
        Args:
            log_file: Path to file where emails will be logged
        """
        self.log_file = log_file
        self.sent_emails: List[Dict] = []
    
    def send_user_reminder(
        self,
        user: User,
        courses: List[CourseScheduleStatus],
        status_type: ScheduleStatus
    ) -> bool:
        """
        Send a reminder email to a user based on their course status.
        
        Args:
            user: The user to send email to
            courses: List of course statuses to include in email
            status_type: The type of status determining the template
        
        Returns:
            True if email was sent successfully
        """
        if not courses:
            return False
        
        template = EmailTemplateFactory.get_template(status_type, user)
        subject = template.generate_subject()
        body = template.generate_body(courses)
        
        email_record = {
            "timestamp": datetime.now().isoformat(),
            "to": user.email,
            "from": "noreply@learningplatform.com",
            "subject": subject,
            "body": body,
            "type": "user_reminder",
            "status_type": status_type.value,
            "course_ids": [course.course_id for course in courses]
        }
        
        self._log_email(email_record)
        return True
    
    def send_manager_summary(
        self,
        manager_email: str,
        user_summaries: List[Dict]
    ) -> bool:
        """
        Send a summary email to a manager about their team's progress.
        
        Args:
            manager_email: The manager's email address
            user_summaries: List of user summary dictionaries
        
        Returns:
            True if email was sent successfully
        """
        if not user_summaries:
            return False
        
        template = EmailTemplateFactory.get_manager_template(manager_email)
        subject = template.generate_subject(len(user_summaries))
        body = template.generate_body(user_summaries)
        
        email_record = {
            "timestamp": datetime.now().isoformat(),
            "to": manager_email,
            "from": "noreply@learningplatform.com",
            "subject": subject,
            "body": body,
            "type": "manager_summary",
            "user_count": len(user_summaries)
        }
        
        self._log_email(email_record)
        return True
    
    def send_batch_reminders(
        self,
        users_with_courses: Dict[User, List[CourseScheduleStatus]]
    ) -> Dict[str, int]:
        """
        Send reminder emails to multiple users.
        
        Args:
            users_with_courses: Dictionary mapping users to their course statuses
        
        Returns:
            Dictionary with counts of emails sent by status type
        """
        results = {
            "needs_reminder": 0,
            "progressed": 0,
            "started": 0,
            "completed": 0,
            "total": 0
        }
        
        for user, courses in users_with_courses.items():
            if not courses:
                continue
            
            # Group courses by status
            courses_by_status = {}
            for course in courses:
                status = course.status
                if status not in courses_by_status:
                    courses_by_status[status] = []
                courses_by_status[status].append(course)
            
            # Send emails for each status type
            for status, status_courses in courses_by_status.items():
                if self.send_user_reminder(user, status_courses, status):
                    results[status.value.replace(" ", "_")] += 1
                    results["total"] += 1
        
        return results
    
    def _log_email(self, email_record: Dict) -> None:
        """
        Log an email record (simulates sending).
        
        Args:
            email_record: Dictionary containing email details
        """
        self.sent_emails.append(email_record)
        
        # In production, this would actually send the email
        # For now, we just log it
        print(f"[EMAIL SENT] To: {email_record['to']}")
        print(f"Subject: {email_record['subject']}")
        print("-" * 80)
    
    def save_email_log(self) -> None:
        """Save all sent emails to the log file."""
        try:
            # Load existing logs
            try:
                with open(self.log_file, 'r') as f:
                    existing_logs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                existing_logs = []
            
            # Append new emails
            existing_logs.extend(self.sent_emails)
            
            # Save to file
            with open(self.log_file, 'w') as f:
                json.dump(existing_logs, f, indent=2)
            
            print(f"\nSaved {len(self.sent_emails)} email(s) to {self.log_file}")
        except Exception as e:
            print(f"Error saving email log: {e}")
    
    def get_email_statistics(self) -> Dict[str, int]:
        """
        Get statistics about sent emails.
        
        Returns:
            Dictionary with email statistics
        """
        stats = {
            "total_sent": len(self.sent_emails),
            "user_reminders": 0,
            "manager_summaries": 0
        }
        
        for email in self.sent_emails:
            if email["type"] == "user_reminder":
                stats["user_reminders"] += 1
            elif email["type"] == "manager_summary":
                stats["manager_summaries"] += 1
        
        return stats
