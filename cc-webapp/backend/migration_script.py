#!/usr/bin/env python3
"""
Database migration script to add missing columns
"""
import sqlite3
import os

def migrate_database():
    """Add missing columns to existing database"""
    
    # Database paths to migrate
    db_paths = [
        "./test.db",
        "./test_unlock.db", 
        "./test_rewards.db",
        "./test_notification.db",
        "./app.db"  # Production database if exists
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"Migrating {db_path}...")
            migrate_single_db(db_path)
        else:
            print(f"Database {db_path} not found, skipping...")

def migrate_single_db(db_path):
    """Migrate a single database file"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add source_description column to user_rewards table
        try:
            cursor.execute("ALTER TABLE user_rewards ADD COLUMN source_description TEXT")
            print(f"  Added source_description column to user_rewards in {db_path}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"  source_description column already exists in {db_path}")
            else:
                print(f"  Error adding source_description: {e}")
        
        # Add name column to user_segments table
        try:
            cursor.execute("ALTER TABLE user_segments ADD COLUMN name VARCHAR(50)")
            print(f"  Added name column to user_segments in {db_path}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"  name column already exists in {db_path}")
            else:
                print(f"  Error adding name: {e}")
        
        conn.commit()
        print(f"  Migration completed for {db_path}")
        
    except Exception as e:
        print(f"  Error migrating {db_path}: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
