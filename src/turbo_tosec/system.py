import os
import subprocess
import platform

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
