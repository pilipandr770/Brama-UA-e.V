"""
This script fixes the enum case mismatch issue by updating the Python models to match 
the database values correctly.
"""

import os
import sys
import inspect
from sqlalchemy import text
from app import db, create_app
from app.models.user import UserRole
from app.models.meeting import MeetingStatus, VoteType

app = create_app()

def fix_enum_values():
    with app.app_context():
        try:
            print("Fixing enum case mismatch issue...")
            
            # First, we need to query the database to check the actual enum values
            conn = db.engine.connect()
            
            # Check if any users have the 'founder' role
            result = conn.execute(text("SELECT COUNT(*) FROM users WHERE role = 'founder'")).scalar()
            has_founder_role = result > 0
            
            if has_founder_role:
                print("Found users with 'founder' role (lowercase). Updating Python model...")
                
                # Dynamically update the UserRole enum values to match database values
                UserRole.MEMBER._value_ = "member"
                UserRole.ADMIN._value_ = "admin" 
                UserRole.FOUNDER._value_ = "founder"
                
                # Clear SQLAlchemy's enum value cache
                UserRole._value2member_map_ = {
                    "member": UserRole.MEMBER,
                    "admin": UserRole.ADMIN,
                    "founder": UserRole.FOUNDER
                }
                
                # Also update MeetingStatus enum
                MeetingStatus.PLANNED._value_ = "planned"
                MeetingStatus.ACTIVE._value_ = "active"
                MeetingStatus.COMPLETED._value_ = "completed"
                MeetingStatus.CANCELLED._value_ = "cancelled"
                
                MeetingStatus._value2member_map_ = {
                    "planned": MeetingStatus.PLANNED,
                    "active": MeetingStatus.ACTIVE,
                    "completed": MeetingStatus.COMPLETED,
                    "cancelled": MeetingStatus.CANCELLED
                }
                
                # Update VoteType enum
                VoteType.YES._value_ = "yes"
                VoteType.NO._value_ = "no"
                VoteType.ABSTAIN._value_ = "abstain"
                
                VoteType._value2member_map_ = {
                    "yes": VoteType.YES,
                    "no": VoteType.NO,
                    "abstain": VoteType.ABSTAIN
                }
                
                print("✅ Python model updates complete!")
                
                # Create model file backups
                backup_model_files()
                
                # Update the actual model files
                update_model_files()
                
                print("✅ Updates applied successfully!")
            else:
                print("No lowercase 'founder' roles found. No changes needed.")
                
            conn.close()
            return 0
        except Exception as e:
            print(f"❌ Error fixing enum case mismatch: {e}")
            return 1

def backup_model_files():
    """Create backups of the model files"""
    user_model_path = inspect.getfile(UserRole)
    meeting_model_path = inspect.getfile(MeetingStatus)
    
    # Create backups
    with open(user_model_path, 'r') as f:
        user_model_content = f.read()
    
    with open(meeting_model_path, 'r') as f:
        meeting_model_content = f.read()
    
    with open(f"{user_model_path}.bak", 'w') as f:
        f.write(user_model_content)
    
    with open(f"{meeting_model_path}.bak", 'w') as f:
        f.write(meeting_model_content)
    
    print(f"✅ Created backups: {user_model_path}.bak and {meeting_model_path}.bak")

def update_model_files():
    """Update the model files to use lowercase enum values"""
    user_model_path = inspect.getfile(UserRole)
    meeting_model_path = inspect.getfile(MeetingStatus)
    
    # Update user.py
    with open(user_model_path, 'r') as f:
        content = f.read()
        
    content = content.replace('MEMBER = "MEMBER"', 'MEMBER = "member"')
    content = content.replace('ADMIN = "ADMIN"', 'ADMIN = "admin"')
    content = content.replace('FOUNDER = "FOUNDER"', 'FOUNDER = "founder"')
    
    with open(user_model_path, 'w') as f:
        f.write(content)
    
    # Update meeting.py
    with open(meeting_model_path, 'r') as f:
        content = f.read()
    
    content = content.replace('PLANNED = "PLANNED"', 'PLANNED = "planned"')
    content = content.replace('ACTIVE = "ACTIVE"', 'ACTIVE = "active"')
    content = content.replace('COMPLETED = "COMPLETED"', 'COMPLETED = "completed"')
    content = content.replace('CANCELLED = "CANCELLED"', 'CANCELLED = "cancelled"')
    
    content = content.replace('YES = "YES"', 'YES = "yes"')
    content = content.replace('NO = "NO"', 'NO = "no"')
    content = content.replace('ABSTAIN = "ABSTAIN"', 'ABSTAIN = "abstain"')
    
    with open(meeting_model_path, 'w') as f:
        f.write(content)
    
    print("✅ Model files updated successfully!")

if __name__ == "__main__":
    sys.exit(fix_enum_values())
