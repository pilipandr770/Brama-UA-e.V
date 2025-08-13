from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, abort
from flask_login import login_required, current_user
from app.models.meeting import Meeting, AgendaItem, MeetingAttendee, MeetingVote, VoteType, MeetingStatus
from app.models.user import UserRole
from app import db
from datetime import datetime
from flask_babel import _

meeting_bp = Blueprint('meeting', __name__)

# Helper function to check if user is a founder
def founder_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_founder:
            flash(_('This action requires founder privileges'), 'error')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# Helper function to check if user is an admin
def admin_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            flash(_('This action requires admin privileges'), 'error')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# Meeting list page - visible to all members but with different actions based on role
@meeting_bp.route('/meetings')
@login_required
def meetings_list():
    # Different queries based on user role
    if current_user.role == UserRole.admin or current_user.role == UserRole.founder:
        # Admins and founders see all meetings
        meetings = Meeting.query.order_by(Meeting.date.desc()).all()
    else:
        # Regular members only see active or completed meetings
        meetings = Meeting.query.filter(Meeting.status.in_([MeetingStatus.active, MeetingStatus.completed])) \
                               .order_by(Meeting.date.desc()).all()
    
    return render_template('meetings/list.html', meetings=meetings)

# Meeting detail page
@meeting_bp.route('/meetings/<int:meeting_id>')
@login_required
def meeting_detail(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    
    # Check if user is allowed to view this meeting
    if meeting.status == MeetingStatus.planned and current_user.role not in [UserRole.admin, UserRole.founder]:
        flash(_('This meeting is not yet available for viewing'), 'warning')
        return redirect(url_for('meeting.meetings_list'))
    
    agenda_items = AgendaItem.query.filter_by(meeting_id=meeting.id).order_by(AgendaItem.order).all()
    
    # Check if user has already voted on each agenda item
    user_votes = {}
    if current_user.is_founder:
        for item in agenda_items:
            vote = MeetingVote.query.filter_by(agenda_item_id=item.id, user_id=current_user.id).first()
            user_votes[item.id] = vote.vote.value if vote else None
    
    return render_template('meetings/detail.html', 
                          meeting=meeting, 
                          agenda_items=agenda_items,
                          user_votes=user_votes)

# Create new meeting - only for founders and admins
@meeting_bp.route('/meetings/new', methods=['GET', 'POST'])
@login_required
@founder_required
def new_meeting():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date')
        
        try:
            # Parse date from form
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            
            # Create new meeting
            new_meeting = Meeting(
                title=title,
                description=description,
                date=date,
                creator_id=current_user.id,
                status=MeetingStatus.planned
            )
            db.session.add(new_meeting)
            db.session.commit()
            
            flash(_('Meeting created successfully'), 'success')
            return redirect(url_for('meeting.meeting_detail', meeting_id=new_meeting.id))
        
        except Exception as e:
            flash(_('Error creating meeting: {}').format(str(e)), 'error')
    
    return render_template('meetings/create.html')

# Edit meeting
@meeting_bp.route('/meetings/<int:meeting_id>/edit', methods=['GET', 'POST'])
@login_required
@founder_required
def edit_meeting(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if request.method == 'POST':
        meeting.title = request.form.get('title')
        meeting.description = request.form.get('description')
        date_str = request.form.get('date')
        
        try:
            meeting.date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            meeting.updated_at = datetime.utcnow()
            
            # Update meeting status if provided
            status = request.form.get('status')
            if status:
                meeting.status = MeetingStatus(status)
            
            db.session.commit()
            flash(_('Meeting updated successfully'), 'success')
            return redirect(url_for('meeting.meeting_detail', meeting_id=meeting.id))
        
        except Exception as e:
            flash(_('Error updating meeting: {}').format(str(e)), 'error')
    
    return render_template('meetings/edit.html', meeting=meeting)

# Manage agenda items
@meeting_bp.route('/meetings/<int:meeting_id>/agenda', methods=['GET', 'POST'])
@login_required
@founder_required
def manage_agenda(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        requires_voting = 'requires_voting' in request.form
        
        # Get the highest existing order
        max_order = db.session.query(db.func.max(AgendaItem.order))\
                             .filter_by(meeting_id=meeting_id).scalar() or 0
        
        # Create new agenda item
        new_item = AgendaItem(
            meeting_id=meeting_id,
            title=title,
            description=description,
            requires_voting=requires_voting,
            order=max_order + 1
        )
        
        db.session.add(new_item)
        db.session.commit()
        
        # Send notification to all founders
        from app.websockets import notify_founders_about_agenda_item
        notify_founders_about_agenda_item(meeting_id, new_item)
        
        flash(_('Agenda item added successfully'), 'success')
        return redirect(url_for('meeting.manage_agenda', meeting_id=meeting_id))
    
    agenda_items = AgendaItem.query.filter_by(meeting_id=meeting_id).order_by(AgendaItem.order).all()
    return render_template('meetings/agenda.html', meeting=meeting, agenda_items=agenda_items)

# Delete agenda item
@meeting_bp.route('/meetings/agenda/<int:item_id>/delete', methods=['POST'])
@login_required
@founder_required
def delete_agenda_item(item_id):
    item = AgendaItem.query.get_or_404(item_id)
    meeting_id = item.meeting_id
    
    db.session.delete(item)
    db.session.commit()
    
    flash(_('Agenda item deleted'), 'success')
    return redirect(url_for('meeting.manage_agenda', meeting_id=meeting_id))

# Edit agenda item
@meeting_bp.route('/meetings/agenda/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
@founder_required
def edit_agenda_item(item_id):
    item = AgendaItem.query.get_or_404(item_id)
    
    if request.method == 'POST':
        item.title = request.form.get('title')
        item.description = request.form.get('description')
        item.requires_voting = 'requires_voting' in request.form
        
        db.session.commit()
        flash(_('Agenda item updated'), 'success')
        return redirect(url_for('meeting.manage_agenda', meeting_id=item.meeting_id))
    
    return render_template('meetings/edit_agenda_item.html', item=item)

# Vote on agenda item
@meeting_bp.route('/meetings/agenda/<int:item_id>/vote', methods=['POST'])
@login_required
def vote_agenda_item(item_id):
    if not current_user.is_founder:
        return jsonify({'error': _('Only founders can vote')}), 403
    
    item = AgendaItem.query.get_or_404(item_id)
    
    if not item.requires_voting:
        return jsonify({'error': _('This item does not require voting')}), 400
    
    meeting = Meeting.query.get(item.meeting_id)
    if meeting.status != MeetingStatus.active:
        return jsonify({'error': _('Voting is only allowed for active meetings')}), 400
    
    vote_value = request.form.get('vote')
    comment = request.form.get('comment', '')
    
    if vote_value not in [v.value for v in VoteType]:
        return jsonify({'error': _('Invalid vote value')}), 400
    
    # Check if user has already voted
    existing_vote = MeetingVote.query.filter_by(
        agenda_item_id=item_id,
        user_id=current_user.id
    ).first()
    
    try:
        if existing_vote:
            # Update existing vote
            existing_vote.vote = VoteType(vote_value)
            existing_vote.comment = comment
            existing_vote.voted_at = datetime.utcnow()
        else:
            # Create new vote
            new_vote = MeetingVote(
                agenda_item_id=item_id,
                user_id=current_user.id,
                vote=VoteType(vote_value),
                comment=comment
            )
            db.session.add(new_vote)
        
        db.session.commit()
        
        # Get updated vote counts
        results = {
            'yes': item.yes_votes,
            'no': item.no_votes,
            'abstain': item.abstain_votes,
            'result': item.result
        }
        
        return jsonify({
            'success': True,
            'message': _('Vote recorded successfully'),
            'results': results
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get vote results for an item
@meeting_bp.route('/meetings/agenda/<int:item_id>/results')
@login_required
def get_vote_results(item_id):
    item = AgendaItem.query.get_or_404(item_id)
    
    results = {
        'yes': item.yes_votes,
        'no': item.no_votes,
        'abstain': item.abstain_votes,
        'result': item.result
    }
    
    return jsonify(results)

# Mark attendance for a meeting
@meeting_bp.route('/meetings/<int:meeting_id>/attend', methods=['POST'])
@login_required
@founder_required
def mark_attendance(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    
    # Check if already marked as attending
    existing = MeetingAttendee.query.filter_by(
        meeting_id=meeting_id,
        user_id=current_user.id,
        left_at=None
    ).first()
    
    if existing:
        flash(_('You are already marked as attending this meeting'), 'info')
    else:
        # Mark attendance
        attendance = MeetingAttendee(
            meeting_id=meeting_id,
            user_id=current_user.id,
            joined_at=datetime.utcnow()
        )
        db.session.add(attendance)
        db.session.commit()
        flash(_('Attendance marked successfully'), 'success')
    
    return redirect(url_for('meeting.meeting_detail', meeting_id=meeting_id))

# Activate a meeting
@meeting_bp.route('/meetings/<int:meeting_id>/activate', methods=['POST'])
@login_required
@founder_required
def activate_meeting(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if meeting.status != MeetingStatus.planned:
        flash(_('Only planned meetings can be activated'), 'warning')
    else:
        meeting.status = MeetingStatus.active
        db.session.commit()
        flash(_('Meeting activated successfully'), 'success')
    
    return redirect(url_for('meeting.meeting_detail', meeting_id=meeting_id))

# Complete a meeting
@meeting_bp.route('/meetings/<int:meeting_id>/complete', methods=['POST'])
@login_required
@founder_required
def complete_meeting(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if meeting.status != MeetingStatus.active:
        flash(_('Only active meetings can be completed'), 'warning')
    else:
        meeting.status = MeetingStatus.completed
        
        # Close attendance for all attendees who haven't left
        open_attendances = MeetingAttendee.query.filter_by(
            meeting_id=meeting_id,
            left_at=None
        ).all()
        
        for attendance in open_attendances:
            attendance.left_at = datetime.utcnow()
        
        db.session.commit()
        flash(_('Meeting completed successfully'), 'success')
    
    return redirect(url_for('meeting.meeting_detail', meeting_id=meeting_id))

# Upload meeting protocol
@meeting_bp.route('/meetings/<int:meeting_id>/protocol', methods=['POST'])
@login_required
@founder_required
def upload_protocol(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    
    # Here you would handle file upload and storage
    # For simplicity, we'll just update with a URL
    protocol_url = request.form.get('protocol_url')
    
    if protocol_url:
        meeting.protocol_url = protocol_url
        db.session.commit()
        flash(_('Protocol URL updated successfully'), 'success')
    else:
        flash(_('Protocol URL is required'), 'error')
    
    return redirect(url_for('meeting.meeting_detail', meeting_id=meeting_id))

# Delete a meeting - only for admins
@meeting_bp.route('/meetings/<int:meeting_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_meeting(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    
    try:
        # Delete all related agenda items first (this will also delete related votes)
        agenda_items = AgendaItem.query.filter_by(meeting_id=meeting_id).all()
        for item in agenda_items:
            # Delete all votes for this agenda item
            MeetingVote.query.filter_by(agenda_item_id=item.id).delete()
            db.session.delete(item)
        
        # Delete all attendance records
        MeetingAttendee.query.filter_by(meeting_id=meeting_id).delete()
        
        # Now delete the meeting
        db.session.delete(meeting)
        db.session.commit()
        flash(_('Meeting deleted successfully'), 'success')
    except Exception as e:
        db.session.rollback()
        flash(_('Error deleting meeting: {}').format(str(e)), 'error')
    
    return redirect(url_for('meeting.meetings_list'))
