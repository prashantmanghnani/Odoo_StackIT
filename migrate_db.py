#!/usr/bin/env python3
"""
Database Migration Script
Adds reputation column to existing users table
"""

import sqlite3

def migrate_database():
    """Add reputation column to users table if it doesn't exist"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Check if reputation column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'reputation' not in columns:
        print("Adding reputation column to users table...")
        cursor.execute('ALTER TABLE users ADD COLUMN reputation INTEGER DEFAULT 0')
        
        # Update existing users with default reputation
        cursor.execute('UPDATE users SET reputation = 100 WHERE reputation IS NULL')
        
        conn.commit()
        print("✅ Reputation column added successfully!")
    else:
        print("✅ Reputation column already exists!")
    
    conn.close()

if __name__ == '__main__':
    print("🔄 Running database migration...")
    migrate_database()
    print("✅ Migration completed!") 