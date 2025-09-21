#!/usr/bin/env python3
"""
Test script for verifying the fixes to the Block model with NOT NULL constraints.
This script tests both the Block model's ability to handle missing columns
and its ability to handle NOT NULL constraints on name and slug fields.
"""

import os
import sys
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text, create_engine
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test_models')

# Create a test Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def setup_test_db_no_name_columns():
    """Create test database without name and slug columns."""
    logger.info("Setting up test database without name/slug columns...")
    
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create blocks table without name, slug columns
        db.engine.execute('''
        CREATE TABLE blocks (
            id INTEGER PRIMARY KEY,
            title VARCHAR(128) NOT NULL,
            content TEXT,
            type VARCHAR(32) NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            image_url VARCHAR(300),
            translations TEXT,
            image_data BLOB,
            image_mimetype VARCHAR(64)
        )
        ''')
        
        logger.info("Created blocks table without name/slug columns")

def setup_test_db_with_not_null_constraints():
    """Create test database with NOT NULL constraints on name and slug."""
    logger.info("Setting up test database with NOT NULL constraints...")
    
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create blocks table with NOT NULL constraints on name and slug
        db.engine.execute('''
        CREATE TABLE blocks (
            id INTEGER PRIMARY KEY,
            title VARCHAR(128) NOT NULL,
            content TEXT,
            type VARCHAR(32) NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            image_url VARCHAR(300),
            translations TEXT,
            name VARCHAR(50) NOT NULL,
            slug VARCHAR(50) NOT NULL,
            image_data BLOB,
            image_mimetype VARCHAR(64)
        )
        ''')
        
        logger.info("Created blocks table with NOT NULL constraints on name/slug")

def test_missing_columns():
    """Test handling of missing name and slug columns."""
    logger.info("Testing with missing name/slug columns...")
    
    from app.models.block import Block
    
    with app.app_context():
        # Create a test block
        block = Block(
            title="Test Block",
            content="This is a test block",
            type="info",
            is_active=True
        )
        
        # Test that the virtual properties still work
        logger.info(f"Virtual name property: {block.name}")
        logger.info(f"Virtual slug property: {block.slug}")
        
        try:
            # This should work even without name/slug columns
            db.session.add(block)
            db.session.commit()
            logger.info(f"Successfully created block with ID {block.id}")
            
            # Check that we can read it back
            retrieved = Block.query.get(block.id)
            logger.info(f"Retrieved block - ID: {retrieved.id}, Title: {retrieved.title}")
            logger.info(f"Retrieved block - Name (virtual): {retrieved.name}")
            logger.info(f"Retrieved block - Slug (virtual): {retrieved.slug}")
            
            return True
        except Exception as e:
            logger.error(f"Error creating/retrieving block: {e}")
            return False

def test_not_null_constraints():
    """Test handling of NOT NULL constraints on name and slug."""
    logger.info("Testing with NOT NULL constraints...")
    
    from app.models.block import Block
    
    with app.app_context():
        # Create a test block without explicitly setting name or slug
        block = Block(
            title="Test Block with NOT NULL",
            content="This block should handle NOT NULL constraints",
            type="info",
            is_active=True
        )
        
        # The model should automatically set default values
        logger.info(f"Name before save: {block.name}")
        logger.info(f"Slug before save: {block.slug}")
        
        try:
            # This should work by automatically setting default values
            db.session.add(block)
            db.session.commit()
            logger.info(f"Successfully created block with ID {block.id}")
            
            # Check that we can read it back
            retrieved = Block.query.get(block.id)
            logger.info(f"Retrieved block - ID: {retrieved.id}, Title: {retrieved.title}")
            logger.info(f"Retrieved block - Name: {retrieved.name}")
            logger.info(f"Retrieved block - Slug: {retrieved.slug}")
            
            # Verify that NULL values were not stored
            conn = db.engine.connect()
            result = conn.execute(text(f"SELECT name, slug FROM blocks WHERE id = {block.id}"))
            row = result.fetchone()
            logger.info(f"Direct DB query - Name: {row[0]}, Slug: {row[1]}")
            
            # Ensure we don't have NULL values
            if row[0] is None or row[1] is None:
                logger.error("NULL values were stored despite NOT NULL constraints!")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error creating/retrieving block: {e}")
            return False

def run_tests():
    """Run all tests."""
    logger.info("Starting tests...")
    
    # Import the Block model here to avoid circular imports
    from app.models.block import Block
    
    # Test 1: Missing columns
    setup_test_db_no_name_columns()
    test1_result = test_missing_columns()
    
    # Test 2: NOT NULL constraints
    setup_test_db_with_not_null_constraints()
    test2_result = test_not_null_constraints()
    
    # Report results
    logger.info("\n--- Test Results ---")
    logger.info(f"Test 1 (Missing Columns): {'PASSED' if test1_result else 'FAILED'}")
    logger.info(f"Test 2 (NOT NULL Constraints): {'PASSED' if test2_result else 'FAILED'}")
    
    if test1_result and test2_result:
        logger.info("\nALL TESTS PASSED! The Block model handles both scenarios correctly.")
    else:
        logger.error("\nSome tests FAILED. Please review the logs for details.")

if __name__ == "__main__":
    run_tests()