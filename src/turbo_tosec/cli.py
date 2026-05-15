import os
import re
import sys
from datetime import datetime
import time
import argparse
import logging
import subprocess
import platform
from multiprocessing import freeze_support

from tqdm import tqdm 

from turbo_tosec.database import DatabaseManager, DBConfig
from turbo_tosec.session import ImportSession
from turbo_tosec.exceptions import ConflictingFlagsError, VersionMismatchError, TurboTosecBaseError
from turbo_tosec._version import __version__
from turbo_tosec.utils import UniversalProgress, Console, open_file_with_default_app, check_system_resources

class CLICallbackHandler:
    """
    Encapsulates CLI presentation state to provide clean, isolated callback hooks.
    Strictly prevents the use of nested inner functions.
    """
    def __init__(self, pbar: UniversalProgress | None = None, session: ImportSession | None = None):
        
        self.pbar = pbar
        self.session = session

    def update_progress(self, current_bytes: int, total_bytes: int) -> None:
        """Translates raw engine byte metrics into CLI progress bar updates."""
        if self.pbar and self.pbar.console_bar:
            if self.pbar.console_bar.total != total_bytes:
                self.pbar.console_bar.total = total_bytes
                
            self.pbar.current = current_bytes
            self.pbar.console_bar.n = current_bytes
            self.pbar.console_bar.refresh()
            
            if self.session:
                self.pbar.set_postfix({"ROMs": self.session.total_roms, "Errors": self.session.error_count})

    @staticmethod
    def write_above_bar(msg: str) -> None:
        """Safely writes engine status updates above an active tqdm progress bar."""
        tqdm.write(f"{Console.SYM_INFO} {msg}")

    @staticmethod
    def write_standard(msg: str) -> None:
        """Standard console output for modes without an active progress bar."""
        Console.info(msg)
        
def setup_logging(log_file: str):
   
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(level=logging.ERROR, 
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[logging.FileHandler(log_file, mode='w', encoding='utf-8')]
    )

def run_scan_mode(args, log_filename: str):
    
    setup_logging(log_filename)
    check_system_resources(args.workers, args.db_threads)

    # Determine ingestion mode based on flags
    mode = 'legacy'
    if args.direct:
        mode = 'direct'
    elif args.staged:
        mode = 'staged'
    
    db_config = DBConfig(turbo=(args.workers > 1), memory=args.db_memory, threads=args.db_threads)
    
    with DatabaseManager(args.output, config=db_config) as db:
        db.configure_threads(args.workers)
        
        # Inject the arguments into the domain engine
        session = ImportSession(db_manager=db, workers=args.workers, temp_dir=args.temp_dir, batch_size=args.batch_size)
        Console.info(f"\nInitializing ingestion sequence for: {args.input}")
        start_time = time.time()
        
        with UniversalProgress(total=0, desc="Ingesting DATs") as pbar:
            # Instantiate the Handler instead of nested functions
            handler = CLICallbackHandler(pbar=pbar, session=session)

            stats = session.ingest(source_path=args.input, mode=mode, resume=args.resume, force_new=args.force_new,
                                   progress_callback=handler.update_progress, status_callback=handler.write_above_bar)
    end_time = time.time()
    duration = end_time - start_time
    
    print("\nTransaction completed!")
    print(f"Database: {args.output}")
    print(f"Total ROMs: {stats.get('total_roms', 0):,}")
    print(f"Elapsed Time: {duration:.2f}s")
    
    if stats.get('errors', 0) > 0:
        print(f"\nWARNING: {stats.get('errors', 0)} files failed.")
        if args.open_log: 
            open_file_with_default_app(log_filename)
    else:
        logging.shutdown()
        if os.path.exists(log_filename): 
            try: 
                os.remove(log_filename)
            except OSError: 
                pass
        Console.success("Clean import.")

