import os
import re
from typing import List, Tuple, Callable, Dict, Any
import threading
import concurrent.futures
import time
import shutil
from pathlib import Path
import logging
import multiprocessing
import gc
import pyarrow as pa
import xml.etree.ElementTree as ET

from turbo_tosec.database import DatabaseManager
from turbo_tosec.parser import TurboParser
from turbo_tosec.state import IngestionStateEvaluator, IngestionActionPlan
from turbo_tosec.domain import TosecNamingService

def worker_parse_task(filepath: str) -> List[Tuple]:
    """
    Worker for InMemoryMode: Parses XML completely into RAM (and returns list of tuples).
    """
    parser = TurboParser()
    return parser.parse(filepath)

def worker_staged_task(filepath: str, temp_dir: str) -> dict:
    """
    Worker for StagedMode: Parses XML and writes chunks to intermediate Parquet files.
    """
    try:
        parser = TurboParser()
        result_stats = parser.parse_and_save_chunks(filepath, temp_dir)
        return result_stats
    except Exception as error:
        raise RuntimeError(f"Error in {os.path.basename(filepath)}: {error}")

class ImportSession:
    """
    Manages the ingestion workflow for TOSEC DAT files.
    Encapsulates file discovery, parsing, and database insertion strategies.
    """
    def __init__(self, db_manager: DatabaseManager, workers: int = 0, temp_dir: str = "temp_chunks", batch_size: int = 1000):
        """
        Initializes the import session with the necessary configuration and dependencies.
        
        Args:
            db_manager (DatabaseManager): An active DatabaseManager instance injected by the caller.
            workers (int): Number of CPU workers for parallel processing. Defaults to 0 (auto-detect).
            temp_dir (str): Directory path for staging temporary parquet chunks.
            batch_size (int): Threshold for flushing memory buffer to the database.
        
        Raises:
            ValueError: If neither db_manager nor db_path is provided.
        """
        self.db: DatabaseManager = db_manager
        self.temp_dir: str = temp_dir
        self.batch_size: int = batch_size
        
        # Internal State Management
        self.buffer: List[Tuple[Any, ...]] = []
        self.total_roms: int = 0
        self.error_count: int = 0
        self.stop_monitor = threading.Event()
        self.executor: concurrent.futures.ProcessPoolExecutor | None = None # To track active executor for cleanup
        
        # Hardware Resource Resolution
        max_cpu = multiprocessing.cpu_count()
        self.workers = workers if 0 < workers <= max_cpu else max_cpu
        
    def _discover_files(self, source_path: str, filters: List[str] | None = None) -> List[str]:
        """
        Internally scans the directory for DAT files with optional pattern filtering.
        
        Args:
            source_path (str): Root directory for scanning.
            filters (Optional[List[str]]): List of keywords to include (e.g., ['Amiga', 'Commodore']).
            
        Returns:
            List[str]: List of resolved absolute file paths.
        """
        discovered = []
        for root, _, files in os.walk(source_path):
            for f in files:
                if not f.lower().endswith(".dat"):
                    continue
                
                # Apply optional filtering logic
                if filters and not any(f.lower() in f.lower() for f in filters):
                    continue
                    
                discovered.append(os.path.join(root, f))
                
        return discovered
    
    def ingest(self, source_path: str, mode: str = 'direct', resume: bool = False, force_new: bool = False, filters: List[str] | None = None, 
               progress_callback: Callable[[int, int], None] | None = None,
               status_callback: Callable[[str], None] | None = None) -> Dict[str, int]:
        """
        Executes the high-level ingestion pipeline, managing database state autonomously.
        
        Args:
            source_path (str): The root directory containing TOSEC DAT metadata files.
            mode (str): Execution strategy ('direct', 'staged', or 'legacy').
            resume (bool): Instructs the engine to skip previously processed files.
            force_new (bool): Instructs the engine to wipe the existing database prior to ingestion.
            filters (Optional[List[str]]): Keywords to filter DAT files.
            progress_callback (Optional[Callable]): Callback mechanism for UI thread synchronization.
            
        Returns:
            Dict[str, int]: Aggregated ingestion statistics including total ROMs and errors.
        """
        all_files = self._discover_files(source_path, filters=filters)
        if not all_files:
            return {'total_roms': 0, 'errors': 0}
        
        input_version = TosecNamingService.extract_version(source_path)
        db_version = self.db.get_metadata_value('tosec_version')
        
        plan = self._evaluate_state(all_files, input_version, db_version, resume, force_new)
        
        files_to_process = self._apply_state(plan)
        if not files_to_process:
            return {'total_roms': 0, 'errors': 0}
        
        self._dispatch_execution(files_to_process, mode, progress_callback, status_callback)
        
        return {'total_roms': self.total_roms, 'errors': self.error_count}
    
    def _evaluate_state(self, all_files: List[str], input_version: str, db_version: str | None, resume: bool, force_new: bool) -> IngestionActionPlan:
        """
        Analyzes the current database state against the incoming dataset to formulate an execution plan.
        This method is strictly read-only and produces no database side effects.
        """
        # Fetch the existing processed files from the database. 
        # If the database is empty or new, default to an empty set.
        processed_set = self.db.get_processed_files() or set()
        
        evaluator = IngestionStateEvaluator()
        
        # The Evaluator internally decides everything, including new_version_to_write
        plan = evaluator.evaluate(all_discovered_files=all_files, processed_files=processed_set, current_db_version=db_version,
                                  input_version=input_version, resume_requested=resume, force_new_requested=force_new)
        return plan
        
    def _apply_state(self, plan: IngestionActionPlan) -> List[str]:
        """
        Executes the structural directives dictated by the evaluation plan.
        Acts as a strict mutator with zero decision-making logic.
        """
        if plan.wipe_required:
            self.db.wipe_database()
            
        if plan.new_version_to_write:
            self.db.set_metadata_value('tosec_version', plan.new_version_to_write)
            
        return plan.pending_files
    
    def _dispatch_execution(self, files_to_process: List[str], mode: str, 
                            progress_callback: Callable[[int, int], None] | None = None,
                            status_callback: Callable[[str], None] | None = None) -> None:
        """
        Routes the ingestion workload to the specified processing strategy 
        and guarantees resource cleanup upon completion or failure.
        """
        self.total_roms = 0
        self.error_count = 0
        
        total_bytes = sum(os.path.getsize(f) for f in files_to_process)
        
        if mode == 'staged':
            self._prepare_temp_dir()

        try:
            if mode == 'direct':
                self._run_direct_mode(files_to_process, total_bytes, 0, progress_callback, status_callback)
            elif mode == 'staged':
                self._run_staged_mode(files_to_process, self.workers, total_bytes, 0, progress_callback, status_callback)
            elif mode == 'legacy':
                self._run_in_memory_mode(files_to_process, self.workers, total_bytes, 0, progress_callback, status_callback)
            else:
                raise ValueError(f"Unsupported ingestion mode requested: {mode}")
        finally:
            # Ensures temp files are purged even if a VersionMismatchError or system crash occurs
            if mode == 'staged' and os.path.exists(self.temp_dir): 
                shutil.rmtree(self.temp_dir)
                
    # Strategy: In-memory
    def _run_in_memory_mode(self, files: List[str], workers: int, total_bytes: int, initial_bytes: int, 
                            progress_callback: Callable[[int, int], None] | None = None,
                            status_callback: Callable[[str], None] | None = None) -> None:
        """
        Legacy In-Memory Mode: Parses XML entirely into RAM before batch inserting.
        100% UI/CLI Agnostic.
        """
        init_msg = f"Initiating In-Memory Mode ingestion with {workers} workers..."
        logging.info(init_msg)
        if status_callback:
            status_callback(init_msg)

        if workers < 2:
            self._run_serial(files, total_bytes, initial_bytes, progress_callback, status_callback)
        else:
            self._run_parallel(files, workers, total_bytes, initial_bytes, progress_callback, status_callback)
        
        self._flush_buffer() # Write any remaining data

    # Strategy: Staged 
    def _run_staged_mode(self, files: List[str], workers: int, total_bytes: int, initial_bytes: int, 
                         progress_callback: Callable[[int, int], None] | None = None,
                         status_callback: Callable[[str], None] | None = None) -> None:
        
        """
        Staged Mode: Parses XML and writes chunks to intermediate Parquet files before bulk importing.
        100% UI/CLI Agnostic. Relies strictly on callbacks for state reporting.
        """
        current_bytes = initial_bytes
        
        init_msg = f"Initiating Staged Mode ingestion with {workers} parallel workers..."
        logging.info(init_msg)
        if status_callback:
            status_callback(init_msg)

        executor = concurrent.futures.ProcessPoolExecutor(max_workers=workers)
        
        try:
            self.executor = executor
            # Call Staging worker
            future_to_file = {
                executor.submit(worker_staged_task, f, self.temp_dir): f for f in files
            }
            
            for future in concurrent.futures.as_completed(future_to_file):
                filepath = future_to_file[future]
                try:
                    stats = future.result() # Return as Dict: {'roms': 500, 'size': 1024, 'skipped': False}
                    
                    # Check Skipped Files (for Legacy CMP files)
                    if stats.get("skipped"):
                        skip_msg = f"Skipped: {stats.get('file')} ({stats.get('reason')})"
                        logging.info(skip_msg)
                        if status_callback:
                            status_callback(skip_msg)
                            
                        # Advance progress even if skipped
                        try:
                            current_bytes += os.path.getsize(filepath)
                        except OSError:
                            pass
                            
                        if progress_callback:
                            progress_callback(current_bytes, total_bytes)
                        continue
                    
                    # Update stats
                    self.total_roms += stats.get('roms', 0)
                    
                    # Update Progress-bar 
                    try:
                        current_bytes += os.path.getsize(filepath)
                    except OSError:
                        pass

                    if progress_callback:
                        progress_callback(current_bytes, total_bytes)

                except Exception as error:
                    self._handle_error(error, filepath, status_callback)
        finally:
            if self.executor is not None:
                self.executor.shutdown(wait=True)
                self.executor = None
                
            import gc
            gc.collect()

        # Bulk Import into DuckDB
        if self.total_roms > 0:
            import_msg = f"Bulk loading Parquet fragments from staging area: {self.temp_dir}..."
            logging.info(import_msg)
            if status_callback:
                status_callback(import_msg)
                
            # We already updated this method earlier to bubble up exceptions and accept a status_callback!
            self.db.import_from_parquet_folder(self.temp_dir, status_callback=status_callback)
            
        else:
            warn_msg = "No compatible ROM entries discovered to import."
            logging.warning(warn_msg)
            if status_callback:
                status_callback(warn_msg)

    # Strategy: Direct Mode
    def _run_direct_mode(self, files: List[str], total_bytes: int, initial_bytes: int, 
                         progress_callback: Callable[[int, int], None] | None = None, 
                         status_callback: Callable[[str], None] | None = None) -> None:
        """
        Parses XML stream and injects directly into DuckDB via Arrow.
        100% UI/CLI Agnostic.
        """
        parser = TurboParser()
        current_bytes = initial_bytes
    
        logging.info("Initiating Direct Mode ingestion...")
        if status_callback:
            status_callback("Initiating Direct Mode ingestion...")

        for filepath in files:
            try:
                arrow_stream = parser.parse_to_arrow_stream(filepath=filepath, chunk_size=50000)
                for arrow_batch in arrow_stream:
                    self.db.conn.execute("INSERT INTO roms SELECT * FROM arrow_batch")
                    self.total_roms += arrow_batch.num_rows

                # Advance progress
                try:
                    current_bytes += os.path.getsize(filepath)
                except OSError:
                    pass
                
                # Emit raw data back to the caller (UI or CLI)
                if progress_callback:
                    progress_callback(current_bytes, total_bytes)

            except Exception as error:
                self._handle_error(error, filepath, status_callback)

    def _flush_buffer(self) -> None:
        
        if self.buffer:
            self.db.insert_batch(self.buffer)
            self.total_roms += len(self.buffer)
            self.buffer.clear()

    def _run_serial(self, files: List[str], total_bytes: int, initial_bytes: int, 
                    progress_callback: Callable[[int, int], None] | None,
                    status_callback: Callable[[str], None] | None) -> None:
        
        parser = TurboParser()
        current_bytes = initial_bytes
        
        for filepath in files:
            try:
                data = parser.parse(filepath)
                self._process_result(data)
                
                try:
                    current_bytes += os.path.getsize(filepath)
                except OSError:
                    pass
                    
                if progress_callback:
                    progress_callback(current_bytes, total_bytes)
                    
            except Exception as error:
                self._handle_error(error, filepath, status_callback)

    def _run_parallel(self, files: List[str], workers: int, total_bytes: int, initial_bytes: int, 
                      progress_callback: Callable[[int, int], None] | None = None,
                      status_callback: Callable[[str], None] | None = None) -> None:
        
        current_bytes = initial_bytes
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
            future_to_file = {executor.submit(worker_parse_task, f): f for f in files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                filepath = future_to_file[future]
                try:
                    data = future.result()
                    self._process_result(data)
                    
                    try:
                        current_bytes += os.path.getsize(filepath)
                    except OSError:
                        pass
                        
                    if progress_callback:
                        progress_callback(current_bytes, total_bytes)
                        
                except Exception as error:
                    self._handle_error(error, filepath, status_callback)
                    
    def _process_result(self, data: List[Tuple]) -> None:
        """
        Appends parsed data tuples to the memory buffer and flushes to DuckDB 
        when the configured batch size threshold is met.
        """
        if data:
            self.buffer.extend(data)
            if len(self.buffer) >= self.batch_size:
                self._flush_buffer()

    def _prepare_temp_dir(self) -> None:
        """Cleans or creates the temporary staging directory for Parquet chunks."""
        p = Path(self.temp_dir)
        if p.exists():
            try:
                shutil.rmtree(p)
            except Exception as error:
                logging.warning(f"Could not clean temp dir {p}: {error}")
                
        p.mkdir(parents=True, exist_ok=True)

    def _handle_error(self, error: Exception, filepath: str, 
                      status_callback: Callable[[str], None] | None = None) -> None:
        """
        Centralized error handling for ingestion tasks. 
        Bubbles up critical hardware faults while logging standard parsing errors.
        """
        error_msg = str(error).lower()
        if "not enough space" in error_msg or "read-only file system" in error_msg:
             raise OSError("CRITICAL: Disk is full or not writable!") from error
             
        self.error_count += 1
        
        fail_msg = f"Failed: {os.path.basename(filepath)} -> {error}"
        logging.error(fail_msg)
        
        if status_callback:
            status_callback(f"Error skipping file: {os.path.basename(filepath)}")
