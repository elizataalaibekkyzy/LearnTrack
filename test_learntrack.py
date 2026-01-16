"""
Example tests for the LearnTrack system.

This file demonstrates how the system would be tested in production.
To run these tests, you would need pytest installed:
    pip install pytest pytest-cov

Then run:
    pytest test_learntrack.py -v
    pytest test_learntrack.py --cov=. --cov-report=html
"""

from datetime import datetime
from models import (
    User, CourseEnrollment, CourseSchedule, 
    EnrollmentStatus, ScheduleStatus
)
from services import ScheduleStatusService, EmailTemplateFactory


class TestCourseModels:
    """Test the data models."""
    
    def test_enrollment_is_completed(self):
        """Test enrollment completion check."""
        enrollment = CourseEnrollment(
            course_id="COURSE_001",
            status=EnrollmentStatus.COMPLETED,
            enrollment_date=datetime(2025, 1, 1),
            start_date=datetime(2025, 1, 1),
            completion_date=datetime(2025, 1, 3)
        )
        assert enrollment.is_completed() is True
    
    def test_enrollment_days_since_enrollment(self):
        """Test days calculation."""
        enrollment = CourseEnrollment(
            course_id="COURSE_001",
            status=EnrollmentStatus.IN_PROGRESS,
            enrollment_date=datetime(2025, 1, 1),
            start_date=datetime(2025, 1, 1)
        )
        current_date = datetime(2025, 1, 5)
        assert enrollment.days_since_enrollment(current_date) == 4
    
    def test_enrollment_from_dict(self):
        """Test creating enrollment from dictionary."""
        data = {
            'course_id': 'COURSE_001',
            'status': 'Completed',
            'enrollment_date': '2025-01-01T08:00:00',
            'start_date': '2025-01-01T09:00:00',
            'completion_date': '2025-01-01T10:54:00'
        }
        enrollment = CourseEnrollment.from_dict(data)
        assert enrollment.course_id == 'COURSE_001'
        assert enrollment.is_completed() is True


