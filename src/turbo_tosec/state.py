import os
from dataclasses import dataclass
from typing import List, Set, Optional

@dataclass
class IngestionActionPlan:
    """
    Data transfer object representing the execution strategy determined by the state evaluator.
    """
    wipe_required: bool
    files_to_process: List[str]
    error_message: Optional[str] = None

class IngestionStateEvaluator:
    """
    Evaluates the current state of the database against the incoming dataset to determine
    the appropriate ingestion strategy (resume, wipe, or abort on conflict).
    """

    def evaluate(self, all_discovered_files: List[str], processed_files: Set[str], current_db_version: Optional[str], 
                 input_version: str, resume_requested: bool, force_new_requested: bool) -> IngestionActionPlan:
        """
        Calculates the operational delta and resolves configuration conflicts.
        
        Args:
            all_discovered_files (List[str]): Absolute paths of all DAT files in the source.
            processed_files (Set[str]): Basenames of files already committed to the database.
            current_db_version (Optional[str]): The TOSEC version currently tracked by the DB.
            input_version (str): The TOSEC version detected from the input directory.
            resume_requested (bool): Flag indicating user intent to bypass processed files.
            force_new_requested (bool): Flag indicating user intent to overwrite the existing DB.
            
        Returns:
            IngestionActionPlan: The formulated strategy for the ingestion engine.
        """
        # Version Conflict Resolution
        if current_db_version and current_db_version != input_version:
            if force_new_requested:
                return IngestionActionPlan(wipe_required=True, files_to_process=all_discovered_files)
            else:
                error_msg = (
                    f"Version Mismatch Detected. Database contains '{current_db_version}', "
                    f"but input is '{input_version}'. Use '--force-new' to overwrite."
                )
                return IngestionActionPlan(wipe_required=False, files_to_process=[], error_message=error_msg)

        # Fresh Start / Force Wipe
        if force_new_requested or not processed_files:
            return IngestionActionPlan(wipe_required=force_new_requested, files_to_process=all_discovered_files)

        # Delta Calculation for Resume
        if resume_requested:
            pending_files = [f for f in all_discovered_files if os.path.basename(f) not in processed_files]
            return IngestionActionPlan(wipe_required=False, files_to_process=pending_files)

        # Ambiguous State (Existing data found, but no explicit instruction)
        error_msg = (
            f"Database already contains {len(processed_files)} processed files. "
            "Explicitly provide 'resume=True' to continue or 'force_new=True' to wipe."
        )
        return IngestionActionPlan(wipe_required=False, files_to_process=[], error_message=error_msg)
