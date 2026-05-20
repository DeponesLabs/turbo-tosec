import re
from typing import Tuple

class TosecNamingService:
    """
    Domain Service responsible for encapsulating all business rules and 
    knowledge regarding TOSEC naming conventions, patterns, and formats.
    
    This class is completely stateless and has zero dependencies on 
    infrastructure (databases, file systems, or UI).
    """
    
    @staticmethod
    def extract_version(directory_path: str) -> str:
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
    
class TosecTitleDecoder:
    
    @staticmethod
    def parse_game_info(game_name: str | None) -> Tuple[str, int]:
        """
        Extracts title and release year from the game name string
        Input: "Dragonstone (1994)(Core)(M3)(Disk 1 of 4)[cr RNX - TRD]"
        Output: ("Dragonstone", "1994")
        """
        # Safety Check: XML node might miss the 'name' attribute
        if not game_name:
            return "Unknown", 0
        
        # Title: Take everything up to the first '(' character)
        # If there are no parentheses, take the entire name.
        title_match = re.match(r'^(.*?)(\s*\(|$)', game_name)
        title = title_match.group(1).strip() if title_match else game_name.strip()
        
        # Year: Capture the format (19xx) or (20xx)
        # Usually the first parenthesis, but look for 4 digits to be sure.
        year_match = re.search(r'\((\d{4})\)', game_name)
        release_year = int(year_match.group(1)) if year_match else 0
        
        return title, release_year

    @staticmethod
    def versions_match(db_version: str, input_version: str) -> bool:
        """
        Evaluates if the incoming TOSEC dataset version is compatible with the existing database.
        Encapsulates the business logic for version equality (handles case-insensitivity and whitespace).
        """
        # A robust enterprise check rather than a fragile simple string comparison
        return db_version.strip().lower() == input_version.strip().lower()