class TestStatusCalculation:
    """Test the status calculation logic (Part 1)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.schedules = [
            CourseSchedule(course_id="COURSE_001", days_to_complete=2, batch=0),
            CourseSchedule(course_id="COURSE_002", days_to_complete=2, batch=1),
        ]
        self.service = ScheduleStatusService(self.schedules)
    
    def test_completed_course(self):
        """Test status for completed course."""
        enrollment = CourseEnrollment(
            course_id="COURSE_001",
            status=EnrollmentStatus.COMPLETED,
            enrollment_date=datetime(2025, 1, 1, 8, 0),
            start_date=datetime(2025, 1, 1, 9, 0),
            completion_date=datetime(2025, 1, 1, 10, 54)
        )
        schedule = self.schedules[0]
        current_date = datetime(2025, 1, 15)
        
        status = self.service.calculate_status(enrollment, schedule, current_date)
        
        assert status.status == ScheduleStatus.COMPLETED
        assert status.days_overdue == 0
        assert "Completed on" in status.message
    
    def test_overdue_not_started(self):
        """Test status for overdue course that hasn't been started."""
        enrollment = CourseEnrollment(
            course_id="COURSE_002",
            status=EnrollmentStatus.ENROLLED,
            enrollment_date=datetime(2025, 1, 1, 10, 54),
            start_date=None,
            completion_date=None
        )
        schedule = self.schedules[1]
        current_date = datetime(2025, 1, 15)  # 14 days after enrollment
        
        status = self.service.calculate_status(enrollment, schedule, current_date)
        
        assert status.status == ScheduleStatus.NEEDS_REMINDER
        assert status.days_overdue == 12  # 14 - 2 = 12
        assert "Not started" in status.message
        assert "overdue" in status.message
    
    def test_in_progress_within_deadline(self):
        """Test status for course in progress and on track."""
        enrollment = CourseEnrollment(
            course_id="COURSE_001",
            status=EnrollmentStatus.IN_PROGRESS,
            enrollment_date=datetime(2025, 1, 14, 10, 54),
            start_date=datetime(2025, 1, 14, 14, 15),
            completion_date=None
        )
        schedule = self.schedules[0]
        current_date = datetime(2025, 1, 15)  # 1 day after enrollment
        
        status = self.service.calculate_status(enrollment, schedule, current_date)
        
        assert status.status == ScheduleStatus.PROGRESSED
        assert status.days_overdue == 0
        assert "In progress" in status.message
        assert "remaining" in status.message
    
    def test_in_progress_but_overdue(self):
        """Test status for course in progress but past deadline."""
        enrollment = CourseEnrollment(
            course_id="COURSE_001",
            status=EnrollmentStatus.IN_PROGRESS,
            enrollment_date=datetime(2025, 1, 1),
            start_date=datetime(2025, 1, 1),
            completion_date=None
        )
        schedule = self.schedules[0]
        current_date = datetime(2025, 1, 15)  # 14 days after enrollment
        
        status = self.service.calculate_status(enrollment, schedule, current_date)
        
        assert status.status == ScheduleStatus.NEEDS_REMINDER
        assert status.days_overdue == 12
        assert "overdue" in status.message
    
    def test_started_within_deadline(self):
        """Test status for course that's been started but not in progress."""
        enrollment = CourseEnrollment(
            course_id="COURSE_001",
            status=EnrollmentStatus.ENROLLED,
            enrollment_date=datetime(2025, 1, 14),
            start_date=datetime(2025, 1, 14),
            completion_date=None
        )
        schedule = self.schedules[0]
        current_date = datetime(2025, 1, 15)
        
        status = self.service.calculate_status(enrollment, schedule, current_date)
        
        assert status.status == ScheduleStatus.STARTED
        assert status.days_overdue == 0
    
    def test_get_courses_needing_reminder(self):
        """Test filtering for courses needing reminders."""
        enrollments = [
            CourseEnrollment(
                course_id="COURSE_001",
                status=EnrollmentStatus.COMPLETED,
                enrollment_date=datetime(2025, 1, 1),
                start_date=datetime(2025, 1, 1),
                completion_date=datetime(2025, 1, 2)
            ),
            CourseEnrollment(
                course_id="COURSE_002",
                status=EnrollmentStatus.ENROLLED,
                enrollment_date=datetime(2025, 1, 1),
                start_date=None,
                completion_date=None
            ),
        ]
        current_date = datetime(2025, 1, 15)
        
        reminders = self.service.get_courses_needing_reminder(enrollments, current_date)
        
        assert len(reminders) == 1
        assert reminders[0].course_id == "COURSE_002"
        assert reminders[0].status == ScheduleStatus.NEEDS_REMINDER
    
    def test_get_user_summary(self):
        """Test user summary generation."""
        enrollments = [
            CourseEnrollment(
                course_id="COURSE_001",
                status=EnrollmentStatus.COMPLETED,
                enrollment_date=datetime(2025, 1, 1),
                start_date=datetime(2025, 1, 1),
                completion_date=datetime(2025, 1, 2)
            ),
            CourseEnrollment(
                course_id="COURSE_002",
                status=EnrollmentStatus.ENROLLED,
                enrollment_date=datetime(2025, 1, 1),
                start_date=None,
                completion_date=None
            ),
        ]
        current_date = datetime(2025, 1, 15)
        
        summary = self.service.get_user_summary(enrollments, current_date)
        
        assert summary['total_courses'] == 2
        assert summary['completed'] == 1
        assert summary['needs_reminder'] == 1


