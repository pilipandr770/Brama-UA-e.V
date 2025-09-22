"""Set up environment variables for the application

This script creates or updates a .env file with the necessary environment variables
for the application to run correctly.

Usage:
    python setup_env.py

"""
import os
import sys
from pathlib import Path

def setup_env():
    # Define the path to the .env file
    env_path = Path(__file__).parent / '.env'
    
    # Define the environment variables
    env_vars = {
        'DATABASE_URL': 'postgresql://ittoken_db_user:Xm98VVSZv7cMJkopkdWRkgvZzC7Aly42@dpg-d0visga4d50c73ekmu4g-a.frankfurt-postgres.render.com/ittoken_db',
        'DB_SCHEMA': 'brama',
        'SECRET_KEY': 'your-secret-key-here',  # Change this to a secure value in production
        # Add any other environment variables needed for the application
    }
    
    # Read existing .env file if it exists
    existing_vars = {}
    if env_path.exists():
        print(f"Reading existing .env file at {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    existing_vars[key] = value
    
    # Merge existing and new environment variables, giving priority to existing ones
    merged_vars = {**env_vars, **existing_vars}
    
    # Write the .env file
    with open(env_path, 'w') as f:
        for key, value in merged_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f".env file created/updated at {env_path}")
    print("The following environment variables have been set:")
    for key in merged_vars:
        print(f"  - {key}")
    
    # Explain how to load the environment variables
    print("\nTo use these environment variables in PowerShell:")
    print("    Get-Content .env | ForEach-Object { if ($_ -match '(.+)=(.+)') { $env:$($matches[1]) = $matches[2] } }")
    print("\nTo use these environment variables in CMD:")
    print("    for /F \"tokens=1,2 delims==\" %G in (.env) do set %G=%H")
    print("\nTo use these environment variables in Bash:")
    print("    export $(grep -v '^#' .env | xargs)")
    
    # Create a simple batch file to load the environment variables in Windows
    batch_path = Path(__file__).parent / 'load_env.bat'
    with open(batch_path, 'w') as f:
        f.write('@echo off\n')
        f.write('echo Loading environment variables...\n')
        f.write('for /F "tokens=1,2 delims==" %%G in (.env) do set %%G=%%H\n')
        f.write('echo Environment variables loaded.\n')
    
    print(f"\nA batch file has been created at {batch_path}")
    print("Run it before starting the application to load the environment variables:")
    print("    load_env.bat")

if __name__ == "__main__":
    setup_env()