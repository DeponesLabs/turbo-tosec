from types import TracebackType
from typing import List, Generator, Tuple, Callable
import shutil
import tqdm

class Console:
    """
    Old-school ASCII styling for CLI output.
    Design Philosophy: "No Emojis. Just Data."
    """
    # ANSI Colors
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Symbols
    SYM_INFO = "[*]"
    SYM_PLUS = "[+]"
    SYM_WARN = "[!]"
    SYM_FAIL = "[X]"
    SYM_TIME = "[T]"

    @staticmethod
    def banner() -> None:
        """Prints the system banner."""
        # Width calculation for centering
        cols, _ = shutil.get_terminal_size((80, 20))
        
        logo = rf"""{Console.OKBLUE}{Console.BOLD}
   ______            __               ______
  /_  __/_  ______  / /_  ____       /_  __/___  ________  _____
   / / / / / / __ \/ __ \/ __ \_______/ / / __ \/ ___/ _ \/ ___/
  / / / /_/ / /   / /_/ / /_/ /_____// / / /_/ (__  )  __/ /__
 /_/  \__,_/_/   /_.___/\____/      /_/  \____/____/\___/\___/
        {Console.ENDC}"""
        print(logo)
        print(f"{Console.OKCYAN}{':: HIGH-PERFORMANCE DATA INGESTION ENGINE ::'.center(cols)}{Console.ENDC}")
        print(f"{Console.OKCYAN}{':: DEPONES LABS ::'.center(cols)}{Console.ENDC}\n")

    @staticmethod
    def section(title: str) -> None:
        """Draws a section header line."""
        cols, _ = shutil.get_terminal_size((80, 20))
        print(f"\n{Console.BOLD}{Console.HEADER}{title.upper()}{Console.ENDC}")
        print(f"{Console.HEADER}{'=' * cols}{Console.ENDC}")

    @staticmethod
    def info(msg: str, indent: int = 0) -> None:
        """Standard info log."""
        prefix = " " * indent + Console.SYM_INFO
        print(f"{Console.OKBLUE}{prefix} {msg}{Console.ENDC}")

    @staticmethod
    def success(msg: str, indent: int = 0) -> None:
        """Success operation log."""
        prefix = " " * indent + Console.SYM_PLUS
        print(f"{Console.OKGREEN}{prefix} {msg}{Console.ENDC}")

    @staticmethod
    def warning(msg: str) -> None:
        """Warning log."""
        print(f"{Console.WARNING}{Console.SYM_WARN} {msg}{Console.ENDC}")

    @staticmethod
    def error(msg: str) -> None:
        """Critical error log."""
        print(f"{Console.FAIL}{Console.SYM_FAIL} {msg}{Console.ENDC}")
        
    @staticmethod
    def perf(msg: str) -> None:
        """Performance metrics log."""
        print(f"{Console.OKCYAN}{Console.SYM_TIME} {msg}{Console.ENDC}")

class UniversalProgress:
    """
    A wrapper that abstracts progress reporting.
    If a 'callback' is provided (GUI mode), it invokes the callback.
    If no callback is provided (CLI mode), it uses 'tqdm' for console output.
    """
    def __init__(self, total: int, initial: int = 0, desc: str = "", unit: str = 'B', callback: Callable[[int, int], None] | None = None) -> None:
        
        self.callback: Callable[[int, int], None] | None = callback
        self.total: int = total
        self.current: int = initial
        self.console_bar: tqdm.tqdm = None
        
        if not self.callback:
            # CLI Mode: Initialize tqdm
            self.console_bar = tqdm(total=total, initial=initial, unit=unit, unit_scale=True, unit_divisor=1024, desc=desc)

    def update(self, n: int) -> None:
        
        self.current += n
        if self.console_bar:
            self.console_bar.update(n)
        elif self.callback:
            # GUI Mode: Send (current, total)
            # The GUI will take these values ​​and set the progress bar.
            self.callback(self.current, self.total)

    def set_postfix(self, stats: dict[str, int]) -> None:
        
        if self.console_bar:
            self.console_bar.set_postfix(stats)
        elif self.callback:
            # Optional: This can be expanded if the GUI callback accepts a third parameter (stats). 
            # # For now, only percentages are sent to the GUI.
            pass

    def close(self) -> None:
        
        if self.console_bar:
            self.console_bar.close()

    def __enter__(self) -> "UniversalProgress": 
        
        return self
    
    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        
        self.close()
