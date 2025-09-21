from app import db
from datetime import datetime
from app.models.helpers import get_table_args

class Vote(db.Model):
    __tablename__ = 'votes'
    __table_args__ = get_table_args()
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id' if not get_table_args() else 'brama.users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id' if not get_table_args() else 'brama.projects.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    __tablename__ = 'projects'
    __table_args__ = get_table_args()
    
    @classmethod
    def __declare_last__(cls):
        """
        Hook called after mapper configuration is complete.
        We use it to exclude columns that might not exist in the DB.
        """
        from sqlalchemy import inspect
        import logging
        logger = logging.getLogger('app.models.project')
        
        # Try to detect if columns exist in the database
        try:
            engine = db.engine
            insp = inspect(engine)
            
            # Try to get columns for different schema scenarios
            existing_columns = set()
            schemas_to_check = ['brama', None]  # None = без схемы (как в SQLite)
            
            for schema in schemas_to_check:
                try:
                    cols = insp.get_columns(cls.__tablename__, schema=schema)
                    existing_columns = {col['name'] for col in cols}
                    break  # Found table, exit loop
                except Exception:
                    continue
            
            # Exclude properties if columns don't exist
            exclude_props = []
            for column_name in ['document_url', 'image_data', 'image_mimetype']:
                if column_name not in existing_columns:
                    exclude_props.append(column_name)
                
            # Apply exclude_properties only if needed
            if exclude_props:
                # Get current mapper
                mapper = inspect(cls).mapper
                # Update exclude_properties in __mapper_args__
                if hasattr(mapper, 'exclude_properties'):
                    mapper.exclude_properties = list(set(mapper.exclude_properties) | set(exclude_props))
                else:
                    mapper._exclude_properties = exclude_props
                logger.info(f"Excluded columns from Project model: {exclude_props}")
        except Exception as e:
            logger.warning(f"Error in Project.__declare_last__: {e}")
            # If any error occurs, just continue without updating mapper
            pass

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    problem_description = db.Column(db.Text, nullable=False)
    goal = db.Column(db.Text, nullable=False)
    target_audience = db.Column(db.Text, nullable=False)
    implementation_plan = db.Column(db.Text, nullable=False)
    executor_info = db.Column(db.Text, nullable=False)
    total_budget = db.Column(db.Float, nullable=False)
    budget_breakdown = db.Column(db.Text, nullable=False)
    expected_result = db.Column(db.Text, nullable=False)
    risks = db.Column(db.Text, nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    reporting_plan = db.Column(db.Text, nullable=False)
    
    # Додаткові поля
    category = db.Column(db.String(100))
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    social_links = db.Column(db.Text)  # JSON рядок або список через кому
    image_url = db.Column(db.String(300), nullable=True)
    image_data = db.deferred(db.Column(db.LargeBinary, nullable=True))
    image_mimetype = db.deferred(db.Column(db.String(64), nullable=True))
    document_url = db.deferred(db.Column(db.String(300), nullable=True))
    status = db.Column(db.String(20), default='pending')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id' if not get_table_args() else 'brama.users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    votes = db.relationship('Vote', backref='project', lazy='dynamic')
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id' if not get_table_args() else 'brama.blocks.id'), nullable=True)
    block = db.relationship('Block', backref=db.backref('projects', lazy='dynamic'))

