"""
Mermaid Syntax Sanitizer for Pyreverse Output (Final Production Version).

This script fixes Python syntax formatting errors (PEP 484 type hints) for Mermaid,
strips crashing empty class brackets, and allows you to dynamically inject a custom 
layout orientation (TB, LR, BT, RL).

Usage:
    python fix_mermaid.py <path_to_mmd_file> [orientation_code]
    
Examples:
    python fix_mermaid.py classes.mmd       # Defaults to Top-to-Bottom (TB)
    python fix_mermaid.py classes.mmd LR    # Forces Left-to-Right layout
"""

import sys
import re
from pathlib import Path

def sanitize_mermaid_file(file_path: str, direction: str = "TB") -> None:
    path = Path(file_path)
    if not path.exists():
        print(f"Error: Could not find {file_path}")
        return

    content = path.read_text(encoding="utf-8")

    # 1. Clean up Python artifacts and invisible characters
    content = content.replace('\xa0', ' ')
    content = content.replace('...', '')
    content = content.replace('NoneType, ', '')
    content = content.replace(', NoneType', '')

    # 2. Safely replace the Union operator (pipe WITH spaces) 
    # Do NOT replace raw '|' otherwise it destroys Mermaid's inheritance arrow (--|>)
    content = content.replace(' | ', ' or ')

    # 3. FIX FOR EMPTY CLASSES: Remove brackets with only whitespace/newlines inside
    content = re.sub(r'\{\s*\}', '', content)

    # 4. INJECT ORIENTATION: Inject direction directly under 'classDiagram' line
    valid_directions = ["TB", "BT", "LR", "RL"]
    target_dir = direction.upper() if direction.upper() in valid_directions else "TB"
    
    if "direction " not in content:
        content = content.replace("classDiagram", f"classDiagram\n  direction {target_dir}")

    # 5. Stack-based parser for generics
    out = []
    bracket_depth = 0
    
    for char in content:
        if char == '[':
            bracket_depth += 1
            out.append('⟨')  # Unicode Left Angle Bracket
        elif char == ']':
            if bracket_depth > 0:
                bracket_depth -= 1
            out.append('⟩')  # Unicode Right Angle Bracket
        elif char == ',' and bracket_depth > 0:
            # Inside a generic type: remove the comma so Mermaid doesn't split the param
            out.append(' ')
        else:
            out.append(char)
            
    # 6. Final string cleanup
    final_content = "".join(out)
    final_content = final_content.replace('  ', ' ') 
    final_content = final_content.replace('⟨ ', '⟨').replace(' ⟩', '⟩')

    # Overwrite the file with the sanitized content
    path.write_text(final_content, encoding="utf-8")
    print(f"Successfully sanitized Mermaid layout (Direction: {target_dir}) in {path.name}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Check if an orientation argument was passed, else default to 'TB'
        chosen_direction = sys.argv[2] if len(sys.argv) > 2 else "TB"
        sanitize_mermaid_file(sys.argv[1], chosen_direction)
    else:
        print("Usage: python fix_mermaid.py <path_to_mmd_file> [TB|LR|BT|RL]")