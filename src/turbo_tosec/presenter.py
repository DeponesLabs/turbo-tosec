from typing import Optional
from tqdm import tqdm

from turbo_tosec.terminal import UniversalProgress, Console
from turbo_tosec.session import ImportSession

class CLIPresenter:
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
