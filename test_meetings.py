"""
Test script to check if meetings tables are accessible
"""
from app import create_app, db
from app.models import Meeting

def main():
    # Create app with application context
    app = create_app()
    with app.app_context():
        try:
            print('Testing connection to meetings table...')
            # Try to query the meetings table
            count = Meeting.query.count()
            print(f'Connection to meetings table successful! Number of meetings: {count}')
        except Exception as e:
            print(f'Error accessing meetings table: {e}')

if __name__ == '__main__':
    main()