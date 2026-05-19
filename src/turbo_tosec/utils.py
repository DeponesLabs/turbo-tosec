import os
import re
import subprocess
import platform
from types import TracebackType
from typing import List, Generator, Tuple, Callable
import hashlib
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
        
def get_dat_files(root_dir: str) -> List[str]:
    
    dat_files = []
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(".dat"):
                dat_files.append(os.path.join(root, file))
    return dat_files

def clean_path(path: str) -> str:
    """Normalizes paths for display (removes distinct drive letters if needed)."""
    return os.path.normpath(path)

def calculate_file_hash(filepath: str, hash_algorithm: str = "md5", chunk_size: int = 8192) -> str:
    """
    Calculates the hash of a file synchronously.
    Returns the hex digest string directly.
    """
    # Algorithm selection
    if hash_algorithm == "md5":
        hasher = hashlib.md5()
    elif hash_algorithm == "sha1":
        hasher = hashlib.sha1()
    else:
        raise ValueError(f"Unsupported hash algorithm: {hash_algorithm}")

    # No need to calculate file size or track processed bytes anymore
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
    except Exception as error:
        print(error)

    return hasher.hexdigest()

def calculate_file_hash_gen(filepath: str, hash_algorithm: str = "md5", chunk_size: int = 8192) -> Generator[Tuple[int, int], None, str]:
    """
    A generator-based hash calculator.
    
    Yields:
        (processed_bytes, total_bytes): Progress update.
    
    Returns:
        The final hash string (captured via StopIteration in low-level usage, 
        or simply by returning it if used as a generator).
        
    Note: To get the return value from a generator loop in Python, 
    one typically needs to store the state externally or use 'yield' 
    for the final result as well.
    """
    
    # Algorithm selection
    if hash_algorithm == "md5":
        hasher = hashlib.md5()
    elif hash_algorithm == "sha1":
        hasher = hashlib.sha1()
    else:
        raise ValueError(f"Unsupported hash algorithm: {hash_algorithm}")

    file_size = os.path.getsize(filepath)
    processed_bytes = 0

    with open(filepath, 'rb') as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
            processed_bytes += len(chunk)
            
            # Yield control back to the caller with progress info
            yield processed_bytes, file_size

    # The loop is done. The generator returns the final hash.
    return hasher.hexdigest()

def extract_tosec_version(directory_path: str) -> str:
    """
    Extracts the TOSEC version string from a given directory path using regular expressions.
    
    The expected pattern follows the standard TOSEC release naming convention,
    which typically resembles 'TOSEC-vYYYY-MM-DD' (e.g., 'TOSEC-v2023-08-15').
    
    Args:
        directory_path (str): The absolute or relative file system path to be evaluated.
        
    Returns:
        str: The extracted TOSEC version string. Returns 'Unknown' if the pattern is not found.
    """
    version_pattern = r"(TOSEC-v\d{4}-\d{2}-\d{2})"
    match = re.search(version_pattern, directory_path, re.IGNORECASE)
    
    if match:
        return match.group(1)
    return "Unknown"

def human_readable_size(size: int) -> str:
    
    try:
        s = float(size)
    except (ValueError, TypeError):
        return "0 B"
        
    for unit in ['B', 'KB', 'MB', 'GB']:
        if s < 1024.0:
            return f"{s:.2f} {unit}"
        s /= 1024.0
    return f"{s:.2f} TB"

def open_file_with_default_app(filepath: str) -> None:
    """Opens a file with the OS default application."""
    try:
        if platform.system() == 'Windows':
            os.startfile(filepath)
        elif platform.system() == 'Darwin': # macOS
            subprocess.call(('open', filepath))
        else: # Linux
            subprocess.call(('xdg-open', filepath))
    except Exception as error:
        print(f"\nCould not open log file automatically: {error}")
        
def check_system_resources(workers: int, db_threads: int) -> None:
    """
    Checks system limits and warns if the configuration might cause bottlenecks.
    """
    try:
        cpu_count = os.cpu_count() or 1
        total_requested_threads = workers * db_threads
        
        print(f"System Resources: {cpu_count} CPU Cores detected.")
        
        if total_requested_threads > cpu_count:
            print(f"WARNING: You requested {total_requested_threads} concurrent threads ({workers} workers x {db_threads} db_threads).")
            print(f"Your system only has {cpu_count} cores.")
            print("    -> This may cause 'Context Switching' overhead and SLOW DOWN the process.")
            print("    -> Recommendation: Keep (workers * db_threads) <= CPU Cores.")
        else:
            print(f"Configuration looks good: {total_requested_threads} threads <= {cpu_count} cores.")
            
    except Exception as e:
        print(f"Resource check skipped: {e}")