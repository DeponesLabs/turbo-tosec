import pytest
import os
from turbo_tosec.database import DatabaseManager

def test_load_column_metadata():
    
    expected_columns = ['dat_filename', 'platform', 'category', 'game_name', 'title', 'release_year', 
                     'description', 'rom_name', 'size', 'crc', 'md5', 'sha1', 'status', 'system']
    
    db_path = "E:/HOME/Documents/Databases/turbo-tosec/duckdb/tosec-v2025-03-13.duckdb"
    db = DatabaseManager(db_path, read_only=True)
    db.connect()
    db._load_column_metadata()
    
    actual_columns = db.columns
    
    # *** Print Debug ***
    print(f"\n From DB: ({len(actual_columns)}): {actual_columns}")
    print(f"Expected: ({len(expected_columns)}): {expected_columns}")
    
    # Find diff with sets (Unordered comparison)
    missing_in_db = set(expected_columns) - set(actual_columns)
    extra_in_db = set(actual_columns) - set(expected_columns)
    
    if missing_in_db:
        print(f"Missing columns in DB: {missing_in_db}")
    if extra_in_db:
        print(f"Extra columns in DB: {extra_in_db}")

    # Assert !
    assert actual_columns == expected_columns