class TestEmailTemplates:
    """Test the email template system (Part 3)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.user = User(
            user_id="user_001",
            name="John Doe",
            email="john.doe@company.com",
            manager_email="manager@company.com",
            hire_date=datetime(2025, 1, 1)
        )
    
    def test_needs_reminder_template(self):
        """Test needs reminder email template."""
        template = EmailTemplateFactory.get_template(
            ScheduleStatus.NEEDS_REMINDER,
            self.user
        )
        
        subject = template.generate_subject()
        assert "Action Required" in subject
        assert self.user.name in subject
        
        # Create mock courses
        from models import CourseScheduleStatus
        courses = [
            CourseScheduleStatus(
                course_id="COURSE_001",
                status=ScheduleStatus.NEEDS_REMINDER,
                enrollment=None,
                schedule=CourseSchedule("COURSE_001", 2, 0),
                days_overdue=5,
                message="Not started - 5 days overdue"
            )
        ]
        
        body = template.generate_body(courses)
        assert self.user.name in body
        assert "COURSE_001" in body
        assert "overdue" in body.lower()
    
    def test_progressed_template(self):
        """Test progressed email template."""
        template = EmailTemplateFactory.get_template(
            ScheduleStatus.PROGRESSED,
            self.user
        )
        
        subject = template.generate_subject()
        assert "Progress" in subject or "progress" in subject.lower()
    
    def test_started_template(self):
        """Test started email template."""
        template = EmailTemplateFactory.get_template(
            ScheduleStatus.STARTED,
            self.user
        )
        
        subject = template.generate_subject()
        assert "Welcome" in subject or "Journey" in subject
    
    def test_completed_template(self):
        """Test completed email template."""
        template = EmailTemplateFactory.get_template(
            ScheduleStatus.COMPLETED,
            self.user
        )
        
        subject = template.generate_subject()
        assert "Congratulations" in subject or "Completed" in subject
    
    def test_manager_summary_template(self):
        """Test manager summary template."""
        from services.email_templates import ManagerSummaryTemplate
        
        template = ManagerSummaryTemplate("manager@company.com")
        subject = template.generate_subject(user_count=5)
        assert "5 Team Members" in subject
        
        summaries = [
            {
                "user_name": "John Doe",
                "completed_count": 2,
                "in_progress_count": 1,
                "needs_reminder_count": 0
            },
            {
                "user_name": "Jane Smith",
                "completed_count": 1,
                "in_progress_count": 0,
                "needs_reminder_count": 2
            }
        ]
        
        body = template.generate_body(summaries)
        assert "John Doe" in body
        assert "Jane Smith" in body
        assert "[NEEDS ATTENTION]" in body or "needs attention" in body.lower()


class TestEmailService:
    """Test the email service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        from services import EmailService
        import tempfile
        
        # Create temporary log file
        self.temp_log = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_log.close()
        
        self.service = EmailService(log_file=self.temp_log.name)
        self.user = User(
            user_id="user_001",
            name="Test User",
            email="test@example.com",
            manager_email="manager@example.com",
            hire_date=datetime(2025, 1, 1)
        )
    
    def test_send_user_reminder(self):
        """Test sending user reminder email."""
        from models import CourseScheduleStatus
        
        courses = [
            CourseScheduleStatus(
                course_id="COURSE_001",
                status=ScheduleStatus.NEEDS_REMINDER,
                enrollment=None,
                schedule=CourseSchedule("COURSE_001", 2, 0),
                days_overdue=5,
                message="Not started - 5 days overdue"
            )
        ]
        
        result = self.service.send_user_reminder(
            self.user,
            courses,
            ScheduleStatus.NEEDS_REMINDER
        )
        
        assert result is True
        assert len(self.service.sent_emails) == 1
        
        email = self.service.sent_emails[0]
        assert email['to'] == self.user.email
        assert email['type'] == 'user_reminder'
        assert 'COURSE_001' in email['course_ids']
    
    def test_send_manager_summary(self):
        """Test sending manager summary email."""
        summaries = [
            {
                "user_name": "Test User",
                "user_email": "test@example.com",
                "completed_count": 1,
                "in_progress_count": 0,
                "needs_reminder_count": 1,
                "total_courses": 2
            }
        ]
        
        result = self.service.send_manager_summary(
            "manager@example.com",
            summaries
        )
        
        assert result is True
        assert len(self.service.sent_emails) == 1
        
        email = self.service.sent_emails[0]
        assert email['to'] == "manager@example.com"
        assert email['type'] == 'manager_summary'
    
    def test_get_email_statistics(self):
        """Test email statistics generation."""
        # Send some test emails
        from models import CourseScheduleStatus
        
        courses = [
            CourseScheduleStatus(
                course_id="COURSE_001",
                status=ScheduleStatus.NEEDS_REMINDER,
                enrollment=None,
                schedule=CourseSchedule("COURSE_001", 2, 0),
                days_overdue=5,
                message="Test"
            )
        ]
        
        self.service.send_user_reminder(self.user, courses, ScheduleStatus.NEEDS_REMINDER)
        self.service.send_manager_summary("manager@example.com", [{"user_name": "Test"}])
        
        stats = self.service.get_email_statistics()
        
        assert stats['total_sent'] == 2
        assert stats['user_reminders'] == 1
        assert stats['manager_summaries'] == 1


