# tests/test_state.py
import pytest
from turbo_tosec.state import IngestionStateEvaluator, IngestionActionPlan
from turbo_tosec.exceptions import ConflictingFlagsError, VersionMismatchError, TurboTosecBaseError

class TestIngestionStateEvaluator:
    
    def setup_method(self):
        """Creates a fresh evaluator for every test."""
        self.evaluator = IngestionStateEvaluator()

    def test_conflicting_flags_raises_error(self):
        """Proves the engine fails fast if the user asks to both resume AND wipe."""
        with pytest.raises(ConflictingFlagsError):
            self.evaluator.evaluate(
                all_discovered_files=["game.dat"],
                processed_files=set(),
                current_db_version="TOSEC-v1",
                input_version="TOSEC-v1",
                resume_requested=True,     # TRUE
                force_new_requested=True   # TRUE (Conflict!)
            )

    def test_version_mismatch_raises_error(self):
        """Proves the engine refuses to ingest if versions do not match (without force)."""
        with pytest.raises(VersionMismatchError):
            self.evaluator.evaluate(
                all_discovered_files=["game.dat"],
                processed_files=set(),
                current_db_version="TOSEC-v1990",  # DB is old
                input_version="TOSEC-v2024",       # Input is new
                resume_requested=False,
                force_new_requested=False          # Didn't authorize a wipe
            )

    def test_force_new_action_plan(self):
        """Proves that 'force_new' schedules a wipe and processes ALL files."""
        plan = self.evaluator.evaluate(
            all_discovered_files=["f1.dat", "f2.dat"],
            processed_files={"f1.dat"},  # One file was already processed
            current_db_version="TOSEC-v1",
            input_version="TOSEC-v2",
            resume_requested=False,
            force_new_requested=True     # Force wipe requested!
        )
        
        assert isinstance(plan, IngestionActionPlan)
        assert plan.wipe_required is True
        assert plan.new_version_to_write == "TOSEC-v2"
        assert len(plan.pending_files) == 2  # It should process everything again

    def test_resume_action_plan(self):
        """Proves that 'resume' skips already processed files and does NOT wipe."""
        plan = self.evaluator.evaluate(
            all_discovered_files=["f1.dat", "f2.dat", "f3.dat"],
            processed_files={"f1.dat", "f2.dat"}, # Two files already processed
            current_db_version="TOSEC-v1",
            input_version="TOSEC-v1",
            resume_requested=True,       # Resume requested!
            force_new_requested=False
        )
        
        assert plan.wipe_required is False
        assert plan.new_version_to_write is None # Don't overwrite the version on a resume
        assert len(plan.pending_files) == 1   # Only f3.dat should be left
        assert plan.pending_files[0] == "f3.dat"
