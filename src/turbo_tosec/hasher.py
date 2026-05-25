import hashlib
import zlib
import os
from typing import Callable, Generator

class FileHasher:
    """
    Math is written exactly once, 
    but can be consumed as a Generator (for CLI) 
    or a Synchronous call (for Threads/UI).
    """

    @staticmethod
    def compute_gen(file_path: str, algorithm: str) -> Generator[tuple[int, int], None, str]:
        """
        Yields (processed_bytes, total_bytes) for progress tracking.
        Returns the final hash string upon completion.
        """
        algorithm_name = algorithm.lower().replace("-", "")
        file_size = os.path.getsize(file_path)
        processed_bytes = 0

        # CRC32
        if algorithm_name == 'crc32':
            crc = 0
            
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    crc = zlib.crc32(chunk, crc)
                    processed_bytes += len(chunk)
                    
                    yield processed_bytes, file_size
                    
            return f"{crc & 0xFFFFFFFF:08x}"

        # Standard Hashlib (MD5, SHA1, etc.)
        if algorithm_name not in hashlib.algorithms_available:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
            
        hasher = hashlib.new(algorithm_name)
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
                processed_bytes += len(chunk)
            
                yield processed_bytes, file_size
                
        return hasher.hexdigest()

    @staticmethod
    def compute_sync(file_path: str, algorithm: str, is_cancelled: Callable[[], bool] | None = None) -> str | None:
        """
        The Thread Wrapper:
        Consumes the generator synchronously. Checks the cancellation flag 
        on every chunk. Returns the final hash or None if aborted.
        """
        gen = FileHasher.compute_gen(file_path, algorithm)
        
        try:
            # Loop through the generator, let it do the heavy lifting
            for processed, total in gen:
                # The UI Thread injected this callback. Checks it every 8KB.
                if is_cancelled and is_cancelled():
                    gen.close()  # Safely closes the generator and the open file
                    return None
                    
        except StopIteration as e:
            # In modern Python, when a generator executes a 'return' statement,
            # the returned value is attached to the StopIteration exception!
            return e.value
            
        return None
