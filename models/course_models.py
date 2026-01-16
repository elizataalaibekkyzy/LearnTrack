"""
Data models for the Learning & Development tracking system.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class EnrollmentStatus(Enum):
    """Enrollment status for a course."""
    ENROLLED = "Enrolled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class ScheduleStatus(Enum):
    """Schedule status for a course."""
    STARTED = "started"
    NEEDS_REMINDER = "needs reminder"
    PROGRESSED = "progressed"
    COMPLETED = "completed"


@dataclass
class CourseEnrollment:
    """
    Represents a user's enrollment in a course.
    
    Attributes:
        course_id: Unique identifier for the course
        status: Current status of the enrollment
        enrollment_date: When the user was enrolled
        start_date: When the user started the course (None if not started)
        completion_date: When the user completed the course (None if not completed)
    """
    course_id: str
    status: EnrollmentStatus
    enrollment_date: datetime
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CourseEnrollment':
        """Create a CourseEnrollment from a dictionary."""
        return cls(
            course_id=data['course_id'],
            status=EnrollmentStatus(data['status']),
            enrollment_date=datetime.fromisoformat(data['enrollment_date']),
            start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
            completion_date=datetime.fromisoformat(data['completion_date']) if data.get('completion_date') else None
        )
    
    def is_completed(self) -> bool:
        """Check if the course is completed."""
        return self.status == EnrollmentStatus.COMPLETED
    
    def is_started(self) -> bool:
        """Check if the course has been started."""
        return self.start_date is not None
    
    def days_since_enrollment(self, current_date: datetime) -> int:
        """Calculate days since enrollment."""
        return (current_date - self.enrollment_date).days
    
    def days_since_start(self, current_date: datetime) -> int:
        """Calculate days since the course was started."""
        if not self.start_date:
            return 0
        return (current_date - self.start_date).days


@dataclass
class CourseSchedule:
    """
    Represents the schedule requirements for a course.
    
    Attributes:
        course_id: Unique identifier for the course
        days_to_complete: Number of days allocated to complete the course
        batch: The batch number this course belongs to (for grouping courses)
    """
    course_id: str
    days_to_complete: int
    batch: int
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CourseSchedule':
        """Create a CourseSchedule from a dictionary."""
        return cls(
            course_id=data['course_id'],
            days_to_complete=data['days_to_complete'],
            batch=data['batch']
        )


@dataclass
class CourseScheduleStatus:
    """
    Represents the calculated status of a user's progress on a course schedule.
    
    Attributes:
        course_id: Unique identifier for the course
        status: The calculated status (started, needs reminder, progressed, completed)
        enrollment: The enrollment record
        schedule: The schedule requirements
        days_overdue: Number of days overdue (0 if on time)
        message: Human-readable status message
    """
    course_id: str
    status: ScheduleStatus
    enrollment: Optional[CourseEnrollment]
    schedule: CourseSchedule
    days_overdue: int = 0
    message: str = ""
    
    def needs_reminder(self) -> bool:
        """Check if this course schedule needs a reminder email."""
        return self.status == ScheduleStatus.NEEDS_REMINDER


@dataclass
class User:
    """
    Represents a user in the system.
    
    Attributes:
        user_id: Unique identifier for the user
        name: User's full name
        email: User's email address
        manager_email: Manager's email address
        hire_date: Date the user was hired
    """
    user_id: str
    name: str
    email: str
    manager_email: str
    hire_date: datetime
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create a User from a dictionary."""
        return cls(
            user_id=data['user_id'],
            name=data['name'],
            email=data['email'],
            manager_email=data['manager_email'],
            hire_date=datetime.fromisoformat(data['hire_date'])
        )
