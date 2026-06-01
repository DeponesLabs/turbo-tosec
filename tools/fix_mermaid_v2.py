"""
Turbo-Tosec Unified UML Generator and Sanitizer (CLI Powered).

This script automates the complete architectural documentation pipeline:
1. Parses runtime options and flags via argparse.
2. Verifies and creates target output directories.
3. Executes `pyreverse` via `subprocess` to build the Abstract Syntax Tree.
4. Post-processes the output file using a custom character stack parser 
   to strip out empty classes and illegal syntax that crash strict Mermaid renderers.
   
Usage:
    python generate_uml.py [orientation] [options]
"""

import sys
import re
import subprocess
import argparse
from pathlib import Path

def parse_arguments():
    """Sets up argparse for command line flags and options."""
    parser = argparse.ArgumentParser(
        description="Automated Pyreverse-to-Mermaid generator with built-in syntax sanitization."
    )
    
    # Positional argument with choices and a default
    parser.add_argument(
        "orientation",
        nargs="?",
        default="TB",
        choices=["TB", "BT", "LR", "RL"],
        help="Diagram layout orientation. TB=Top-to-Bottom, LR=Left-to-Right. (Default: TB)"
    )
    
    # Optional flags for full flexibility
    parser.add_argument(
        "-s", "--source",
        default="src/turbo_tosec",
        help="Source directory or package to parse. (Default: src/turbo_tosec)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="./docs/diagrams/mermaids/",
        help="Destination directory for the output file. (Default: ./docs/diagrams/mermaids/)"
    )
    
    parser.add_argument(
        "-i", "--ignore",
        default="tests,ui_compiled.py",
        help="Comma-separated list of files/folders to exclude. (Default: tests,ui_compiled.py)"
    )
    
    parser.add_argument(
        "-a", "--depth",
        default="1",
        help="Ancestry depth level for external inheritances. (Default: 1)"
    )
    
    return parser.parse_args()

def run_pyreverse(source: str, output: str, ignore: str, depth: str) -> Path:
    """Executes the pyreverse command using the parsed arguments."""
    out_path = Path(output)
    out_path.mkdir(parents=True, exist_ok=True)
    
    print(f"[*] Initializing static code analysis on target: {source}")
    
    # Construct command array dynamically from parameters
    command = [
        "pyreverse",
        source,
        "-o", "mmd",
        "-a", depth,
        f"--ignore={ignore}",
        "-d", str(out_path)
    ]
    
    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
        print("[+] pyreverse successfully compiled the Abstract Syntax Tree (AST).")
        return out_path / "classes.mmd"
        
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Error: pyreverse execution failed!")
        print(f"Stdout:\n{e.stdout}")
        print(f"Stderr:\n{e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n[!] Critical Error: 'pyreverse' command not found inside the active environment.")
        sys.exit(1)

def sanitize_mermaid_file(file_path: Path, direction: str) -> None:
    """Performs character-by-character cleaning to ensure Mermaid rendering safety."""
    if not file_path.exists():
        print(f"[!] Sanitization Error: Target file {file_path} not found.")
        return

    print(f"[*] Post-processing raw file for Mermaid compatibility: {file_path.name}")
    content = file_path.read_text(encoding="utf-8")

    # 1. Strip copy-paste artifacts and dynamic typing anomalies
    content = content.replace('\xa0', ' ')
    content = content.replace('...', '')
    content = content.replace('NoneType, ', '').replace(', NoneType', '')

    # 2. Convert python style type unions (leaving structural arrows untouched)
    content = content.replace(' | ', ' or ')

    # 3. CRITICAL: Remove empty class definitions entirely (removes curly brackets)
    content = re.sub(r'\{\s*\}', '', content)

    # 4. Inject structural orientation/layout controls
    if "direction " not in content:
        content = content.replace("classDiagram", f"classDiagram\n  direction {direction}")

    # 5. Non-destructive Stack Parser for flattening complex nested types
    out = []
    bracket_depth = 0
    
    for char in content:
        if char == '[':
            bracket_depth += 1
            out.append('⟨')
        elif char == ']':
            if bracket_depth > 0:
                bracket_depth -= 1
            out.append('⟩')
        elif char == ',' and bracket_depth > 0:
            out.append(' ')
        else:
            out.append(char)
            
    # 6. Formatting Polish
    final_content = "".join(out)
    final_content = final_content.replace('  ', ' ') 
    final_content = final_content.replace('⟨ ', '⟨').replace(' ⟩', '⟩')

    file_path.write_text(final_content, encoding="utf-8")
    print(f"[+] Complete! Clean diagram saved safely with '{direction}' orientation.")

if __name__ == "__main__":
    # Parse CLI flags
    args = parse_arguments()
    
    # Run the generation pipeline using parsed args
    target_file = run_pyreverse(
        source=args.source,
        output=args.output,
        ignore=args.ignore,
        depth=args.depth
    )
    
    # Sanitize the output file
    sanitize_mermaid_file(target_file, args.orientation)