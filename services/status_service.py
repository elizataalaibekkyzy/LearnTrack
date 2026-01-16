"""
Service for calculating course schedule status.

This service implements the core business logic for determining whether a user
is on track with their assigned courses.
"""
from datetime import datetime
from typing import List, Dict, Optional
from models import (
    CourseEnrollment,
    CourseSchedule,
    CourseScheduleStatus,
    EnrollmentStatus,
    ScheduleStatus
)


class ScheduleStatusService:
    """
    Service for calculating course schedule status.
    
    Approach & Assumptions:
    -----------------------
    1. Status Calculation Logic:
       - "completed": Course has completion_date set
       - "started": Course has start_date but not completed, within deadline
       - "progressed": Course status is "In Progress" and within deadline
       - "needs reminder": Course is overdue (past days_to_complete since enrollment)
    
    2. Assumptions:
       - Deadline starts from enrollment_date (could also use hire_date)
       - Batches determine grouping but don't affect individual course deadlines
       - A course is overdue if days_since_enrollment > days_to_complete
       - Users should be reminded if they haven't started or haven't completed within deadline
    
    3. Edge Cases Handled:
       - Enrolled but not started courses
       - Started but not completed courses
       - Courses completed early
       - Missing enrollment data
    """
    
    def __init__(self, schedules: List[CourseSchedule]):
        """
        Initialize the service with course schedules.
        
        Args:
            schedules: List of course schedules defining deadlines
        """
        self.schedules_map: Dict[str, CourseSchedule] = {
            schedule.course_id: schedule for schedule in schedules
        }
    
    def calculate_status(
        self,
        enrollment: CourseEnrollment,
        schedule: CourseSchedule,
        current_date: datetime
    ) -> CourseScheduleStatus:
        """
        Calculate the status for a single course enrollment.
        
        Args:
            enrollment: The user's enrollment record
            schedule: The schedule requirements for the course
            current_date: The current date for calculation
        
        Returns:
            CourseScheduleStatus with calculated status and details
        """
        days_since_enrollment = enrollment.days_since_enrollment(current_date)
        days_overdue = max(0, days_since_enrollment - schedule.days_to_complete)
        
        # Case 1: Course is completed
        if enrollment.is_completed():
            return CourseScheduleStatus(
                course_id=enrollment.course_id,
                status=ScheduleStatus.COMPLETED,
                enrollment=enrollment,
                schedule=schedule,
                days_overdue=0,
                message=f"Completed on {enrollment.completion_date.strftime('%Y-%m-%d')}"
            )
        
        # Case 2: Course is overdue (needs reminder)
        if days_since_enrollment > schedule.days_to_complete:
            status_detail = "Not started" if not enrollment.is_started() else "In progress but overdue"
            return CourseScheduleStatus(
                course_id=enrollment.course_id,
                status=ScheduleStatus.NEEDS_REMINDER,
                enrollment=enrollment,
                schedule=schedule,
                days_overdue=days_overdue,
                message=f"{status_detail} - {days_overdue} days overdue"
            )
        
        # Case 3: Course is in progress and within deadline
        if enrollment.status == EnrollmentStatus.IN_PROGRESS:
            days_remaining = schedule.days_to_complete - days_since_enrollment
            return CourseScheduleStatus(
                course_id=enrollment.course_id,
                status=ScheduleStatus.PROGRESSED,
                enrollment=enrollment,
                schedule=schedule,
                days_overdue=0,
                message=f"In progress - {days_remaining} days remaining"
            )
        
        # Case 4: Course has been started but not marked as "In Progress" yet
        if enrollment.is_started():
            days_remaining = schedule.days_to_complete - days_since_enrollment
            return CourseScheduleStatus(
                course_id=enrollment.course_id,
                status=ScheduleStatus.STARTED,
                enrollment=enrollment,
                schedule=schedule,
                days_overdue=0,
                message=f"Started - {days_remaining} days remaining"
            )
        
        # Case 5: Course is enrolled but not started (within deadline)
        days_remaining = schedule.days_to_complete - days_since_enrollment
        return CourseScheduleStatus(
            course_id=enrollment.course_id,
            status=ScheduleStatus.STARTED,
            enrollment=enrollment,
            schedule=schedule,
            days_overdue=0,
            message=f"Enrolled - {days_remaining} days to start and complete"
        )
    
    def calculate_user_status(
        self,
        enrollments: List[CourseEnrollment],
        current_date: datetime
    ) -> List[CourseScheduleStatus]:
        """
        Calculate status for all of a user's course enrollments.
        
        Args:
            enrollments: List of user's course enrollments
            current_date: The current date for calculation
        
        Returns:
            List of CourseScheduleStatus objects, one per enrollment
        """
        statuses = []
        
        for enrollment in enrollments:
            schedule = self.schedules_map.get(enrollment.course_id)
            
            if not schedule:
                # Course not in schedule - could be optional or error
                continue
            
            status = self.calculate_status(enrollment, schedule, current_date)
            statuses.append(status)
        
        return statuses
    
    def get_courses_needing_reminder(
        self,
        enrollments: List[CourseEnrollment],
        current_date: datetime
    ) -> List[CourseScheduleStatus]:
        """
        Get all courses that need reminder emails.
        
        Args:
            enrollments: List of user's course enrollments
            current_date: The current date for calculation
        
        Returns:
            List of CourseScheduleStatus objects for courses needing reminders
        """
        all_statuses = self.calculate_user_status(enrollments, current_date)
        return [status for status in all_statuses if status.needs_reminder()]
    
    def get_user_summary(
        self,
        enrollments: List[CourseEnrollment],
        current_date: datetime
    ) -> Dict[str, int]:
        """
        Get a summary of user's progress across all courses.
        
        Args:
            enrollments: List of user's course enrollments
            current_date: The current date for calculation
        
        Returns:
            Dictionary with counts for each status type
        """
        all_statuses = self.calculate_user_status(enrollments, current_date)
        
        summary = {
            "total_courses": len(all_statuses),
            "completed": 0,
            "in_progress": 0,
            "needs_reminder": 0,
            "on_track": 0
        }
        
        for status in all_statuses:
            if status.status == ScheduleStatus.COMPLETED:
                summary["completed"] += 1
            elif status.status == ScheduleStatus.NEEDS_REMINDER:
                summary["needs_reminder"] += 1
            elif status.status in [ScheduleStatus.PROGRESSED, ScheduleStatus.STARTED]:
                summary["in_progress"] += 1
                if status.days_overdue == 0:
                    summary["on_track"] += 1
        
        return summary
