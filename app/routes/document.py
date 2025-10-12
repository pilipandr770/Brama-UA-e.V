"""
Routes for meeting documents
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, jsonify, abort
from flask_login import login_required, current_user
from app.models.meeting import Meeting
from app.models.meeting_document import MeetingDocument
from app.models.user import UserRole, User
from app.routes.meeting import founder_required, admin_required
from app import db, socketio
import io
import os
from flask_babel import _

document_bp = Blueprint('meeting_document', __name__, url_prefix='/meeting')

# Helper function to check if user can access a document
def can_access_document(document):
    # Public documents are accessible to all authenticated users
    if document.is_public:
        return True
    
    # Admin and founders can access any document
    if current_user.is_admin or current_user.is_founder:
        return True
        
    # Otherwise, access denied
    return False

# List all documents for a meeting
@document_bp.route('/meetings/<int:meeting_id>/documents')
@login_required
def list_documents(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    
    # Filter documents based on user role
    if current_user.is_admin or current_user.is_founder:
        documents = meeting.documents.all()
    else:
        documents = meeting.documents.filter_by(is_public=True).all()
    
    return render_template('meetings/documents.html', meeting=meeting, documents=documents)

# Upload new document to a meeting
@document_bp.route('/meetings/<int:meeting_id>/documents/upload', methods=['GET', 'POST'])
@login_required
@founder_required
def upload_document(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description', '')
            is_public = 'is_public' in request.form
            file = request.files.get('file')
            
            if not name or not file or not file.filename:
                flash(_('Please provide a name and select a file'), 'error')
                return render_template('meetings/upload_document.html', meeting=meeting)
            
            # Read file data and create document
            file_data = file.read()
            
            if len(file_data) > 10 * 1024 * 1024:  # 10MB limit
                flash(_('File too large. Maximum size is 10MB.'), 'error')
                return render_template('meetings/upload_document.html', meeting=meeting)
            
            document = MeetingDocument(
                meeting_id=meeting_id,
                name=name,
                description=description,
                file_data=file_data,
                file_mimetype=file.mimetype,
                file_size=len(file_data),
                uploaded_by=current_user.id,
                is_public=is_public
            )
            
            db.session.add(document)
            db.session.commit()
            
            # Notify founders about the new document
            # from app.websockets import notify_about_new_document  # DISABLED: Socket.IO removed
            # notify_about_new_document(meeting_id, document)
            
            flash(_('Document uploaded successfully'), 'success')
            return redirect(url_for('meeting_document.list_documents', meeting_id=meeting_id))
            
        except Exception as e:
            db.session.rollback()
            flash(_('Error uploading document: {}').format(str(e)), 'error')
            print(f"Error uploading document: {str(e)}")
    
    return render_template('meetings/upload_document.html', meeting=meeting)

# Download a document
@document_bp.route('/meetings/documents/<int:document_id>')
@login_required
def download_document(document_id):
    document = MeetingDocument.query.get_or_404(document_id)
    
    # Check if user can access this document
    if not can_access_document(document):
        abort(403)  # Forbidden
    
    # Create a file-like object from the binary data
    file_data = io.BytesIO(document.file_data)
    
    # Try to determine a reasonable filename extension from MIME type
    extension = ''
    if document.file_mimetype == 'application/pdf':
        extension = '.pdf'
    elif document.file_mimetype == 'application/msword':
        extension = '.doc'
    elif document.file_mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        extension = '.docx'
    elif document.file_mimetype == 'application/vnd.ms-excel':
        extension = '.xls'
    elif document.file_mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        extension = '.xlsx'
    elif document.file_mimetype == 'application/vnd.ms-powerpoint':
        extension = '.ppt'
    elif document.file_mimetype == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
        extension = '.pptx'
    
    filename = f"{document.name}{extension}"
    
    return send_file(
        file_data,
        download_name=filename,
        mimetype=document.file_mimetype,
        as_attachment=True
    )

# Delete a document
@document_bp.route('/meetings/documents/<int:document_id>/delete', methods=['POST'])
@login_required
@founder_required
def delete_document(document_id):
    document = MeetingDocument.query.get_or_404(document_id)
    meeting_id = document.meeting_id
    
    # Only admin or document uploader can delete
    if not current_user.is_admin and document.uploaded_by != current_user.id:
        flash(_('You do not have permission to delete this document'), 'error')
        return redirect(url_for('meeting_document.list_documents', meeting_id=meeting_id))
    
    try:
        db.session.delete(document)
        db.session.commit()
        flash(_('Document deleted successfully'), 'success')
    except Exception as e:
        db.session.rollback()
        flash(_('Error deleting document: {}').format(str(e)), 'error')
    
    return redirect(url_for('meeting_document.list_documents', meeting_id=meeting_id))

# AJAX endpoint to get document info
@document_bp.route('/api/meetings/documents/<int:document_id>')
@login_required
def get_document_info(document_id):
    document = MeetingDocument.query.get_or_404(document_id)
    
    # Check if user can access this document
    if not can_access_document(document):
        abort(403)  # Forbidden
    
    return jsonify({
        'id': document.id,
        'name': document.name,
        'description': document.description,
        'file_size': document.file_size,
        'file_mimetype': document.file_mimetype,
        'uploaded_at': document.uploaded_at.strftime('%Y-%m-%d %H:%M'),
        'is_public': document.is_public,
        'uploader_id': document.uploaded_by
    })
