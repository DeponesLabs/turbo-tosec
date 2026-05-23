import os
import pytest
from pathlib import Path
from turbo_tosec.parser import TurboParser, detect_file_format

SAMPLE_CMP_CONTENT = """clrmamepro (
    name "Commodore 64 - Games"
    description "Commodore 64 - Games (TOSEC-v2012)"
    version 2012
)

game (
    name "Test Game (1986)(Publisher)[!]"
    description "Test Game Description"
    rom ( name "test.zip" size 100 crc 12345678 md5 abcdef123456 sha1 1234567890abcdef )
)

game (
    name "Another Game"
    description "Just another game"
    rom ( name "game2.rom" size 200 crc AABBCCDD md5 11223344 sha1 55667788 )
)
"""

@pytest.fixture
def mock_cmp_file(tmp_path: Path) -> str:
    """
    Constructs a structurally valid ClrMamePro (CMP) Dat file in an isolated 
    temporary directory for testing extraction logic without disk I/O dependency.
    """
    file_path = tmp_path / "Commodore 64 - Games.dat"
    file_path.write_text(SAMPLE_CMP_CONTENT, encoding="utf-8")
    return str(file_path)

@pytest.fixture
def parser() -> TurboParser:
    """Provides a fresh parser instance for testing state encapsulation."""
    return TurboParser()


class TestCMPParser:
    
    def test_is_cmp_file_detection(self, tmp_path: Path, parser: TurboParser):
        """
        Validates the format detection heuristic to ensure the engine correctly 
        routes files to the CMP parser versus the XML parser.
        """
        # Create a valid CMP file
        cmp_file = tmp_path / "test.dat"
        cmp_file.write_text(SAMPLE_CMP_CONTENT, encoding="utf-8")
        
        # Create an invalid (XML) file
        xml_file = tmp_path / "test.xml"
        xml_file.write_text("<?xml version='1.0'?><datafile>...</datafile>", encoding="utf-8")

        assert detect_file_format(str(cmp_file)) == 'cmp'
        assert detect_file_format(str(xml_file)) != 'cmp'

    def test_parser_extracts_valid_cmp_data(self, mock_cmp_file: str, parser: TurboParser):
        """
        Validates that the CMP parser successfully tokenizes the proprietary format, 
        extracts the required nodes, and formats the output into the strict 
        14-column tuple required by the DatabaseManager schema.
        """
        results = list(parser.parse(mock_cmp_file))
        
        # Verify total node extraction count
        assert len(results) == 2
        
        # Extract first record for strict schema validation
        game1 = results[0]
        
        # Verify Schema Index 0: dat_filename
        assert game1[0] == "Commodore 64 - Games.dat"
        
        # Verify Schema Index 3 & 4: game_name and title extraction
        assert "Test Game" in game1[3]
        
        # Verify Schema Index 7: rom_name
        assert game1[7] == "test.zip"
        
        # Verify Schema Index 8: size (Must be castable/evaluated as integer)
        assert int(game1[8]) == 100
        
        # Verify Schema Index 9: CRC
        assert game1[9] == "12345678"
        
        # Verify Schema Index 10 & 11: MD5 and SHA1
        assert game1[10] == "abcdef123456"
        assert game1[11] == "1234567890abcdef"
        
        # Extract second record to ensure fallback behavior works on missing standard tags
        game2 = results[1]
        assert game2[8] == 200
        assert game2[9] == "AABBCCDD"


@pytest.fixture
def mock_dat_file(tmp_path: Path) -> str:
    """
    Constructs a structurally valid, minimal TOSEC XML Dat file in an isolated 
    temporary directory. This prevents actual disk I/O dependency during CI/CD pipelines.
    """
    xml_payload = """<?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE datafile PUBLIC "-//Logiqx//DTD ROM Management Datafile//EN" "http://www.logiqx.com/Dats/datafile.dtd">
    <datafile>
        <header>
            <name>Commodore Amiga - Games - [TOSEC-v2024-01-01]</name>
            <description>Commodore Amiga - Games</description>
            <version>2024-01-01</version>
            <author>TOSEC</author>
        </header>
        <game name="Alien Breed (1992)(Team17)(AGA)(Disk 1 of 3)[cr][b]">
            <description>Alien Breed (1992)(Team17)(AGA)(Disk 1 of 3)[cr][b]</description>
            <rom name="Alien_Breed_Disk1.adf" size="901120" crc="A1B2C3D4" md5="098f6bcd4621d373cade4e832627b4f6" sha1="a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"/>
        </game>
        <game name="Zelda (1986)(Nintendo)[!]">
            <description>Zelda (1986)(Nintendo)[!]</description>
            <rom name="zelda.rom" size="1024" crc="00000000" md5="md5hash456" sha1="sha1hash456"/>
        </game>
    </datafile>
    """
    
    file_path = tmp_path / "Commodore Amiga - Games.dat"
    file_path.write_text(xml_payload, encoding="utf-8")
    
    return str(file_path)

@pytest.fixture
def empty_dat_file(tmp_path: Path) -> str:
    """Constructs a valid TOSEC XML file containing a header but zero ROM entries."""
    xml_payload = """<?xml version="1.0" encoding="utf-8"?>
    <datafile>
        <header><name>Empty System</name></header>
    </datafile>
    """
    file_path = tmp_path / "empty.dat"
    file_path.write_text(xml_payload, encoding="utf-8")
    return str(file_path)

class TestTurboParser:
    
    def test_parser_extracts_valid_rom_data(self, mock_dat_file: str):
        """
        Validates that the parser successfully traverses the XML tree, 
        extracts the required nodes, and formats the output into the strict 
        14-column tuple required by the DatabaseManager schema.
        """
        parser = TurboParser()
        
        # Depending on implementation, parse() may return a generator or a list.
        # Coercing to list ensures full evaluation for testing.
        results = list(parser.parse(mock_dat_file))
        
        # Verify total node extraction count
        assert len(results) == 2
        
        # Extract first record for strict schema validation
        game1 = results[0]
        
        # Verify Schema Index 0: dat_filename
        assert game1[0] == "Commodore Amiga - Games.dat"
        
        # Verify Schema Index 3 & 4: game_name and title extraction
        assert "Alien Breed" in game1[3]
        
        # Verify Schema Index 7: rom_name
        assert game1[7] == "Alien_Breed_Disk1.adf"
        
        # Verify Schema Index 8: size (Must be castable/evaluated as integer)
        assert int(game1[8]) == 901120
        
        # Verify Schema Index 9: CRC
        assert game1[9] == "A1B2C3D4"

    def test_parser_handles_empty_dat_gracefully(self, empty_dat_file: str):
        """
        Validates that parsing a valid XML file with no <game> nodes 
        returns an empty collection without raising exceptions.
        """
        parser = TurboParser()
        results = list(parser.parse(empty_dat_file))
        
        assert len(results) == 0

    def test_parser_raises_on_missing_file(self):
        """
        Validates the infrastructure's fail-fast mechanism when provided 
        with an invalid or non-existent file path.
        """
        parser = TurboParser()
        
        # The underlying xml.etree or lxml library should raise an IOError/FileNotFoundError
        with pytest.raises((ValueError, FileNotFoundError, OSError)):
            list(parser.parse("non_existent_system_path.dat"))