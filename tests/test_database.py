import os
import duckdb
import pytest

from turbo_tosec.database import DatabaseManager
from turbo_tosec.utils import calculate_file_hash

@pytest.fixture
def db_manager():

    db_path = "E:/HOME/Documents/Databases/turbo-tosec/duckdb/tosec-v2025-03-13.duckdb"
    db = DatabaseManager(db_path, read_only=True)
    
    try:
        db.connect()
    except:
        exit(1)
        
    return db
    
def test_load_column_metadata(db_manager):
    
    expected_columns = ['dat_filename', 'platform', 'category', 'game_name', 'title', 'release_year', 
                     'description', 'rom_name', 'size', 'crc', 'md5', 'sha1', 'status', 'system']
    
    db_manager._load_column_metadata()
    
    actual_columns = db_manager.columns
    
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

def test_find_by_hash_success(db_manager):
    """Test exact match via MD5 hash."""
    
    commando_path = r"E:\HOME\RetroVault\Games\C\Commando (1985)\MEDIA\Gamefiles\C64\TOSEC\Commando (1985)(Elite).d64"
    hash_commando = calculate_file_hash(commando_path)
    result = db_manager.find_by_hash(hash_commando, hash_type="md5")
    
    assert result is not None
    # Unpack expected fields (game_name, release_year, platform, description, score)
    game_name, title, release_year, platform, description, hash_value, score = result
    
    assert title == "Commando"
    assert release_year == 1985
    assert platform == "Commodore C64"
    
    assert score == 1.0  # Hash match must be 100%

def test_find_by_hash_not_found(db_manager):
    """Test non-existent hash."""
    result = db_manager.find_by_hash("non_existent_hash", hash_type="md5")
    assert result is None

def test_find_by_hash_invalid_type(db_manager):
    """Test that invalid hash types raise ValueError (Security check)."""
    with pytest.raises(ValueError, match="Invalid hash type"):
        db_manager.find_by_hash("some_hash", hash_type="invalid_type")

# --- Tests for find_by_fuzzy_name ---

def test_find_by_fuzzy_name_high_similarity(db_manager):
    """Test if a messy filename finds the correct clean game name."""
    # User has file: "Secret of Monkey Island.d64" -> Should find "Secret of Monkey Island"
    filename = "Secret of Monkey Island.d64" 
    
    result = db_manager.find_by_fuzzy_name(filename, platform="Commodore Amiga")
    
    assert result is not None
    dat_filename, game_name, title, release_year, platform, _, score = result
    
    assert title == "Secret of Monkey Island, The"
    assert score > 0.8  # Jaro-Winkler should give a high score for this

def test_find_by_fuzzy_name_with_platform_filter(db_manager):
    """
    Test that searching for the same game name in different platforms 
    returns the correct platform-specific record.
    """
    result = db_manager.find_by_fuzzy_name("It Came From the Desert III", platform="Commodore Amiga")
    
    assert result is not None
    dat_filename, game_name, title, release_year, platform, _, score = result
    
    assert title == "It Came from the Desert"
    assert platform == "Commodore Amiga"
    # assert "Disk 1 of 2" in game_name # Verify it picked the Amiga ROM, not C64

def test_find_by_fuzzy_name_no_match(db_manager):
    """Test a completely unrelated name."""
    result = db_manager.find_by_fuzzy_name("Zelda.zip", platform="Commodore 64")
    # Should be None because Zelda is not in our mock DB for C64
    assert result is None 

# --- Integration Test (Orchestrator) ---

def test_resolve_game_match_priority(db_manager):
    """
    Test that if hash is provided, it takes precedence over fuzzy name.
    """
    # We provide a filename that looks like Amiga, but a Hash that belongs to C64.
    # The system should trust the Hash and return C64.
    filename = "Turrican_Amiga_Fake_Name.zip"
    real_c64_hash = "md5_turrican"
    
    result = db_manager.resolve_game_match(filename, file_hash=real_c64_hash, hash_type="md5")
    
    assert result is not None
    dat_filename, game_name, title, release_year, platform, _, score = result
    
    assert platform == "Commodore C64" # Hash won
    assert score > 0.8
