from app import db
from app.models.helpers import get_table_args
from datetime import datetime
import sqlalchemy as sa
import logging

# Set up logging
logger = logging.getLogger('app.models.block')

class Block(db.Model):
    """
    Model for content blocks on the website.
    
    Designed to work even without the name and slug fields in the database,
    using deferred loading and column reflection to handle missing columns.
    Both read and write operations are protected against missing columns.
    """
    __tablename__ = 'blocks'
    __table_args__ = get_table_args()
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic required fields that should exist in all DB versions
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(32), nullable=False)  # info, gallery, projects
    is_active = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(300), nullable=True)  # cover URL
    translations = db.Column(db.Text, nullable=True)  # JSON for multilingual content
    
    # Optional fields that might not exist in older database versions
    # Using deferred loading to avoid errors when querying
    _name = db.deferred(db.Column('name', db.String(50), nullable=True))
    _slug = db.deferred(db.Column('slug', db.String(50), nullable=True))
    image_data = db.deferred(db.Column(db.LargeBinary, nullable=True))
    image_mimetype = db.deferred(db.Column(db.String(64), nullable=True))
    
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
            optional_columns = ['name', 'slug', 'image_data', 'image_mimetype']
            
            for col_name in optional_columns:
                actual_name = col_name
                if col_name == 'name':
                    actual_name = '_name'  # Handle our property name mapping
                elif col_name == 'slug':
                    actual_name = '_slug'  # Handle our property name mapping
                
                if col_name not in cls._existing_columns:
                    missing_columns.append(actual_name)
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
            logger.warning(f"Error in Block.__declare_last__: {e}")
            # If any error occurs, continue without modifying mapper
            # This means we'll attempt to use all columns
    
    # Virtual properties for safe access to name and slug
    @property
    def name(self):
        """
        Get the name of the block. If name column doesn't exist or the value is None,
        generates a default name based on block type and id.
        """
        # If name column doesn't exist in DB, generate a default
        if self._existing_columns is not None and 'name' not in self._existing_columns:
            return f"block_{self.type}_{self.id or 'new'}"
            
        # If name column exists but value is None
        if hasattr(self, '_name'):
            try:
                if self._name is not None:
                    return self._name
            except sa.exc.SQLAlchemyError as e:
                logger.debug(f"SQLAlchemy error accessing name: {e}")
                
        # Generate a default name if needed (ensures we never return None)
        if hasattr(self, 'id') and self.id:
            default_name = f"block_{self.type}_{self.id}"
        else:
            default_name = f"block_{self.type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # If column exists in DB, update it with the default
        if self._existing_columns is None or 'name' in self._existing_columns:
            try:
                self._name = default_name
            except sa.exc.SQLAlchemyError as e:
                logger.debug(f"SQLAlchemy error setting default name: {e}")
                
        return default_name
    
    @name.setter
    def name(self, value):
        """
        Set the name of the block. Silently ignores if column doesn't exist.
        Always ensures a non-NULL value is set if the column exists.
        """
        # Only try to set if column exists in DB
        if self._existing_columns is None or 'name' in self._existing_columns:
            try:
                if value is None:
                    # Never set NULL values for name
                    if hasattr(self, 'id') and self.id:
                        self._name = f"block_{self.type}_{self.id}"
                    else:
                        self._name = f"block_{self.type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                else:
                    self._name = value
            except sa.exc.SQLAlchemyError as e:
                logger.debug(f"SQLAlchemy error setting name: {e}")
    
    @property
    def slug(self):
        """
        Get the slug of the block. If slug column doesn't exist or the value is None,
        generates a default slug based on name or block type and id.
        """
        # If slug column doesn't exist in DB
        if self._existing_columns is not None and 'slug' not in self._existing_columns:
            # Generate slug from name if available
            if hasattr(self, '_name') and self._name is not None:
                try:
                    return self._name.lower().replace(" ", "_")
                except (AttributeError, sa.exc.SQLAlchemyError):
                    pass
            return f"block_{self.type}_{self.id or 'new'}".lower()
            
        # If slug column exists but value is None
        if hasattr(self, '_slug'):
            try:
                if self._slug is not None:
                    return self._slug
                # Try to generate from name if slug is None
                if hasattr(self, '_name') and self._name is not None:
                    return self._name.lower().replace(" ", "_")
            except sa.exc.SQLAlchemyError as e:
                logger.debug(f"SQLAlchemy error accessing slug: {e}")
        
        # Generate a default slug if needed (ensures we never return None)
        if hasattr(self, 'id') and self.id:
            default_slug = f"block_{self.type}_{self.id}".lower()
        else:
            default_slug = f"block_{self.type}_{datetime.now().strftime('%Y%m%d%H%M%S')}".lower()
        
        # If column exists in DB, update it with the default
        if self._existing_columns is None or 'slug' in self._existing_columns:
            try:
                self._slug = default_slug
            except sa.exc.SQLAlchemyError as e:
                logger.debug(f"SQLAlchemy error setting default slug: {e}")
                
        return default_slug
    
    @slug.setter
    def slug(self, value):
        """
        Set the slug of the block. Silently ignores if column doesn't exist.
        Always ensures a non-NULL value is set if the column exists.
        """
        # Only try to set if column exists in DB
        if self._existing_columns is None or 'slug' in self._existing_columns:
            try:
                if value is None:
                    # Never set NULL values for slug
                    if hasattr(self, 'id') and self.id:
                        self._slug = f"block_{self.type}_{self.id}".lower()
                    else:
                        self._slug = f"block_{self.type}_{datetime.now().strftime('%Y%m%d%H%M%S')}".lower()
                else:
                    self._slug = value
            except sa.exc.SQLAlchemyError as e:
                logger.debug(f"SQLAlchemy error setting slug: {e}")
    
    def __init__(self, **kwargs):
        """
        Initialize a new Block instance, safely handling name and slug fields
        that might not exist in the database.
        """
        # Extract name and slug values before passing kwargs to parent
        name_value = kwargs.pop('name', None)
        slug_value = kwargs.pop('slug', None)
        
        # Remove internal attribute names to prevent errors
        kwargs.pop('_name', None)
        kwargs.pop('_slug', None)
        
        # Initialize with basic fields
        super(Block, self).__init__(**kwargs)
        
        # Generate default values for name and slug if they're needed
        if hasattr(self, 'type') and hasattr(self, 'id'):
            default_name = f"block_{self.type}_{self.id or 'new'}"
            default_slug = default_name.lower()
        else:
            # Fallback if type or id is not available yet
            default_name = f"block_{kwargs.get('type', 'unknown')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            default_slug = default_name.lower()
        
        # Always set name and slug values, using defaults if none provided
        # This ensures we never have NULL values for columns that require values
        if self._existing_columns is None or 'name' in self._existing_columns:
            try:
                self._name = name_value if name_value is not None else default_name
            except sa.exc.SQLAlchemyError as e:
                logger.debug(f"SQLAlchemy error setting name: {e}")
        
        if self._existing_columns is None or 'slug' in self._existing_columns:
            try:
                self._slug = slug_value if slug_value is not None else default_slug
            except sa.exc.SQLAlchemyError as e:
                logger.debug(f"SQLAlchemy error setting slug: {e}")