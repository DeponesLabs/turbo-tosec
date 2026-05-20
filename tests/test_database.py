# tests/test_database.py
import pytest
import os
from turbo_tosec.database import DatabaseManager, DBConfig

@pytest.fixture
def temp_db(tmp_path):
    """
    A Pytest fixture that creates a fresh, temporary DuckDB database for each test.
    It automatically cleans up the file from the hard drive after the test finishes.
    """
    db_file = tmp_path / "test_tosec.duckdb"
    
    # We use a memory-optimized config for blazingly fast tests
    config = DBConfig(memory=True, threads=1)
    
    # Using the context manager ensures __enter__ and __exit__ are tested and closed cleanly
    with DatabaseManager(str(db_file), config=config) as db:
        yield db

class TestDatabaseManager:

    def test_schema_creation_and_versioning(self, temp_db):
        """Tests that tables are created and version state can be saved/loaded."""
        # A fresh DB should have no version
        assert temp_db.get_db_version() is None
        
        # Set a version and verify it persists
        temp_db.set_db_version("TOSEC-v2024-01-01")
        assert temp_db.get_db_version() == "TOSEC-v2024-01-01"

    def test_wipe_database(self, temp_db):
        """Tests that wipe completely truncates tables and drops the version."""
        # Setup state
        temp_db.set_db_version("TOSEC-v1999")
        
        # Action
        temp_db.wipe_database()
        
        # Verify
        assert temp_db.get_db_version() is None
        
        # Verify the 'roms' table exists but is empty
        count = temp_db.conn.execute("SELECT COUNT(*) FROM roms").fetchone()[0]
        assert count == 0

    def test_insert_batch(self, temp_db):
        """Tests that data is correctly inserted and processed files are tracked."""
        # Create a dummy buffer matching the 14-column schema your DatabaseManager expects
        dummy_buffer = [
            # filename, title, year, publisher, system, size, crc, md5, sha1, is_bad, is_cracked, is_verified, is_alternate, languages
            ("game1.zip", "Game One", "1990", "Pub", "Amiga", 1024, "crc1", "md51", "sha11", False, False, True, False, "En"),
            ("game2.zip", "Game Two", "1992", "Pub", "Amiga", 2048, "crc2", "md52", "sha12", True, False, False, False, "Fr")
        ]
        
        # Action
        temp_db.insert_batch(dummy_buffer)
        
        # Verify Roms
        rom_count = temp_db.conn.execute("SELECT COUNT(*) FROM roms").fetchone()[0]
        assert rom_count == 2
        
        # Verify Processed Files
        processed = temp_db.get_processed_files()
        assert "game1.zip" in processed
        assert "game2.zip" in processed
        assert len(processed) == 2

    def test_parquet_export_import(self, temp_db, tmp_path):
        """Tests DuckDB's ability to round-trip data through Parquet."""
        parquet_file = str(tmp_path / "export.parquet")
        
        # Insert some data
        dummy_buffer = [("test.zip", "Test", "1990", "P", "S", 1, "c", "m", "s", False, False, False, False, "")]
        temp_db.insert_batch(dummy_buffer)
        
        # Export it
        temp_db.export_to_parquet(parquet_file)
        assert os.path.exists(parquet_file)
        
        # Wipe the database to prove it's empty
        temp_db.wipe_database()
        assert temp_db.conn.execute("SELECT COUNT(*) FROM roms").fetchone()[0] == 0
        
        # Import it back
        temp_db.import_from_parquet(parquet_file)
        assert temp_db.conn.execute("SELECT COUNT(*) FROM roms").fetchone()[0] == 1