class TestBackgroundJob:
    """Test the background job (Part 2)."""
    
    def test_job_initialization(self):
        """Test job can be initialized."""
        from jobs import DailyReminderJob
        
        job = DailyReminderJob()
        assert job is not None
        assert job.users == []
        assert job.schedules == []
    
    def test_load_data(self):
        """Test data loading."""
        from jobs import DailyReminderJob
        
        job = DailyReminderJob()
        job.load_data()
        
        assert len(job.users) > 0
        assert len(job.schedules) > 0
        assert len(job.enrollments_by_user) > 0
        assert job.status_service is not None


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_enrollment_on_deadline_day(self):
        """Test course enrolled exactly on the deadline."""
        schedules = [
            CourseSchedule(course_id="COURSE_001", days_to_complete=2, batch=0)
        ]
        service = ScheduleStatusService(schedules)
        
        enrollment = CourseEnrollment(
            course_id="COURSE_001",
            status=EnrollmentStatus.IN_PROGRESS,
            enrollment_date=datetime(2025, 1, 1),
            start_date=datetime(2025, 1, 1),
            completion_date=None
        )
        
        # Exactly 2 days later (deadline day)
        current_date = datetime(2025, 1, 3)
        status = service.calculate_status(enrollment, schedules[0], current_date)
        
        # Should not be overdue yet (2 days since enrollment, 2 days to complete)
        assert status.status == ScheduleStatus.PROGRESSED
    
    def test_enrollment_one_day_past_deadline(self):
        """Test course one day past deadline."""
        schedules = [
            CourseSchedule(course_id="COURSE_001", days_to_complete=2, batch=0)
        ]
        service = ScheduleStatusService(schedules)
        
        enrollment = CourseEnrollment(
            course_id="COURSE_001",
            status=EnrollmentStatus.IN_PROGRESS,
            enrollment_date=datetime(2025, 1, 1),
            start_date=datetime(2025, 1, 1),
            completion_date=None
        )
        
        # 3 days later (1 day overdue)
        current_date = datetime(2025, 1, 4)
        status = service.calculate_status(enrollment, schedules[0], current_date)
        
        assert status.status == ScheduleStatus.NEEDS_REMINDER
        assert status.days_overdue == 1
    
    def test_empty_enrollments(self):
        """Test handling of empty enrollments list."""
        schedules = [
            CourseSchedule(course_id="COURSE_001", days_to_complete=2, batch=0)
        ]
        service = ScheduleStatusService(schedules)
        
        statuses = service.calculate_user_status([], datetime.now())
        assert statuses == []
    
    def test_enrollment_without_schedule(self):
        """Test enrollment for course not in schedule."""
        schedules = [
            CourseSchedule(course_id="COURSE_001", days_to_complete=2, batch=0)
        ]
        service = ScheduleStatusService(schedules)
        
        enrollment = CourseEnrollment(
            course_id="COURSE_999",  # Not in schedules
            status=EnrollmentStatus.ENROLLED,
            enrollment_date=datetime(2025, 1, 1),
            start_date=None,
            completion_date=None
        )
        
        statuses = service.calculate_user_status([enrollment], datetime.now())
        assert len(statuses) == 0  # Should skip courses without schedules


# Integration Tests
class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_complete_workflow(self):
        """Test the complete workflow from enrollment to email."""
        # 1. Set up data
        schedules = [
            CourseSchedule(course_id="COURSE_001", days_to_complete=2, batch=0)
        ]
        
        enrollments = [
            CourseEnrollment(
                course_id="COURSE_001",
                status=EnrollmentStatus.ENROLLED,
                enrollment_date=datetime(2025, 1, 1),
                start_date=None,
                completion_date=None
            )
        ]
        
        user = User(
            user_id="user_001",
            name="Test User",
            email="test@example.com",
            manager_email="manager@example.com",
            hire_date=datetime(2025, 1, 1)
        )
        
        # 2. Calculate status
        status_service = ScheduleStatusService(schedules)
        current_date = datetime(2025, 1, 15)  # 14 days later, overdue
        statuses = status_service.calculate_user_status(enrollments, current_date)
        
        assert len(statuses) == 1
        assert statuses[0].status == ScheduleStatus.NEEDS_REMINDER
        
        # 3. Get courses needing reminders
        reminders = status_service.get_courses_needing_reminder(enrollments, current_date)
        assert len(reminders) == 1
        
        # 4. Send email
        from services import EmailService
        import tempfile
        
        temp_log = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_log.close()
        
        email_service = EmailService(log_file=temp_log.name)
        result = email_service.send_user_reminder(
            user,
            reminders,
            ScheduleStatus.NEEDS_REMINDER
        )
        
        assert result is True
        assert len(email_service.sent_emails) == 1


if __name__ == "__main__":
    print("This file contains example tests.")
    print("To run tests, install pytest and execute:")
    print("  pip install pytest pytest-cov")
    print("  pytest test_learntrack.py -v")
    print("\nNote: Some tests require the data files to exist.")
