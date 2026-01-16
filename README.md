# LearnTrack - Learning & Development Tracking System

A comprehensive Learning & Development tracking system designed. This system helps managers monitor whether new hires are on track with their assigned courses.

## Problem Statement

The system addresses three key requirements:

### Part 1: Status Calculation

Given a user's course enrollments and course schedules, determine the user's course schedule status.

### Part 2: Background Job Design

Design a daily background job that sends reminder emails to users who are falling behind on completing course schedules.

## Status Calculation Logic

### Status Types

- **completed**: Course has a completion date set
- **started**: Course has a start date, not completed, within deadline
- **progressed**: Course status is "In Progress", within deadline
- **needs reminder**: Course is overdue (past days_to_complete since enrollment)

### Calculation Approach

```python
For each enrollment:
1. Calculate days_since_enrollment = current_date - enrollment_date
2. Compare with course_schedule.days_to_complete
3. Check enrollment status (Enrolled, In Progress, Completed)
4. Determine appropriate status:
   - If completed → "completed"
   - If days_since_enrollment > days_to_complete → "needs reminder"
   - If in progress and within deadline → "progressed"
   - If started and within deadline → "started"
```

### Assumptions

- Deadline starts from `enrollment_date`
- Course batches group courses but don't affect individual deadlines
- A course is overdue if `days_since_enrollment > days_to_complete`
- Users should be reminded regardless of whether they started the course

## Background Job Design (Part 2)

### DailyReminderJob

#### Workflow:

```

1. Load Data
   ├── Load users from JSON
   ├── Load course schedules
   └── Load course enrollments

2. Calculate Status
   ├── For each user:
   │ ├── Calculate course statuses
   │ ├── Identify courses needing reminders
   │ └── Aggregate for summary

3. Send Emails
   ├── Send reminder emails to users
   └── Send summary emails to managers

4. Log Results
   ├── Save email audit trail
   └── Generate job statistics

```

```

```
