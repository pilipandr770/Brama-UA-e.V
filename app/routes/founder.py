from flask import Blueprint, render_template, redirect, url_for, session, flash, request, jsonify
from app import db
from app.models.user import User, UserRole
from app.models.meeting import Meeting, AgendaItem, MeetingAttendee, MeetingVote, Message, MeetingStatus, VoteType
from functools import wraps
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid
from fpdf import FPDF

founder_bp = Blueprint('founder', __name__, url_prefix='/founder')

def founder_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        user = User.query.get(user_id) if user_id else None
        if not user or not user.is_founder:
            flash('Доступ лише для засновників!', 'danger')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@founder_bp.route('/')
@founder_required
def dashboard():
    """Founder dashboard showing all meetings"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    # Get all meetings
    upcoming_meetings = Meeting.query.filter(Meeting.status == MeetingStatus.planned.value).order_by(Meeting.date.asc()).all()
    active_meetings = Meeting.query.filter(Meeting.status == MeetingStatus.active.value).order_by(Meeting.date.asc()).all()
    past_meetings = Meeting.query.filter(Meeting.status == MeetingStatus.completed.value).order_by(Meeting.date.desc()).all()
    
    founders = User.query.filter_by(role=UserRole.founder.value).all()
    
    return render_template(
        'founder/dashboard.html',
        user=user,
        upcoming_meetings=upcoming_meetings,
        active_meetings=active_meetings, 
        past_meetings=past_meetings,
        founders=founders
    )

@founder_bp.route('/meetings/create', methods=['GET', 'POST'])
@founder_required
def create_meeting():
    """Create a new meeting"""
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        meeting_date_str = request.form.get('date')
        meeting_date = datetime.strptime(meeting_date_str, '%Y-%m-%dT%H:%M')
        
        meeting = Meeting(
            title=title,
            description=description,
            date=meeting_date,
            creator_id=user_id,
            status=MeetingStatus.planned.value
        )
        
        db.session.add(meeting)
        db.session.commit()
        
        # Add agenda items if provided
        agenda_items = request.form.getlist('agenda_item_title')
        agenda_descriptions = request.form.getlist('agenda_item_description')
        agenda_voting = request.form.getlist('agenda_item_requires_voting')
        
        for i, title in enumerate(agenda_items):
            if title.strip():
                item = AgendaItem(
                    meeting_id=meeting.id,
                    title=title,
                    description=agenda_descriptions[i] if i < len(agenda_descriptions) else "",
                    order=i,
                    requires_voting=(i < len(agenda_voting) and agenda_voting[i] == 'on')
                )
                db.session.add(item)
        
        db.session.commit()
        flash('Зустріч успішно створена!', 'success')
        return redirect(url_for('founder.dashboard'))
        
    return render_template('founder/create_meeting.html')

@founder_bp.route('/meetings/<int:meeting_id>')
@founder_required
def view_meeting(meeting_id):
    """View meeting details"""
    meeting = Meeting.query.get_or_404(meeting_id)
    agenda_items = meeting.agenda_items.order_by(AgendaItem.order).all()
    attendees = MeetingAttendee.query.filter_by(meeting_id=meeting_id).all()
    user_ids = [attendee.user_id for attendee in attendees]
    users = User.query.filter(User.id.in_(user_ids)).all()
    
    current_user_id = session.get('user_id')
    is_attending = any(attendee.user_id == current_user_id for attendee in attendees)
    
    messages = Message.query.filter_by(meeting_id=meeting_id).order_by(Message.created_at).all()
    
    return render_template(
        'founder/view_meeting.html',
        meeting=meeting,
        agenda_items=agenda_items,
        attendees=attendees,
        users=users,
        is_attending=is_attending,
        messages=messages
    )

@founder_bp.route('/meetings/<int:meeting_id>/edit', methods=['GET', 'POST'])
@founder_required
def edit_meeting(meeting_id):
    """Edit meeting details"""
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if meeting.status != MeetingStatus.planned.value:
        flash('Можна редагувати лише заплановані зустрічі!', 'danger')
        return redirect(url_for('founder.view_meeting', meeting_id=meeting_id))
    
    if request.method == 'POST':
        meeting.title = request.form.get('title')
        meeting.description = request.form.get('description')
        meeting_date_str = request.form.get('date')
        meeting.date = datetime.strptime(meeting_date_str, '%Y-%m-%dT%H:%M')
        
        # Handle agenda items
        # Delete existing items if requested
        deleted_items = request.form.getlist('delete_agenda_item')
        for item_id in deleted_items:
            if item_id:
                item = AgendaItem.query.get(int(item_id))
                if item and item.meeting_id == meeting.id:
                    db.session.delete(item)
        
        # Update existing items
        for item in meeting.agenda_items:
            item_prefix = f"agenda_item_{item.id}_"
            if f"{item_prefix}title" in request.form:
                item.title = request.form.get(f"{item_prefix}title")
                item.description = request.form.get(f"{item_prefix}description", "")
                item.requires_voting = request.form.get(f"{item_prefix}requires_voting") == 'on'
                item.order = request.form.get(f"{item_prefix}order", 0)
        
        # Add new items
        new_titles = request.form.getlist('new_agenda_item_title')
        new_descriptions = request.form.getlist('new_agenda_item_description')
        new_voting = request.form.getlist('new_agenda_item_requires_voting')
        
        for i, title in enumerate(new_titles):
            if title.strip():
                order = meeting.agenda_items.count() + i
                item = AgendaItem(
                    meeting_id=meeting.id,
                    title=title,
                    description=new_descriptions[i] if i < len(new_descriptions) else "",
                    order=order,
                    requires_voting=(i < len(new_voting) and new_voting[i] == 'on')
                )
                db.session.add(item)
        
        db.session.commit()
        flash('Зустріч успішно оновлена!', 'success')
        return redirect(url_for('founder.view_meeting', meeting_id=meeting_id))
    
    agenda_items = meeting.agenda_items.order_by(AgendaItem.order).all()
    return render_template('founder/edit_meeting.html', meeting=meeting, agenda_items=agenda_items)

@founder_bp.route('/meetings/<int:meeting_id>/delete', methods=['POST'])
@founder_required
def delete_meeting(meeting_id):
    """Delete a meeting"""
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if meeting.status != MeetingStatus.planned.value:
        flash('Можна видаляти лише заплановані зустрічі!', 'danger')
        return redirect(url_for('founder.view_meeting', meeting_id=meeting_id))
    
    db.session.delete(meeting)
    db.session.commit()
    
    flash('Зустріч успішно видалена!', 'success')
    return redirect(url_for('founder.dashboard'))

@founder_bp.route('/meetings/<int:meeting_id>/start', methods=['POST'])
@founder_required
def start_meeting(meeting_id):
    """Start a meeting"""
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if meeting.status != MeetingStatus.planned.value:
        flash('Можна розпочати лише заплановану зустріч!', 'danger')
        return redirect(url_for('founder.view_meeting', meeting_id=meeting_id))
    
    meeting.status = MeetingStatus.active.value
    
    # Add current user as attendee
    current_user_id = session.get('user_id')
    attendee = MeetingAttendee.query.filter_by(meeting_id=meeting_id, user_id=current_user_id).first()
    if not attendee:
        attendee = MeetingAttendee(
            meeting_id=meeting_id,
            user_id=current_user_id,
            joined_at=datetime.utcnow()
        )
        db.session.add(attendee)
    
    db.session.commit()
    flash('Зустріч розпочата!', 'success')
    return redirect(url_for('founder.view_meeting', meeting_id=meeting_id))

@founder_bp.route('/meetings/<int:meeting_id>/join', methods=['POST'])
@founder_required
def join_meeting(meeting_id):
    """Join a meeting"""
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if meeting.status != MeetingStatus.active.value:
        flash('Можна приєднатися лише до активної зустрічі!', 'danger')
        return redirect(url_for('founder.view_meeting', meeting_id=meeting_id))
    
    current_user_id = session.get('user_id')
    attendee = MeetingAttendee.query.filter_by(meeting_id=meeting_id, user_id=current_user_id).first()
    
    if not attendee:
        attendee = MeetingAttendee(
            meeting_id=meeting_id,
            user_id=current_user_id,
            joined_at=datetime.utcnow()
        )
        db.session.add(attendee)
        db.session.commit()
        flash('Ви приєдналися до зустрічі!', 'success')
    else:
        flash('Ви вже є учасником цієї зустрічі!', 'info')
    
    return redirect(url_for('founder.view_meeting', meeting_id=meeting_id))

@founder_bp.route('/meetings/<int:meeting_id>/leave', methods=['POST'])
@founder_required
def leave_meeting(meeting_id):
    """Leave a meeting"""
    meeting = Meeting.query.get_or_404(meeting_id)
    
    current_user_id = session.get('user_id')
    attendee = MeetingAttendee.query.filter_by(meeting_id=meeting_id, user_id=current_user_id).first()
    
    if attendee:
        attendee.left_at = datetime.utcnow()
        db.session.commit()
        flash('Ви вийшли із зустрічі!', 'success')
    
    return redirect(url_for('founder.view_meeting', meeting_id=meeting_id))

@founder_bp.route('/meetings/<int:meeting_id>/end', methods=['POST'])
@founder_required
def end_meeting(meeting_id):
    """End a meeting"""
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if meeting.status != MeetingStatus.active.value:
        flash('Можна завершити лише активну зустріч!', 'danger')
        return redirect(url_for('founder.view_meeting', meeting_id=meeting_id))
    
    meeting.status = MeetingStatus.completed.value
    
    # Set left_at for all attendees who haven't left
    for attendee in meeting.attendees:
        if not attendee.left_at:
            attendee.left_at = datetime.utcnow()
    
    # Generate protocol
    protocol_url = generate_protocol(meeting)
    meeting.protocol_url = protocol_url
    
    db.session.commit()
    flash('Зустріч завершена! Протокол згенеровано.', 'success')
    return redirect(url_for('founder.view_meeting', meeting_id=meeting_id))

@founder_bp.route('/meetings/<int:meeting_id>/message', methods=['POST'])
@founder_required
def add_message(meeting_id):
    """Add a message to the meeting chat"""
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if meeting.status != MeetingStatus.active.value:
        return jsonify({'error': 'Можна відправляти повідомлення лише в активній зустрічі!'}), 400
    
    current_user_id = session.get('user_id')
    content = request.form.get('content')
    
    if not content or not content.strip():
        return jsonify({'error': 'Повідомлення не може бути порожнім!'}), 400
    
    message = Message(
        meeting_id=meeting_id,
        user_id=current_user_id,
        content=content
    )
    
    db.session.add(message)
    db.session.commit()
    
    user = User.query.get(current_user_id)
    
    return jsonify({
        'id': message.id,
        'content': message.content,
        'user_name': user.full_name,
        'created_at': message.created_at.strftime('%H:%M:%S'),
        'user_id': user.id
    })

@founder_bp.route('/meetings/<int:meeting_id>/vote/<int:agenda_item_id>', methods=['POST'])
@founder_required
def vote(meeting_id, agenda_item_id):
    """Cast a vote for an agenda item"""
    meeting = Meeting.query.get_or_404(meeting_id)
    agenda_item = AgendaItem.query.get_or_404(agenda_item_id)
    
    if meeting.status != MeetingStatus.active.value:
        flash('Можна голосувати лише під час активної зустрічі!', 'danger')
        return redirect(url_for('founder.view_meeting', meeting_id=meeting_id))
    
    if not agenda_item.requires_voting:
        flash('Цей пункт порядку денного не потребує голосування!', 'danger')
        return redirect(url_for('founder.view_meeting', meeting_id=meeting_id))
    
    current_user_id = session.get('user_id')
    vote_value = request.form.get('vote')
    comment = request.form.get('comment', '')
    
    # Check if this user already voted
    existing_vote = MeetingVote.query.filter_by(agenda_item_id=agenda_item_id, user_id=current_user_id).first()
    
    if existing_vote:
        existing_vote.vote = VoteType(vote_value)
        existing_vote.comment = comment
        existing_vote.voted_at = datetime.utcnow()
    else:
        vote = MeetingVote(
            agenda_item_id=agenda_item_id,
            user_id=current_user_id,
            vote=VoteType(vote_value),
            comment=comment
        )
        db.session.add(vote)
    
    db.session.commit()
    flash('Ваш голос враховано!', 'success')
    return redirect(url_for('founder.view_meeting', meeting_id=meeting_id))

def generate_protocol(meeting):
    """Generate meeting protocol as PDF"""
    upload_folder = 'app/static/uploads/protocols'
    os.makedirs(upload_folder, exist_ok=True)
    
    filename = f"protocol_{meeting.id}_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(upload_folder, filename)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'app/static/fonts/DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)
    
    # Title
    pdf.cell(0, 10, f"Протокол зустрічі: {meeting.title}", 0, 1, 'C')
    pdf.ln(10)
    
    # Meeting details
    pdf.cell(0, 10, f"Дата: {meeting.date.strftime('%d.%m.%Y %H:%M')}", 0, 1)
    
    creator = User.query.get(meeting.creator_id)
    pdf.cell(0, 10, f"Організатор: {creator.full_name}", 0, 1)
    
    # Attendees
    pdf.ln(5)
    pdf.cell(0, 10, "Учасники:", 0, 1)
    attendees = MeetingAttendee.query.filter_by(meeting_id=meeting.id).all()
    for attendee in attendees:
        user = User.query.get(attendee.user_id)
        pdf.cell(0, 10, f"- {user.full_name}", 0, 1)
    
    # Agenda and voting results
    pdf.ln(5)
    pdf.cell(0, 10, "Порядок денний та результати:", 0, 1)
    agenda_items = meeting.agenda_items.order_by(AgendaItem.order).all()
    for i, item in enumerate(agenda_items):
        pdf.cell(0, 10, f"{i+1}. {item.title}", 0, 1)
        if item.description:
            pdf.multi_cell(0, 10, f"   {item.description}")
        
        if item.requires_voting:
            pdf.cell(0, 10, f"   Результати голосування:", 0, 1)
            pdf.cell(0, 10, f"   За: {item.yes_votes}, Проти: {item.no_votes}, Утримались: {item.abstain_votes}", 0, 1)
            pdf.cell(0, 10, f"   Висновок: {item.result}", 0, 1)
        pdf.ln(5)
    
    # Save the PDF
    pdf.output(filepath)
    
    # Return the URL path to the protocol
    return f"/static/uploads/protocols/{filename}"

@founder_bp.route('/meetings/<int:meeting_id>/protocol')
@founder_required
def view_protocol(meeting_id):
    """View meeting protocol"""
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if not meeting.protocol_url:
        flash('Протокол для цієї зустрічі ще не створено!', 'danger')
        return redirect(url_for('founder.view_meeting', meeting_id=meeting_id))
    
    return redirect(meeting.protocol_url)

# Manage founders
@founder_bp.route('/manage-founders', methods=['GET', 'POST'])
@founder_required
def manage_founders():
    """Manage founder users"""
    founders = User.query.filter_by(role=UserRole.founder).all()
    regular_members = User.query.filter_by(role=UserRole.MEMBER, is_admin=False).all()
    
    if request.method == 'POST':
        action = request.form.get('action')
        user_id = int(request.form.get('user_id'))
        user = User.query.get_or_404(user_id)
        
        if action == 'add':
            user.role = UserRole.founder
            flash(f'{user.full_name} успішно додано як засновника!', 'success')
        elif action == 'remove':
            user.role = UserRole.MEMBER
            flash(f'{user.full_name} видалено з засновників!', 'success')
            
        db.session.commit()
        return redirect(url_for('founder.manage_founders'))
    
    return render_template('founder/manage_founders.html', founders=founders, regular_members=regular_members)