def run_parquet_mode(args):
    """Handles Parquet import/export operations."""
    # Instantiate an empty handler for static methods
    handler = CLICallbackHandler()
    
    with DatabaseManager(args.db) as db:
        if args.export_file:
            db.export_to_parquet(args.export_file, args.workers, status_callback=handler.write_standard)
        elif args.import_file:
            db.import_from_parquet(args.import_file, args.workers, status_callback=handler.write_standard)

def main():
    
    # If no subcommand given, and not asking for help/version, add 'scan' as default command.
    if len(sys.argv) > 1 and sys.argv[1] not in ['scan', 'parquet', '--help', '-h', '--version', '-v', '--about']:
        sys.argv.insert(1, 'scan')    
    
    parser = argparse.ArgumentParser(description="High-performance TOSEC DAT importer using DuckDB.")
    
    ''' Global arguments (may apply to all commands) '''
    # About & Version
    parser.add_argument("--about", action="store_true", help="Show program information, philosophy, and safety defaults.")
    parser.add_argument("--version", "-v", action="version", version=f"{__version__}")

    # Sub-commands for different modes
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scan Command (Main Mode)
    parser_scan = subparsers.add_parser("scan", help="Scan DAT files and import to DB (Default mode).")
    parser_scan.add_argument("--input", "-i", required=True, help="The main directory path where the TOSEC DAT files are located.")
    parser_scan.add_argument("--output", "-o", default="tosec.duckdb", help="Name/path of the DuckDB file to be created.")
    parser_scan.add_argument("--workers", "-w", type=int, default=1, help="Number of worker threads (Default: 1). Tip: Use 0 to auto-detect CPU count.")
    parser_scan.add_argument("--batch-size", "-b", type=int, default=1000, help="Number of rows to insert per batch transaction (Default: 1000).")
    
    # Strategy Selection, Mutually Exclusive Group
    strategy_group = parser_scan.add_mutually_exclusive_group()
    
    strategy_group.add_argument("--staged", action="store_true", help="[Strategy] Staged Mode (Batch/ETL). XML -> Parquet (Disk) -> DB. Safest for huge sets, supports checkpoints.")
    strategy_group.add_argument("--direct", action="store_true", help="[Strategy] Direct Mode (Stream). XML -> Arrow (RAM) -> DB. Zero-Copy ingestion. Fastest.")
    strategy_group.add_argument("--legacy", action="store_true", help="[Strategy] In-Memory Mode (Old). XML -> DOM (RAM). High memory usage. Deprecated.")

    parser_scan.add_argument("--temp-dir", default="temp_chunks", help="Directory for temporary chunk files (used in --staged mode).")
    
    # Flags
    parser_scan.add_argument("--no-open-log", action="store_false", dest="open_log", default=True, help="Do NOT automatically open the log file if errors occur.")
    
    # Resume or New, Mutually Exclusive Group
    state_group = parser_scan.add_mutually_exclusive_group()
    state_group.add_argument("--resume", action="store_true", help="Automatically resume if database exists.")
    state_group.add_argument("--force-new", action="store_true", help="Force overwrite existing database.")
 
    # Parquet Command (Import/Export)
    parser_parquet = subparsers.add_parser("parquet", help="Import/Export data using Parquet files.")
    parser_parquet.add_argument("--db", "-d", default="tosec.duckdb", help="Target/Source DuckDB file.")
    parser_parquet.add_argument("--workers", "-w", type=int, default=1, help="Max threads for DuckDB engine (Default: 1).")
    group = parser_parquet.add_mutually_exclusive_group(required=True)
    group.add_argument("--import-file", "-i", help="Import FROM this Parquet file.")
    group.add_argument("--export-file", "-o", help="Export TO this Parquet file.")
    
    # Advanced Performance Tuning
    parser.add_argument("--db-memory", type=str, default="75%", help="DuckDB memory limit (e.g., '8GB', '75%%'). Default: 75%% of RAM.")
    parser.add_argument("--db-threads", type=int, default=1, help="DuckDB threads per worker process. Default: 1 (Best for bulk insert).")
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()
        
    if args.about:
        print(f"""
 *** turbo-tosec v{__version__} ***
 A high-performance, DuckDB-based importer for TOSEC DAT collections.

  INGESTION STRATEGIES (NEW v1.3)
 ------------------------------------
 1. InMemory (Standard):
    - Default mode. Reads XML into Python objects. 
    - Good for small sets or validation.

 2. Staged (--staged):
    - Replaces old "Streaming" mode.
    - Writes Parquet checkpoints to disk before loading.
    - Robust, resumable, uses less RAM.

 3. Direct (--direct):
    - The "Speedster". Reads XML stream directly into Arrow Tables.
    - Zero-Copy transfer to DuckDB. 
    - Minimal Disk I/O.
 
 USAGE EXAMPLES
 ---------------------------
 $ turbo-tosec scan -i "./dats" --direct
 $ turbo-tosec scan -i "./dats" --staged -w 4
 $ turbo-tosec parquet -o "backup.parquet"

 ---------------------------
 Author:  Depones Labs
 License: GPL v3 (Open Source)
 GitHub:  https://github.com/deponeslabs/turbo-tosec
""")
        return
    
    log_filename = None
    
    try:
        if args.command == "parquet":
            run_parquet_mode(args)
            
        elif args.command == "scan":
            if args.workers > 4:
                print(f"  WARNING: Using {args.workers} threads.")
                print("   If you are using a mechanical HDD, performance may drop due to seek time.")
                print("   Recommended for HDD: 1-4 threads. Recommended for SSD: 4-16 threads.")
            if not args.input:
                parser.error("the following arguments are required: --input/-i")
                
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            os.makedirs("logs", exist_ok=True)
            log_filename = os.path.join("logs", f"tosec_import_log_{timestamp}.log")
            
            run_scan_mode(args, log_filename)
            
    except KeyboardInterrupt:
        print("\n  Process interrupted by user.")
        return
    
    except ConflictingFlagsError as conflict_err:
        print(f"\n  [CONFIGURATION ERROR] {conflict_err}")
        print("  Tip: Remove either --resume or --force-new from your command.")
        sys.exit(1)
        
    except VersionMismatchError as version_err:
        print(f"\n  [VERSION CONFLICT] {version_err}")
        print("  Tip: If you wish to proceed and delete the old data, append --force-new to your command.")
        sys.exit(1)
        
    except TurboTosecBaseError as base_err:
        print(f"\n  [ENGINE ERROR] {base_err}")
        sys.exit(1)
    
    except Exception as error:
        logging.critical(f"FATAL ERROR: {str(error)}", exc_info=True)
        error_msg = str(error)
        
        print(f"\n  Critical Error: {error}")
        print("=" * 60)
        
        if isinstance(error, OSError) and "Disk is full" in error_msg:
            print("Error: Disk Storage Full")
            if getattr(args, 'staged', False):
                print("Tip: --staged mode uses disk space for temp files. Check --temp-dir drive.")
        elif isinstance(error, (RuntimeError, MemoryError)):
            print("Error: System Resources Exhausted")
            if not getattr(args, 'staged', False):
                print("Tip: System ran out of RAM. Try using '--staged' mode to offload to disk.")
        else:
            print("Tip: Check the log file for technical details.")
        
        print("-" * 60)
        logging.shutdown()
            
        if getattr(args, 'open_log', False) and log_filename:
            print(f"Opening log file: {log_filename}")
            try:
                open_file_with_default_app(log_filename)
            except Exception as open_err:
                print(f"Could not open log file automatically: {open_err}")
        elif log_filename:
            print(f"Log file saved to: {os.path.abspath(log_filename)}")
            
        sys.exit(1)
        
if __name__ == "__main__":
    freeze_support() # Missing freeze_support() causes "arguments required" loop
    main()
