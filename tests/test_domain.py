# tests/test_domain.py
import pytest
from turbo_tosec.domain import TosecNamingService

class TestTosecNamingService:
    
    def test_extract_version_success(self):
        path = "/roms/Amiga/TOSEC-v2023-08-15/games"
        assert TosecNamingService.extract_version(path) == "TOSEC-v2023-08-15"
        
    def test_extract_version_case_insensitive(self):
        path = "/roms/tosec-v2022-01-01/games"
        # The regex should capture it as it is in the string, or we test that it found it
        assert TosecNamingService.extract_version(path).lower() == "tosec-v2022-01-01"

    def test_extract_version_not_found(self):
        path = "/roms/Amiga/RandomFolder/games"
        assert TosecNamingService.extract_version(path) == "Unknown"

    def test_versions_match(self):
        # Exact match
        assert TosecNamingService.versions_match("TOSEC-v2023-08-15", "TOSEC-v2023-08-15") is True
        # Whitespace/Case mismatch that should evaluate to True
        assert TosecNamingService.versions_match(" TOSEC-V2023-08-15 ", "tosec-v2023-08-15") is True
        # Actual mismatch
        assert TosecNamingService.versions_match("TOSEC-v2023-08-15", "TOSEC-v2022-01-01") is False
