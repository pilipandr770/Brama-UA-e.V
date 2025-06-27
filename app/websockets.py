from app import socketio, db
from flask_socketio import emit, join_room, leave_room
from flask import request, session
from app.models.user import User
from app.models.meeting import Message, MeetingAttendee, Meeting
from datetime import datetime

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    user_id = session.get('user_id')
    if not user_id:
        return False  # Reject connection if not logged in
    
    user = User.query.get(user_id)
    if not user or not user.is_founder:
        return False  # Reject connection if not a founder

    print(f"Client connected: {user.email}")

@socketio.on('join')
def handle_join(data):
    """Client joining a meeting room"""
    meeting_id = data.get('meeting_id')
    user_id = session.get('user_id')
    
    if not meeting_id or not user_id:
        return
    
    # Create a unique room name for this meeting
    room = f"meeting_{meeting_id}"
    join_room(room)
    
    # Add user to attendees if not already there
    attendee = MeetingAttendee.query.filter_by(meeting_id=meeting_id, user_id=user_id).first()
    if not attendee:
        attendee = MeetingAttendee(
            meeting_id=meeting_id,
            user_id=user_id,
            joined_at=datetime.utcnow()
        )
        db.session.add(attendee)
        db.session.commit()
    
    # Get user info
    user = User.query.get(user_id)
    
    # Notify other clients that user has joined
    emit('user_joined', {
        'user_id': user.id,
        'name': f"{user.first_name} {user.last_name}",
        'time': datetime.utcnow().strftime('%H:%M:%S')
    }, room=room)
    
    print(f"User {user.email} joined meeting room {meeting_id}")

@socketio.on('leave')
def handle_leave(data):
    """Client leaving a meeting room"""
    meeting_id = data.get('meeting_id')
    user_id = session.get('user_id')
    
    if not meeting_id or not user_id:
        return
    
    # Create a unique room name for this meeting
    room = f"meeting_{meeting_id}"
    leave_room(room)
    
    # Update attendee record with leave time
    attendee = MeetingAttendee.query.filter_by(meeting_id=meeting_id, user_id=user_id).first()
    if attendee:
        attendee.left_at = datetime.utcnow()
        db.session.commit()
    
    # Get user info
    user = User.query.get(user_id)
    
    # Notify other clients that user has left
    emit('user_left', {
        'user_id': user.id,
        'name': f"{user.first_name} {user.last_name}",
        'time': datetime.utcnow().strftime('%H:%M:%S')
    }, room=room)
    
    print(f"User {user.email} left meeting room {meeting_id}")

@socketio.on('new_message')
def handle_new_message(data):
    """Handle new message in meeting chat"""
    meeting_id = data.get('meeting_id')
    content = data.get('content')
    user_id = session.get('user_id')
    
    if not meeting_id or not content or not user_id:
        return
    
    # Check if meeting is active
    meeting = Meeting.query.get(meeting_id)
    if not meeting or meeting.status.value != 'active':
        emit('error', {'message': 'Meeting is not active'})
        return
    
    # Save message to database
    message = Message(
        meeting_id=meeting_id,
        user_id=user_id,
        content=content,
        created_at=datetime.utcnow()
    )
    db.session.add(message)
    db.session.commit()
    
    # Get user info
    user = User.query.get(user_id)
    
    # Broadcast message to all clients in the meeting room
    room = f"meeting_{meeting_id}"
    emit('new_message', {
        'id': message.id,
        'content': message.content,
        'user_id': user.id,
        'user_name': f"{user.first_name} {user.last_name}",
        'created_at': message.created_at.strftime('%H:%M:%S')
    }, room=room)
    
    print(f"New message in meeting {meeting_id} from user {user.email}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print("Client disconnected")
    # You might want to update attendee status if they disconnect without leaving properly
