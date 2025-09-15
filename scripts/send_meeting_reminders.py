"""
Script for sending meeting reminders to founders
Run with a scheduler (like cron) once a day
"""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the parent directory to the path so we can import our application modules
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from app import create_app, db
from app.models.meeting import Meeting, MeetingStatus
from app.models.user import User, UserRole
from flask_mail import Mail, Message

def send_meeting_reminders():
    """Send reminders for upcoming meetings"""
    app = create_app()
    
    with app.app_context():
        # Find meetings that are in the next 48 hours and haven't had reminders sent yet
        now = datetime.utcnow()
        reminder_window = now + timedelta(hours=48)  # Two days ahead
        
        upcoming_meetings = Meeting.query.filter(
            Meeting.status == MeetingStatus.planned,
            Meeting.date > now,
            Meeting.date <= reminder_window,
            Meeting.reminder_sent == False  # Only those that haven't had reminders
        ).all()
        
        if not upcoming_meetings:
            print("No upcoming meetings that need reminders")
            return
        
        # Get all founders - use string value since role is stored as string in DB
        founders = User.query.filter_by(role='founder').all()
        if not founders:
            print("No founders found to send reminders to")
            return
        
        # Setup Flask-Mail
        mail = Mail(app)
        
        # Send reminders for each upcoming meeting
        for meeting in upcoming_meetings:
            print(f"Sending reminders for meeting: {meeting.title} on {meeting.date}")
            
            # Prepare email
            subject = f"Reminder: Upcoming Meeting - {meeting.title}"
            
            # Format meeting date in the user's timezone (UTC by default)
            meeting_date = meeting.date.strftime('%A, %B %d at %H:%M UTC')
            
            # Create message body
            html_body = f"""
            <h2>Reminder: Upcoming Meeting</h2>
            <p>This is a reminder about an upcoming founders' meeting:</p>
            <p><strong>Title:</strong> {meeting.title}</p>
            <p><strong>Date:</strong> {meeting_date}</p>
            <p><strong>Description:</strong> {meeting.description}</p>
            <p>You can view the full meeting details and agenda at:</p>
            <p><a href="{app.config['BASE_URL']}/meetings/{meeting.id}">View Meeting Details</a></p>
            <p>Please confirm your attendance if you haven't already done so.</p>
            <p>Thank you,<br>Brama-UA e.V.</p>
            """
            
            text_body = f"""
            Reminder: Upcoming Meeting
            
            This is a reminder about an upcoming founders' meeting:
            Title: {meeting.title}
            Date: {meeting_date}
            
            Description: {meeting.description}
            
            You can view the full meeting details and agenda at: {app.config['BASE_URL']}/meetings/{meeting.id}
            
            Please confirm your attendance if you haven't already done so.
            
            Thank you,
            Brama-UA e.V.
            """
            
            # Send to each founder
            for founder in founders:
                try:
                    msg = Message(
                        subject,
                        recipients=[founder.email],
                        body=text_body,
                        html=html_body,
                        sender=app.config.get('MAIL_DEFAULT_SENDER', 'noreply@brama-ua.org')
                    )
                    mail.send(msg)
                    print(f"  Reminder email sent to {founder.email}")
                except Exception as e:
                    print(f"  Error sending email to {founder.email}: {str(e)}")
            
            # Mark reminder as sent
            meeting.reminder_sent = True
            db.session.commit()
            print(f"  Meeting {meeting.id} marked as reminded")

if __name__ == "__main__":
    send_meeting_reminders()
