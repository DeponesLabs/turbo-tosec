============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.1, pluggy-1.6.0
rootdir: E:\HOME\GitHub\DeponesLabs\turbo-tosec
configfile: pyproject.toml
collected 1 item

test_session.py DB Config: Safe Mode engaged (Full integrity)

[ENGINE STATUS/ERROR]: Initiating Staged Mode ingestion with 8 parallel workers...

[ENGINE STATUS/ERROR]: No compatible ROM entries discovered to import.
F

================================== FAILURES ===================================
_________________ TestImportSession.test_full_ingestion_cycle _________________

self = <tests.test_session.TestImportSession object at 0x000001DD24E9E570>
MockParser = <MagicMock name='TurboParser' id='2049045592832'>
mock_env = ('C:\\Users\\Boccaccio\\AppData\\Local\\Temp\\pytest-of-Boccaccio\\pytest-55\\test_full_ingestion_cycle0\\TOSEC-v2024-...sers\\Boccaccio\\AppData\\Local\\Temp\\pytest-of-Boccaccio\\pytest-55\\test_full_ingestion_cycle0\\test_engine.duckdb')

    @patch('turbo_tosec.session.TurboParser')
    def test_full_ingestion_cycle(self, MockParser, mock_env):
        """
        Validates the complete orchestration lifecycle of the ImportSession.
        Mocks the infrastructure parsing layer to strictly evaluate state management,
        directory traversal, and database commit integration.
        """
        tosec_root, db_path = mock_env
    
        # Configure the mocked parser to bypass XML reading and directly yield a valid data tuple.
        # The schema must strictly adhere to the 14-column standard defined in DatabaseManager.
        # Configure the mocked parser to bypass XML reading.
        # Ensure this matches the exact schema expected by your DatabaseManager
        mock_instance = MockParser.return_value
        mock_instance.parse.return_value = [
            ("test_amiga.dat", "Amiga", "Games", "Mock Game", "Mock Title", 1990, "Mock Desc",
             "rom1.zip", 1024, "crc", "md5", "sha", "[!]", "AGA")
        ]
    
        # Initialize the dependencies properly using Injection
        config = DBConfig(memory=True, threads=1)
        db_manager = DatabaseManager(db_path=db_path, config=config)
    
        # Inject the manager into the Session
        session = ImportSession(db_manager=db_manager)
    
        mock_progress = lambda current, total: None
    
        def mock_status(msg):
            # Maintains visibility into the engine's internal routing
            print(f"\n[ENGINE STATUS/ERROR]: {msg}")
    
        # OPEN THE CONNECTION: The orchestrator requires an active database context
        with db_manager as db:
    
            # Execute the primary ingestion routine using Staged Mode
            result = session.ingest(
                source_path=tosec_root,
                mode='staged',   # <-- VALIDATING PRODUCTION PATH
                resume=False,
                force_new=True,
                progress_callback=mock_progress,
                status_callback=mock_status
            )
    
            # Validate post-execution state directly against the active database infrastructure
            count = db.conn.execute("SELECT COUNT(*) FROM roms").fetchone()[0]
>           assert count == 1
E           assert 0 == 1

test_session.py:74: AssertionError
------------------------------ Captured log call ------------------------------
WARNING  root:session.py:289 No compatible ROM entries discovered to import.
=========================== short test summary info ===========================
FAILED test_session.py::TestImportSession::test_full_ingestion_cycle - assert...
============================== 1 failed in 2.77s ==============================
