import pytest
from unittest.mock import patch
import pyarrow as pa
from turbo_tosec.session import ImportSession
from turbo_tosec.database import DBConfig, DatabaseManager

@pytest.fixture
def mock_env(tmp_path):
    """
    Constructs a temporary, isolated file system mimicking a standard TOSEC release structure.
    Returns a tuple containing the paths to the mock root directory and the target DuckDB file.
    """
    tosec_root = tmp_path / "TOSEC-v2024-01-01"
    tosec_root.mkdir()
    
    fake_dat = tosec_root / "test_amiga.dat"
    fake_dat.write_text("<data></data>")
    
    db_path = tmp_path / "test_engine.duckdb"
    
    return str(tosec_root), str(db_path)

class TestImportSession:
    
    @patch('turbo_tosec.session.TurboParser')
    def test_direct_mode_ingestion(self, MockParser, mock_env):
        """
        Validates the complete lifecycle of the ImportSession.
        Mocks the infrastructure parsing layer to strictly evaluate state management, 
        directory traversal, and database commit integration.
        """
        tosec_root, db_path = mock_env
        
        mock_arrow_data = [
            pa.array(["test_amiga.dat"]),          # dat_filename
            pa.array(["Amiga"]),                   # platform
            pa.array(["Games"]),                   # category
            pa.array(["Mock Game"]),               # game_name
            pa.array(["Mock Title"]),              # title
            pa.array([1990], type=pa.int32()),     # release_year (INTEGER)
            pa.array(["Mock Desc"]),               # description
            pa.array(["rom1.zip"]),                # rom_name
            pa.array([1024], type=pa.int64()),     # size (BIGINT)
            pa.array(["crc"]),                     # crc
            pa.array(["md5"]),                     # md5
            pa.array(["sha1"]),                    # sha1
            pa.array(["[!]"]),                     # status
            pa.array(["AGA"])                      # system
        ]
        
        schema_names = [
            'dat_filename', 'platform', 'category', 'game_name', 'title', 
            'release_year', 'description', 'rom_name', 'size', 'crc', 
            'md5', 'sha1', 'status', 'system'
        ]
        
        mock_arrow_table = pa.Table.from_arrays(mock_arrow_data, names=schema_names)
        
        mock_instance = MockParser.return_value
        mock_instance.parse_to_arrow_stream.return_value = [mock_arrow_table]
        
        config = DBConfig(memory=True, threads=1)
        db_manager = DatabaseManager(db_path=db_path, config=config)
        session = ImportSession(db_manager=db_manager)
        
        mock_progress = lambda current, total: None
        def mock_status(msg):
            print(f"\n[ENGINE STATUS]: {msg}")
            
        with db_manager as db:
            result = session.ingest(source_path=tosec_root, mode='direct',  resume=False, force_new=True, 
                                    progress_callback=mock_progress, status_callback=mock_status)
            
            count = db.conn.execute("SELECT COUNT(*) FROM roms").fetchone()[0]
            
            assert count == 1
            assert db.get_db_version() == "TOSEC-v2024-01-01"
            
            
            
    
    
    