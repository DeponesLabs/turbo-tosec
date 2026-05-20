import re
from enum import Enum
from typing import List, Dict, Any

class TosecDumpStatus(Enum):
    """Enumeration of official TOSEC dump status flags."""
    VERIFIED = "[!]"
    BAD_DUMP = "[b]"
    ALTERNATE = "[a]"
    OVERDUMP = "[o]"
    UNDERDUMP = "[u]"


class TosecModification(Enum):
    """Enumeration of official TOSEC modification flags."""
    CRACKED = "[cr]"
    HACKED = "[h]"
    TRAINED = "[t]"
    FIXED = "[f]"
    MODIFIED = "[m]"
    PIRATE = "[p]"
    VIRUS = "[v]"


class TosecTagEvaluator:
    """
    Standalone utility service for parsing and evaluating standard TOSEC 
    bracket and parentheses tags from ROM filenames.
    
    This class is completely independent of application state, file systems, 
    or database connections.
    """

    @staticmethod
    def is_bad_dump(filename: str) -> bool:
        """Evaluates if the file is explicitly flagged as a bad dump."""
        return TosecDumpStatus.BAD_DUMP.value in filename.lower()

    @staticmethod
    def is_verified(filename: str) -> bool:
        """Evaluates if the file is flagged as a verified good dump."""
        return TosecDumpStatus.VERIFIED.value in filename

    @staticmethod
    def is_cracked(filename: str) -> bool:
        """Evaluates if the file has been cracked."""
        return TosecModification.CRACKED.value in filename.lower()

    @staticmethod
    def is_alternate(filename: str) -> bool:
        """Evaluates if the file is an alternate version."""
        return TosecDumpStatus.ALTERNATE.value in filename.lower()

    @staticmethod
    def extract_languages(filename: str) -> List[str]:
        """
        Extracts language codes from TOSEC parentheses.
        Example: 'Alien Breed (1992)(Ocean)(En,Fr,De).rom' -> ['En', 'Fr', 'De']
        """
        # Matches patterns like (En), (En,Fr), (En,Fr,De)
        # TOSEC standard usually capitalizes the first letter of the language code.
        lang_pattern = r"\(([A-Z][a-z](?:,[A-Z][a-z])*)\)"
        match = re.search(lang_pattern, filename)
        
        if match:
            # Split by comma to return a clean list of individual languages
            return match.group(1).split(',')
        return []

    @staticmethod
    def analyze_tags(filename: str) -> Dict[str, Any]:
        """
        Returns a comprehensive metadata dictionary summarizing all major TOSEC traits 
        found in the filename. Highly useful for UI filtering or database indexing.
        """
        lower_filename = filename.lower()
        
        # Check all modifications dynamically based on the Enum
        mods_found = [
            mod.name for mod in TosecModification 
            if mod.value in lower_filename
        ]
        
        return {
            "is_verified": TosecTagEvaluator.is_verified(filename),
            "is_bad_dump": TosecTagEvaluator.is_bad_dump(filename),
            "is_alternate": TosecTagEvaluator.is_alternate(filename),
            "languages": TosecTagEvaluator.extract_languages(filename),
            "modifications": mods_found
        }
