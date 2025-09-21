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
    """
    Model for projects submitted to the platform.
    
    Designed to work even when optional fields like document_url, image_data, and 
    image_mimetype don't exist in the database, using deferred loading and
    column reflection to handle missing columns.
    """
    __tablename__ = 'projects'
    __table_args__ = get_table_args()
    
    # Dictionary to track which columns actually exist in the database
    # Will be populated in __declare_last__
    _existing_columns = None
    
    @classmethod
    def __declare_last__(cls):
        """
        SQLAlchemy hook called after mapper configuration is complete.
        Detects which columns actually exist in the database and configures
        the mapper to exclude non-existent columns from SQL operations.
        """
        from sqlalchemy import inspect
        import logging
        logger = logging.getLogger('app.models.project')
        
        try:
            engine = db.engine
            insp = inspect(engine)
            
            # Store existing columns at class level for later checks
            cls._existing_columns = set()
            
            # Try to detect columns from different schema scenarios
            schemas_to_check = ['brama', None]  # None = no schema (like in SQLite)
            
            for schema in schemas_to_check:
                try:
                    cols = insp.get_columns(cls.__tablename__, schema=schema)
                    if cols:  # If we found columns, store them and break
                        cls._existing_columns = {col['name'] for col in cols}
                        logger.info(f"Found {len(cls._existing_columns)} columns in {cls.__tablename__} table")
                        break
                except Exception as e:
                    logger.debug(f"Could not inspect schema {schema}: {e}")
                    continue
            
            # Identify which columns are missing
            missing_columns = []
            optional_columns = ['document_url', 'image_data', 'image_mimetype']
            
            for col_name in optional_columns:
                if col_name not in cls._existing_columns:
                    missing_columns.append(col_name)
                    logger.info(f"Column '{col_name}' does not exist in the database")
            
            # Configure the mapper to exclude these columns
            if missing_columns:
                # Get all columns that should be included
                include_properties = [c.name for c in cls.__table__.c 
                                     if c.name not in missing_columns]
                
                # Set the __mapper_args__ with include_properties
                if not hasattr(cls, '__mapper_args__'):
                    cls.__mapper_args__ = {}
                
                cls.__mapper_args__['include_properties'] = include_properties
                logger.info(f"Set include_properties for {cls.__name__}: {include_properties}")
                
        except Exception as e:
            logger.warning(f"Error in Project.__declare_last__: {e}")
            # If any error occurs, continue without modifying mapper

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
    
    # Additional fields
    category = db.Column(db.String(100))
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    social_links = db.Column(db.Text)  # JSON string or comma-separated list
    image_url = db.Column(db.String(300), nullable=True)
    
    # Optional fields that might not exist in older database versions
    # Using deferred loading to avoid errors when querying
    image_data = db.deferred(db.Column(db.LargeBinary, nullable=True))
    image_mimetype = db.deferred(db.Column(db.String(64), nullable=True))
    document_url = db.deferred(db.Column(db.String(300), nullable=True))
    
    # Relationship fields
    status = db.Column(db.String(20), default='pending')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id' if not get_table_args() else 'brama.users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    votes = db.relationship('Vote', backref='project', lazy='dynamic')
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id' if not get_table_args() else 'brama.blocks.id'), nullable=True)
    block = db.relationship('Block', backref=db.backref('projects', lazy='dynamic'))
    
    def get_image_data(self):
        """
        Safely get image data if the column exists in the database.
        """
        if self._existing_columns is not None and 'image_data' not in self._existing_columns:
            return None
            
        try:
            return self.image_data
        except Exception as e:
            logger = logging.getLogger('app.models.project')
            logger.debug(f"Error getting image_data: {e}")
            return None
            
    def get_image_mimetype(self):
        """
        Safely get image mimetype if the column exists in the database.
        """
        if self._existing_columns is not None and 'image_mimetype' not in self._existing_columns:
            return None
            
        try:
            return self.image_mimetype
        except Exception as e:
            logger = logging.getLogger('app.models.project')
            logger.debug(f"Error getting image_mimetype: {e}")
            return None
    
    def get_document_url(self):
        """
        Safely get document URL if the column exists in the database.
        """
        if self._existing_columns is not None and 'document_url' not in self._existing_columns:
            return None
            
        try:
            return self.document_url
        except Exception as e:
            logger = logging.getLogger('app.models.project')
            logger.debug(f"Error getting document_url: {e}")
            return None

