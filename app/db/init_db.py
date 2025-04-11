"""
This file is kept for reference only.
The actual database schema is defined in docs/database_schema.sql
"""

import os
import sys
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.db.session import engine

def recreate_database_schema():
    """
    Recreates the database schema by executing the SQL commands from database_schema.sql.
    This script should be run separately from the main application.
    """
    try:
        # Get the path to the database schema file
        schema_file = Path(__file__).parent.parent / "docs" / "database_schema.sql"
        
        if not schema_file.exists():
            print(f"Error: Schema file not found at {schema_file}")
            sys.exit(1)
            
        # Read the SQL commands
        with open(schema_file, 'r') as f:
            sql_commands = f.read()
            
        # Split the commands by semicolon and execute each one
        commands = sql_commands.split(';')
        
        with engine.connect() as connection:
            for command in commands:
                # Skip empty commands
                if not command.strip():
                    continue
                    
                try:
                    connection.execute(text(command))
                    connection.commit()
                    print(f"Executed: {command[:100]}...")  
                except SQLAlchemyError as e:
                    print(f"Error executing command: {str(e)}")
                    print(f"Command: {command[:100]}...")
                    connection.rollback()
                    
        print("Database schema recreated successfully!")
        
    except Exception as e:
        print(f"Error recreating database schema: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("Recreating database schema...")
    recreate_database_schema() 