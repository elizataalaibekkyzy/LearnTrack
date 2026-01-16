"""
Email templates for different course schedule statuses.

This module provides status-specific email templates for notifying users
and managers about course progress.
"""
from models import ScheduleStatus, User, CourseScheduleStatus
from typing import List


class EmailTemplate:
    """Base class for email templates."""
    
    def __init__(self, user: User):
        self.user = user
    
    def generate_subject(self) -> str:
        """Generate email subject line."""
        raise NotImplementedError
    
    def generate_body(self, courses: List[CourseScheduleStatus]) -> str:
        """Generate email body."""
        raise NotImplementedError


class NeedsReminderTemplate(EmailTemplate):
    """Template for users who are falling behind on courses."""
    
    def generate_subject(self) -> str:
        return f"[Action Required] Course Completion Reminder for {self.user.name}"
    
    def generate_body(self, courses: List[CourseScheduleStatus]) -> str:
        course_details = "\n".join([
            f"  • {course.course_id}: {course.message}"
            for course in courses
        ])
        
        return f"""
Hi {self.user.name},

This is a friendly reminder that you have courses that require your attention. 
The following courses are overdue and need to be completed:

{course_details}

Please prioritize completing these courses to stay on track with your learning goals.

If you're experiencing any difficulties, please reach out to your manager or the L&D team.

Best regards,
Learning & Development Team
"""


class ProgressedTemplate(EmailTemplate):
    """Template for users making progress on courses."""
    
    def generate_subject(self) -> str:
        return f"Great Progress on Your Learning Journey, {self.user.name}!"
    
    def generate_body(self, courses: List[CourseScheduleStatus]) -> str:
        course_details = "\n".join([
            f"  • {course.course_id}: {course.message}"
            for course in courses
        ])
        
        return f"""
Hi {self.user.name},

We wanted to acknowledge your excellent progress on your assigned courses!

Current Progress:
{course_details}

Keep up the great work! You're on track to complete your learning goals.

Best regards,
Learning & Development Team
"""


class StartedTemplate(EmailTemplate):
    """Template for users who have started courses."""
    
    def generate_subject(self) -> str:
        return f"Welcome to Your Learning Journey, {self.user.name}!"
    
    def generate_body(self, courses: List[CourseScheduleStatus]) -> str:
        course_details = "\n".join([
            f"  • {course.course_id}: {course.message}"
            for course in courses
        ])
        
        return f"""
Hi {self.user.name},

Welcome! We're excited to see you've started your learning journey.

Your Active Courses:
{course_details}

Remember to complete these courses within the allocated timeframe. If you need any support, 
don't hesitate to reach out.

Best regards,
Learning & Development Team
"""


class CompletedTemplate(EmailTemplate):
    """Template for users who have completed courses."""
    
    def generate_subject(self) -> str:
        return f"Congratulations on Completing Your Courses, {self.user.name}!"
    
    def generate_body(self, courses: List[CourseScheduleStatus]) -> str:
        course_details = "\n".join([
            f"  • {course.course_id}: {course.message}"
            for course in courses
        ])
        
        return f"""
Hi {self.user.name},

Congratulations! You've successfully completed the following courses:

{course_details}

Your dedication to continuous learning is commendable. These accomplishments have been 
recorded and your manager has been notified.

Best regards,
Learning & Development Team
"""


class ManagerSummaryTemplate:
    """Template for manager summary emails."""
    
    def __init__(self, manager_email: str):
        self.manager_email = manager_email
    
    def generate_subject(self, user_count: int) -> str:
        return f"Daily Learning Progress Report - {user_count} Team Members"
    
    def generate_body(self, user_summaries: List[dict]) -> str:
        """
        Generate manager summary email body.
        
        Args:
            user_summaries: List of dicts with user info and course statuses
        """
        summary_lines = []
        
        for summary in user_summaries:
            user_name = summary['user_name']
            needs_attention = summary['needs_reminder_count']
            
            status_emoji = "[NEEDS ATTENTION]" if needs_attention > 0 else "[COMPLETED]"
            summary_lines.append(
                f"{status_emoji} {user_name}: "
                f"{summary['completed_count']} completed, "
                f"{summary['in_progress_count']} in progress, "
                f"{needs_attention} needs attention"
            )
        
        summary_text = "\n".join(summary_lines)
        
        return f"""
Hello,

Here's your daily learning progress report for your team:

{summary_text}

Team members with courses needing attention have been sent reminder emails.

For detailed progress information, please check the learning management dashboard.

Best regards,
Learning & Development Team
"""


class EmailTemplateFactory:
    """Factory for creating appropriate email templates based on status."""
    
    @staticmethod
    def get_template(status: ScheduleStatus, user: User) -> EmailTemplate:
        """
        Get the appropriate email template for a given status.
        
        Args:
            status: The course schedule status
            user: The user to send the email to
        
        Returns:
            Appropriate EmailTemplate instance
        """
        template_map = {
            ScheduleStatus.NEEDS_REMINDER: NeedsReminderTemplate,
            ScheduleStatus.PROGRESSED: ProgressedTemplate,
            ScheduleStatus.STARTED: StartedTemplate,
            ScheduleStatus.COMPLETED: CompletedTemplate
        }
        
        template_class = template_map.get(status, NeedsReminderTemplate)
        return template_class(user)
    
    @staticmethod
    def get_manager_template(manager_email: str) -> ManagerSummaryTemplate:
        """Get manager summary email template."""
        return ManagerSummaryTemplate(manager_email)
