from app import db
from datetime import datetime
import enum

class MeetingStatus(enum.Enum):
    planned = "planned"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"

class VoteType(enum.Enum):
    yes = "yes"
    no = "no"
    abstain = "abstain"

class Meeting(db.Model):
    __tablename__ = 'meetings'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.Enum(MeetingStatus), default=MeetingStatus.planned)
    protocol_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agenda_items = db.relationship('AgendaItem', backref='meeting', lazy='dynamic', cascade='all, delete-orphan')
    attendees = db.relationship('MeetingAttendee', backref='meeting', lazy='dynamic', cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='meeting', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def attendee_count(self):
        return self.attendees.count()
    
    @property
    def has_quorum(self):
        # 3 is the quorum number as specified
        return self.attendees.count() >= 3

class AgendaItem(db.Model):
    __tablename__ = 'agenda_items'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    requires_voting = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    votes = db.relationship('MeetingVote', backref='agenda_item', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def yes_votes(self):
        return self.votes.filter_by(vote=VoteType.yes).count()
    
    @property
    def no_votes(self):
        return self.votes.filter_by(vote=VoteType.no).count()
    
    @property
    def abstain_votes(self):
        return self.votes.filter_by(vote=VoteType.abstain).count()
    
    @property
    def result(self):
        if self.yes_votes > self.no_votes:
            return "Approved"
        elif self.no_votes > self.yes_votes:
            return "Rejected"
        else:
            return "Tied"

class MeetingAttendee(db.Model):
    __tablename__ = 'meeting_attendees'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    left_at = db.Column(db.DateTime)

class MeetingVote(db.Model):
    __tablename__ = 'meeting_votes'
    
    id = db.Column(db.Integer, primary_key=True)
    agenda_item_id = db.Column(db.Integer, db.ForeignKey('agenda_items.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    vote = db.Column(db.Enum(VoteType))
    comment = db.Column(db.Text)
    voted_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
