import os
from typing import Generator, Tuple
import hashlib
import warnings
import functools

from turbo_tosec.deprecation import deprecated

DEPRECATION_MSG = ("The 'crypto' module is deprecated. "
                   "Please use 'turbo_tosec.core.hasher.FileHasher' instead.")

# Module-level warning (Triggers when someone does 'import crypto')
warnings.warn(DEPRECATION_MSG, category=DeprecationWarning, stacklevel=2)


@deprecated(reason=DEPRECATION_MSG)
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

@deprecated(reason=DEPRECATION_MSG)
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
