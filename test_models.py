#!/usr/bin/env python3
"""
Test script for checking the robustness of models with optional columns.

This script tests whether the Block and Project models can handle both
reading and writing operations when certain columns don't exist in the database.

Usage:
    python test_models.py

The script will:
1. Create test blocks and projects
2. Read them back
3. Try accessing optional columns
4. Try modifying optional columns

It uses a testing database, not your production database.
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test_models')
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Create a test Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Import the models - this should be done after setting up the app and db
from app.models.helpers import get_table_args
from app.models.block import Block
from app.models.project import Project
from app.models.user import User

def setup_test_db():
    """Create test database tables with missing columns."""
    logger.info("Setting up test database...")
    
    with app.app_context():
        # Create tables without the optional columns
        db.drop_all()
        
        # Create users table first (for foreign keys)
        db.engine.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username VARCHAR(80) NOT NULL,
            email VARCHAR(120) NOT NULL,
            password_hash VARCHAR(128),
            is_admin BOOLEAN DEFAULT 0,
            is_founder BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create blocks table without name, slug, image_data, image_mimetype
        db.engine.execute('''
        CREATE TABLE blocks (
            id INTEGER PRIMARY KEY,
            title VARCHAR(128) NOT NULL,
            content TEXT,
            type VARCHAR(32) NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            image_url VARCHAR(300),
            translations TEXT
        )
        ''')
        
        # Create projects table without image_data, image_mimetype, document_url
        db.engine.execute('''
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            problem_description TEXT NOT NULL,
            goal TEXT NOT NULL,
            target_audience TEXT NOT NULL,
            implementation_plan TEXT NOT NULL,
            executor_info TEXT NOT NULL,
            total_budget FLOAT NOT NULL,
            budget_breakdown TEXT NOT NULL,
            expected_result TEXT NOT NULL,
            risks TEXT NOT NULL,
            duration VARCHAR(100) NOT NULL,
            reporting_plan TEXT NOT NULL,
            category VARCHAR(100),
            location VARCHAR(100),
            website VARCHAR(200),
            social_links TEXT,
            image_url VARCHAR(300),
            status VARCHAR(20) DEFAULT 'pending',
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            block_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(block_id) REFERENCES blocks(id)
        )
        ''')
        
        # Create votes table
        db.engine.execute('''
        CREATE TABLE votes (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )
        ''')
        
        logger.info("Test database setup complete!")

def create_test_data():
    """Create test data in the database."""
    logger.info("Creating test data...")
    
    with app.app_context():
        # Create a test user
        user = User(
            username="testuser",
            email="test@example.com",
            is_admin=True
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        
        # Create test blocks
        blocks = [
            Block(
                title="Test Block 1",
                content="This is test content for block 1",
                type="info",
                is_active=True,
                image_url="https://example.com/image1.jpg",
                translations='{"en": {"title": "Test Block 1 in English", "content": "This is test content for block 1 in English"}}'
            ),
            Block(
                title="Test Block 2",
                content="This is test content for block 2",
                type="gallery",
                is_active=True,
                image_url="https://example.com/image2.jpg",
                # Try to set name and slug (which don't exist in our test DB)
                name="test-block-2",
                slug="test-block-2-slug"
            )
        ]
        db.session.add_all(blocks)
        db.session.commit()
        
        # Create test projects
        projects = [
            Project(
                title="Test Project 1",
                problem_description="Test problem",
                goal="Test goal",
                target_audience="Test audience",
                implementation_plan="Test plan",
                executor_info="Test executor",
                total_budget=1000.0,
                budget_breakdown="Test breakdown",
                expected_result="Test result",
                risks="Test risks",
                duration="1 month",
                reporting_plan="Test reporting",
                category="Test Category",
                location="Test Location",
                website="https://example.com",
                social_links='{"facebook": "fb.com/test"}',
                image_url="https://example.com/project1.jpg",
                status="pending",
                user_id=user.id,
                block_id=blocks[0].id
            )
        ]
        db.session.add_all(projects)
        db.session.commit()
        
        logger.info("Test data created!")

def test_read_operations():
    """Test reading from models with missing columns."""
    logger.info("Testing read operations...")
    
    with app.app_context():
        # Test reading blocks
        blocks = Block.query.all()
        logger.info(f"Found {len(blocks)} blocks")
        
        for block in blocks:
            # Test accessing all properties including virtual ones
            logger.info(f"Block ID: {block.id}")
            logger.info(f"Block Title: {block.title}")
            logger.info(f"Block Type: {block.type}")
            logger.info(f"Block Name (virtual property): {block.name}")
            logger.info(f"Block Slug (virtual property): {block.slug}")
            
            # Try to access columns that don't exist
            try:
                logger.info(f"Direct access to _name: {getattr(block, '_name', 'Not accessible')}")
            except Exception as e:
                logger.info(f"Error accessing _name: {e}")
        
        # Test reading projects
        projects = Project.query.all()
        logger.info(f"Found {len(projects)} projects")
        
        for project in projects:
            logger.info(f"Project ID: {project.id}")
            logger.info(f"Project Title: {project.title}")
            logger.info(f"Project Budget: {project.total_budget}")
            
            # Try to access columns that don't exist
            logger.info(f"document_url: {project.get_document_url()}")
            logger.info(f"image_data: {project.get_image_data()}")
            logger.info(f"image_mimetype: {project.get_image_mimetype()}")

def test_write_operations():
    """Test writing to models with missing columns."""
    logger.info("Testing write operations...")
    
    with app.app_context():
        # Test creating a new block with optional fields
        new_block = Block(
            title="New Test Block",
            content="This is new test content",
            type="info",
            is_active=True,
            name="new-test-block",  # This column doesn't exist
            slug="new-test-block-slug",  # This column doesn't exist
            image_data=b"fake image data",  # This column doesn't exist
            image_mimetype="image/jpeg"  # This column doesn't exist
        )
        
        try:
            db.session.add(new_block)
            db.session.commit()
            logger.info(f"Successfully created block with ID: {new_block.id}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create block: {e}")
        
        # Test creating a new project with optional fields
        new_project = Project(
            title="New Test Project",
            problem_description="New test problem",
            goal="New test goal",
            target_audience="New test audience",
            implementation_plan="New test plan",
            executor_info="New test executor",
            total_budget=2000.0,
            budget_breakdown="New test breakdown",
            expected_result="New test result",
            risks="New test risks",
            duration="2 months",
            reporting_plan="New test reporting",
            category="New Test Category",
            location="New Test Location",
            website="https://example.org",
            social_links='{"twitter": "twitter.com/test"}',
            image_url="https://example.org/project1.jpg",
            status="pending",
            user_id=1,
            document_url="https://example.org/doc.pdf",  # This column doesn't exist
            image_data=b"fake project image data",  # This column doesn't exist
            image_mimetype="image/png"  # This column doesn't exist
        )
        
        try:
            db.session.add(new_project)
            db.session.commit()
            logger.info(f"Successfully created project with ID: {new_project.id}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create project: {e}")

def test_update_operations():
    """Test updating models with missing columns."""
    logger.info("Testing update operations...")
    
    with app.app_context():
        # Update a block
        block = Block.query.first()
        if block:
            try:
                block.title = "Updated Title"
                block.name = "updated-name"  # This column doesn't exist
                block.slug = "updated-slug"  # This column doesn't exist
                db.session.commit()
                logger.info(f"Successfully updated block ID {block.id}")
                logger.info(f"Updated title: {block.title}")
                logger.info(f"Virtual name property: {block.name}")
                logger.info(f"Virtual slug property: {block.slug}")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Failed to update block: {e}")
        
        # Update a project
        project = Project.query.first()
        if project:
            try:
                project.title = "Updated Project Title"
                project.document_url = "https://updated-url.com/doc.pdf"  # This column doesn't exist
                db.session.commit()
                logger.info(f"Successfully updated project ID {project.id}")
                logger.info(f"Updated title: {project.title}")
                logger.info(f"Document URL: {project.get_document_url()}")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Failed to update project: {e}")

def run_tests():
    """Run all tests."""
    setup_test_db()
    create_test_data()
    test_read_operations()
    test_write_operations()
    test_update_operations()
    
    logger.info("All tests completed!")
    logger.info("If you didn't see any error messages, the models are working correctly!")

if __name__ == "__main__":
    run_tests()