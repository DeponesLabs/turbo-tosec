import os
import time
import platform
import psutil
import logging
import ctypes
from types import TracebackType
from typing import Dict, List, Tuple, Callable, Any, NamedTuple
import duckdb

from turbo_tosec.domainobjects import TosecDat

class DBConfig(NamedTuple):
    memory: str = "4GB"
    threads: int = 1
    turbo: bool = False
    
class DatabaseManager:
    """
    Manages DuckDB connection, schema creation, and data insertion.
    Encapsulates all SQL logic to keep the main flow clean.
    """
    @property
    def columns(self) -> List[str]:
        return self._column_names

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        """Getter that ensures the connection exists before returning it."""
        if self._conn is None:
            raise RuntimeError("Database connection has not been initialized.")
        return self._conn
    
    def __init__(self, db_path: str, config: DBConfig | None, read_only: bool = False) -> None:
        
        self.db_path = db_path
        # If config is None use default config
        self.config = config or DBConfig()
        self.read_only = read_only
        self._conn: duckdb.DuckDBPyConnection | None = None
        self._column_names: List[str] = []    # for GUI
        
    def __enter__(self) -> "DatabaseManager":
        
        self.connect()
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        
        self.close()

    def connect(self) -> None:
        """Establishes connection and ensures schema exists."""
        self._conn = duckdb.connect(self.db_path, read_only=self.read_only)
        
        # Turbo settings and Table Setup in WRITE mode (CLI)
        if not self.read_only:
            self._apply_performance_settings()
            self._setup_schema()
            
        self._load_column_metadata()
    
    def _apply_performance_settings(self) -> None:
        """
        Applies memory and thread settings for CLI Ingestion mode.
        Prints status messages to console.
        """
        if self.config.turbo:
            print(f"DB: Turbo Mode engaged (Low safety, High speed) | Mem: {self.config.memory} | Db Threads: {self.config.threads}")
            
            # Memory Configuration
            final_mem = self.config.memory
            if "%" in final_mem or final_mem == "auto":
                final_mem = self._get_optimal_ram_limit(final_mem)
                
            # DuckDB PRAGMA Settings
            self.conn.execute(f"PRAGMA memory_limit='{final_mem}'")
            self.conn.execute(f"PRAGMA threads={self.config.threads}")
            
            # Safety Off (Optional: WAL can be disabled for increased speed, but it's risky)
            # self.conn.execute("PRAGMA disable_checkpoint_on_shutdown") 
        else:
            print("DB Config: Safe Mode engaged (Full integrity)")
            
    def close(self) -> None:
        """Closes the database connection safely."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def _setup_schema(self, target_conn: duckdb.DuckDBPyConnection | None = None) -> None:
        # Use the passed connection if it exists, otherwise use the default property
        conn = target_conn or self.conn

        # Main ROM table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS roms (
                dat_filename VARCHAR,
                platform VARCHAR,
                category VARCHAR,
                game_name VARCHAR,
                title VARCHAR,
                release_year INTEGER,
                description VARCHAR,
                rom_name VARCHAR,
                size BIGINT,
                crc VARCHAR,
                md5 VARCHAR,
                sha1 VARCHAR,
                status VARCHAR,
                system VARCHAR
            )
        """)
        # Processed files table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS processed_files (
                filename VARCHAR PRIMARY KEY,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Metadata
        conn.execute("CREATE TABLE IF NOT EXISTS db_metadata (key VARCHAR PRIMARY KEY, value VARCHAR)")
    
    def _load_column_metadata(self) -> None:
        """Caches column names for the GUI model."""
        try:
            cursor = self.conn.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'roms'")
            res1 = cursor.fetchone()
            if not res1 or res1[0] == 0:
                self._column_names = []
            
            res2 = self.conn.execute("SELECT * FROM roms LIMIT 0")
            if res2.description:
                self._column_names = [desc[0] for desc in res2.description]
            else:
                self._column_names = []
                
        except Exception:
            self._column_names = []
    
    def get_metadata_value(self, key: str) -> str | None:
        
        try:
            result = self.conn.execute("SELECT value FROM db_metadata WHERE key=?", (key, )).fetchone()
            return result[0] if result else None
        except:
            return None

    def set_metadata_value(self, key: str, value: str) -> None:
        
        self.conn.execute("INSERT OR REPLACE INTO db_metadata VALUES (?, ?)", (key, value))

    def get_processed_files(self) -> set[str]:
        """Returns a set of filenames that have already been imported."""
        try:
            res = self.conn.execute("SELECT filename FROM processed_files").fetchall()
            return {row[0] for row in res}
        except:
            return set()

    def wipe_database(self) -> None:
        """Clears all data but keeps the file structure."""
        try:
            self.conn.execute("DELETE FROM roms")
            self.conn.execute("DELETE FROM processed_files")
            self.conn.execute("DELETE FROM db_metadata")
            self.conn.execute("VACUUM")
        except Exception as error:
            print(f"Error wiping database: {error}")

    def insert_batch(self, buffer: List[Tuple]) -> None:
        """Inserts a batch of ROMs and marks their files as processed."""
        if not buffer:
            return
            
        # Insert ROM data
        self.conn.executemany("INSERT INTO roms VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", buffer)
        
        # Mark files as processed
        unique_files = {row[0] for row in buffer}
        for filename in unique_files:
            self.conn.execute("INSERT OR IGNORE INTO processed_files (filename) VALUES (?)", (filename, ))
            
    def export_to_parquet(self, parquet_path: str, threads: int = 1, status_callback: Callable[[str], None | None] = None) -> None:
        """
        Exports the current DuckDB database to a compressed Parquet file.
        
        Args:
            parquet_path (str): The destination path for the exported file.
            threads (int): Number of CPU threads to allocate for the operation.
            status_callback (Callable[str]]): Injected callback for real-time UI updates.
            
        Raises:
            FileNotFoundError: If the source database does not exist.
            duckdb.Error: If the database engine encounters an execution failure.
        """
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Source database not found: {self.db_path}")

        init_msg = f"Exporting database to Parquet: {parquet_path} (Threads: {threads})..."
        logging.info(init_msg)
        if status_callback is not None:
            status_callback(init_msg)
            
        start_time = time.time()
        
        # Let exceptions bubble up to the UI/CLI layer.
        conn = duckdb.connect(self.db_path)
        
        try:
            conn.execute(f"PRAGMA threads={threads}")
            conn.execute(f"COPY roms TO '{parquet_path}' (FORMAT PARQUET, COMPRESSION 'SNAPPY')")
        finally:
            conn.close()
            
        duration = time.time() - start_time
        success_msg = f"Export completed successfully in {duration:.2f}s."
        logging.info(success_msg)
        if status_callback:
            status_callback(success_msg)

    def import_from_parquet(self, parquet_path: str, threads: int = 1, status_callback: Callable[[str], None | None] = None) -> None:
        """
        Imports data from a Parquet file into the DuckDB database.
        
        Args:
            parquet_path (str): The source path of the Parquet file.
            threads (int): Number of CPU threads to allocate for the operation.
            status_callback (Optional[Callable]): Injected callback for real-time UI updates.
            
        Raises:
            FileNotFoundError: If the source Parquet file does not exist.
            duckdb.Error: If the database engine encounters an execution failure.
        """
        if not os.path.exists(parquet_path):
            raise FileNotFoundError(f"Source Parquet file not found: {parquet_path}")

        init_msg = f"Importing Parquet into database: {self.db_path} (Threads: {threads})..."
        logging.info(init_msg)
        if status_callback:
            status_callback(init_msg)

        count = 0            
        start_time = time.time()
        
        conn = duckdb.connect(self.db_path)
        try:
            self._setup_schema(target_conn=conn)
            conn.execute(f"PRAGMA threads={threads}")
            
            # Read Parquet and insert into the table
            conn.execute(f"INSERT INTO roms SELECT * FROM read_parquet('{parquet_path}')")
            
            # Gather execution statistics
            result = conn.execute("SELECT count(*) FROM roms").fetchone()
            if result and len(result) > 0:
                count = result[0]
            
        finally:
            conn.close()
            
        duration = time.time() - start_time
        success_msg = f"Import completed in {duration:.2f}s. Total Rows in DB: {count:,}"
        logging.info(success_msg)
        if status_callback:
            status_callback(success_msg)
    
    def import_from_parquet_folder(self, folder_path: str, status_callback: Callable[[str], None | None] = None) -> None:
        """
        Bulk imports all .parquet files from a designated directory into the main database table.
        Leverages DuckDB's native 'read_parquet' with glob wildcard support for maximum throughput.
        
        Args:
            folder_path (str): The target directory containing the fragmented Parquet files.
            status_callback (Optional[Callable]): Injected callback for real-time UI synchronization.
            
        Raises:
            FileNotFoundError: If the designated Parquet folder does not exist.
            duckdb.Error: If the database engine encounters an execution failure during the bulk insert.
        """
        if not os.path.exists(folder_path):
             raise FileNotFoundError(f"Parquet directory not found: {folder_path}")

        # Validate the presence of Parquet files to prevent DuckDB from throwing empty glob errors
        if not any(f.endswith(".parquet") for f in os.listdir(folder_path)):
            warn_msg = f"No .parquet files discovered in the target directory: {folder_path}"
            logging.warning(warn_msg)
            if status_callback:
                status_callback(warn_msg)
            return

        init_msg = f"DuckDB: Bulk importing chunks from {folder_path}/*.parquet ..."
        logging.info(init_msg)
        if status_callback:
            status_callback(init_msg)
        
        # Windows fix: When sending paths within SQL, it's always safer to use a '/'.
        safe_path = folder_path.replace('\\', '/')
        
        # DuckDB's glob (*) capability ensures it to retrieve thousands of files 
        # with a single SQL command without looping.
        query = f"INSERT INTO roms SELECT * FROM read_parquet('{safe_path}/*.parquet', union_by_name=True);"
        self.conn.execute(query)
            
        success_msg = "Bulk Parquet import completed successfully."
        logging.info(success_msg)
        if status_callback:
            status_callback(success_msg)
    
    def configure_threads(self, thread_count: int) -> None:
        """Sets the PRAGMA threads for DuckDB."""
        if thread_count > 0:
            self.conn.execute(f"PRAGMA threads={thread_count}")

    # Read Operations (GUI / Pagination Support)
    def get_total_count(self, filters: Dict[str, str] | None = None) -> int:
        
        query = "SELECT COUNT(*) FROM roms"
        params: List[Any] = []
        
        if filters:
            where_clause, filter_params = self._build_where_clause(filters)
            if where_clause:
                query += f" WHERE {where_clause}"
                params = filter_params
            
        try:
            result = self.conn.execute(query, params).fetchone()
            if result is not None and isinstance(result[0], int):
                return result[0]
            return 0
        
        except Exception as error:
            error_details = f"DB Count Failed: {str(error)}\nSQL: {query}\nParams: {params}"
            logging.error(error_details)
            raise RuntimeError(error_details) from error
        
    def fetch_page(self, limit: int, offset: int, filters: Dict[str, str] | None = None, sort_col: str | None  = None, sort_asc: bool = True) -> List[Tuple]:
        """Fetches a specific slice of data for the GUI."""
        query = "SELECT * FROM roms"
        params = []
        
        if filters:
            where_clause, filter_params = self._build_where_clause(filters)
            query += f" WHERE {where_clause}"
            params.extend(filter_params)
            
        if sort_col and sort_col in self._column_names:
            direction = "ASC" if sort_asc else "DESC"
            query += f" ORDER BY {sort_col} {direction}"
            
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        try:
            return self.conn.execute(query, params).fetchall()
        except Exception as error:
            error_details = f"DB Fetch Failed: {str(error)}\nSQL: {query}\nParams: {params}"
            logging.error(error_details)
            raise RuntimeError(error_details) from error
        
    def find_by_hash(self, file_hash: str, hash_type: str = "md5", platform: str | None = None) -> Tuple | None:
        """
        Searches for a game using its cryptographic hash (MD5, CRC, SHA1).
        Returns the record with a 1.0 (100%) match score if found.
        """
        # Validate hash_type to prevent SQL injection via column name
        valid_hashes = {"md5", "crc", "sha1"}
        if hash_type not in valid_hashes:
            raise ValueError(f"Invalid hash type: {hash_type}")

        query = f"SELECT rom_name, title, platform, category, release_year, description, size, md5, status, system, {hash_type} FROM roms WHERE {hash_type} = ?"
        params = [file_hash]

        if platform:
            query += " AND platform = ?"
            params.append(platform)

        result = None
        try:
            result = self.conn.execute(query, params).fetchone()
        except Exception as error:
            print(error)
        
        # If found, append a perfect score (1.0) to maintain consistency with fuzzy search
        return (*result, 1.0) if result else None

    def find_by_fuzzy_name(self, filename: str, platform: str | None = None, threshold: float = 0.6) -> Tuple | None:
        """
        Searches for a game using Jaro-Winkler string similarity on the game name.
        Returns the best match if the score is above the threshold.
        """
        # Clean the filename: remove extension and underscores
        clean_name = filename.rsplit('.', 1)[0].replace('_', ' ')

        query = "SELECT rom_name, title, platform, category, release_year, description, size, md5, status, system, jaro_winkler_similarity(game_name, ?) as score FROM roms WHERE score > ?"
        params = [clean_name, threshold]

        if platform:
            query += " AND platform = ?"
            params.append(platform)

        # Order by score descending to get the best match
        query += " ORDER BY score DESC LIMIT 1"

        result = self.conn.execute(query, params).fetchone()
        return result if result else None

    def resolve_game_match(self, filename: str, file_hash: str | None = None, hash_type: str = "md5", platform: str | None = None) -> TosecDat | None:
        "Tries to identify the game first by hash, then by fuzzy name."
        match = None

        # Attempt High-Precision Hash Match
        if file_hash:
            match = self.find_by_hash(file_hash, hash_type, platform)
            if not match:
                # Fallback to Fuzzy Name Match
                match = self.find_by_fuzzy_name(filename, platform)
                
        tosecDat = None
        if match:
            "rom_name, title, platform, category, release_year, description, size, md5, status, system"
            tosecDat = TosecDat(rom_name=match[0],
                                title=match[1],
                                platform=match[2],
                                category=match[3],
                                release_year=match[4],
                                description=match[5],
                                size=match[6],
                                md5=match[7],
                                status=match[8],
                                system=match[9])
        return tosecDat

    def _build_where_clause(self, filters: Dict[str, str]) -> Tuple[str, List[Any]]:
        """Constructs a safe SQL WHERE clause."""
        conditions = []
        params = []
        
        for col, val in filters.items():
            if not val:
                continue
            
            conditions.append(f"{col} ILIKE ?")
            params.append(f"%{val}%")
            
        return " AND ".join(conditions), params
        
    def _get_optimal_ram_limit(self, limit_str: str) -> str:
        """
        Calculates RAM limit using psutil (Modern, Active Method).
        """
        # Calculate if the user selected "auto" or entered a percentage.
        if limit_str == "auto":
            percentage = 75
        elif "%" in limit_str:
            try:
                percentage = int(limit_str.replace("%", ""))
            except:
                percentage = 75
        else:
            # If a value like "4GB" appears, do not touch it.
            return limit_str

        try:
            # Total RAM (in Bytes) using psutil
            total_ram = psutil.virtual_memory().total
            limit_bytes = int(total_ram * (percentage / 100))
            
            return f"{limit_bytes}B"
        
        except Exception as error:
            print(f"RAM detection failed ({error}), defaulting to 2GB.")
            return "2GB"

    def _get_optimal_ram_limit_native(self, limit_str: str) -> str:
        """Calculates 75% of total RAM in GB, working on both Windows and Linux."""
        if limit_str == "auto":
            limit_str = "75%"

        # If you already received a value like "16GB", return it directly.
        if "%" not in limit_str:
            return limit_str

        try:
            percent = int(limit_str.replace("%", "")) / 100.0
            total_ram_bytes = 0
            system = platform.system()
            # for Windows
            if system == "Windows":
                kernel32 = ctypes.windll.kernel32
                c_ulonglong = ctypes.c_ulonglong
                
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ('dwLength', ctypes.c_ulong),
                        ('dwMemoryLoad', ctypes.c_ulong),
                        ('ullTotalPhys', c_ulonglong),
                        ('ullAvailPhys', c_ulonglong),
                        ('ullTotalPageFile', c_ulonglong),
                        ('ullAvailPageFile', c_ulonglong),
                        ('ullTotalVirtual', c_ulonglong),
                        ('ullAvailVirtual', c_ulonglong),
                        ('ullAvailExtendedVirtual', c_ulonglong),
                    ]
                
                mem_status = MEMORYSTATUSEX()
                mem_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                kernel32.GlobalMemoryStatusEx(ctypes.byref(mem_status))
                total_ram_bytes = mem_status.ullTotalPhys

            # for Linux / Mac 
            else:
                if "SC_PAGE_SIZE" in os.sysconf_names and "SC_PHYS_PAGES" in os.sysconf_names:
                    total_ram_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
            
            if total_ram_bytes <= 0:
                return "4GB"

            limit_gb = int((total_ram_bytes * percent) / (1024**3))
            limit_gb = max(1, limit_gb)
            
            return f"{limit_gb}GB"

        except Exception as error:
            print(f"RAM detection failed ({error}), defaulting to 2GB.")
            return "2GB"
