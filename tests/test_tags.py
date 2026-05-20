# tests/test_tags.py
import pytest
from turbo_tosec.tags import TosecTagEvaluator

class TestTosecTagEvaluator:
    
    def test_is_bad_dump(self):
        assert TosecTagEvaluator.is_bad_dump("Super Mario [b].rom") is True
        assert TosecTagEvaluator.is_bad_dump("Super Mario [B].rom") is True  # Case insensitive check
        assert TosecTagEvaluator.is_bad_dump("Super Mario [!].rom") is False

    def test_is_verified(self):
        assert TosecTagEvaluator.is_verified("Zelda [!].rom") is True
        assert TosecTagEvaluator.is_verified("Zelda [a].rom") is False

    def test_is_cracked(self):
        assert TosecTagEvaluator.is_cracked("Doom [cr].rom") is True
        assert TosecTagEvaluator.is_cracked("Doom [CR].rom") is True
        assert TosecTagEvaluator.is_cracked("Doom [a].rom") is False

    def test_extract_languages(self):
        # Single language
        assert TosecTagEvaluator.extract_languages("Game (En).rom") == ["En"]
        # Multiple languages
        assert TosecTagEvaluator.extract_languages("Game (En,Fr,De).rom") == ["En", "Fr", "De"]
        # No languages
        assert TosecTagEvaluator.extract_languages("Game (1995)(Ocean).rom") == []

    def test_analyze_tags(self):
        filename = "Alien Breed (1992)(Team17)(En,Fr)[cr][b].rom"
        metadata = TosecTagEvaluator.analyze_tags(filename)
        
        assert metadata["is_bad_dump"] is True
        assert metadata["is_cracked"] is True
        assert metadata["is_verified"] is False
        assert metadata["languages"] == ["En", "Fr"]
        assert "CRACKED" in metadata["modifications"]
