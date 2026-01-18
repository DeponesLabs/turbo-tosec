from dataclasses import dataclass

@dataclass(slots=True)
class TosecDat:
    
    dat_filename: str = ""
    platform: str = ""
    category: str = ""
    game_name: str = ""
    title: str = ""
    release_year: str = ""     # int is dangerous. "199?"
    description: str = ""
    rom_name: str = ""
    size: int = 0              # byte
    crc: str = ""
    md5: str = ""
    sha1: str = ""
    status: str = ""           # [!], [b] etc.
    system: str = ""

    @property
    def human_readable_size(self) -> str:
        
        try:
            s = float(self.size)
        except (ValueError, TypeError):
            return "0 B"
            
        for unit in ['B', 'KB', 'MB', 'GB']:
            if s < 1024.0:
                return f"{s:.2f} {unit}"
            s /= 1024.0
        return f"{s:.2f} TB"

    @property
    def is_verified(self) -> bool:
        """Does the file contain a 'verified dump' [!]?"""
        return "[!]" in (self.status or "") or "[!]" in self.rom_name

    def match_quality(self, local_file_size: int, local_crc: str = None) -> int:
        """
        Local file match score (0-100)
        """
        score = 0
        
        # By size
        if self.size == local_file_size:
            score += 20
        
        # By CRC
        if local_crc and self.crc:
            if local_crc.lower() == self.crc.lower():
                score += 80
            
        return score