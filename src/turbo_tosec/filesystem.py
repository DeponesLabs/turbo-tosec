import os
from typing import List

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
