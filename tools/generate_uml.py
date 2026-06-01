"""
Turbo-Tosec Unified UML Generator and Sanitizer (Multi-File Architecture).

This script automates the complete architectural documentation pipeline:
1. Parses runtime options and flags via argparse.
2. Verifies and creates target output directories.
3. Executes `pyreverse` via `subprocess` to generate BOTH classes.mmd and packages.mmd.
4. Dynamically unpacks paths and post-processes both documents using an 
   adaptive stack parser to ensure 100% rendering layout compatibility.
"""

import sys
import re
import subprocess
import argparse
from pathlib import Path

def parse_arguments():
    """Sets up argparse for command line flags and options."""
    parser = argparse.ArgumentParser(
        description="Automated Pyreverse-to-Mermaid generator tracking multiple layout files."
    )
    parser.add_argument(
        "orientation",
        nargs="?",
        default="TB",
        choices=["TB", "BT", "LR", "RL"],
        help="Diagram layout orientation. TB=Top-to-Bottom, LR=Left-to-Right. (Default: TB)"
    )
    parser.add_argument(
        "-s", "--source",
        default="src/turbo_tosec",
        help="Source directory or package to parse. (Default: src/turbo_tosec)"
    )
    parser.add_argument(
        "-o", "--output",
        default="./docs/diagrams/mermaids/",
        help="Destination directory for output files. (Default: ./docs/diagrams/mermaids/)"
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

def run_pyreverse(source: str, output: str, ignore: str, depth: str) -> tuple[Path, Path]:
    """
    Executes pyreverse and dynamically maps both output paths.
    
    Returns:
        tuple[Path, Path]: A pair matching (classes_diagram_path, packages_diagram_path)
    """
    out_path = Path(output)
    out_path.mkdir(parents=True, exist_ok=True)
    
    print(f"[*] Initializing static code analysis on target: {source}")
    
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
        print("[+] pyreverse successfully compiled Class and Project files.")
        
        # Capture and return both file paths explicitly as a tuple
        classes_file = out_path / "classes.mmd"
        packages_file = out_path / "packages.mmd"
        return classes_file, packages_file
        
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Error: pyreverse execution failed!")
        print(f"Stdout:\n{e.stdout}")
        print(f"Stderr:\n{e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n[!] Critical Error: 'pyreverse' command not found inside the active environment.")
        sys.exit(1)

def sanitize_mermaid_file(file_path: Path, direction: str) -> None:
    """Performs adaptive cleaning and injects orientation flags into Mermaid files."""
    if not file_path.exists():
        print(f"[!] Warning: Expected file {file_path.name} was not built by pyreverse.")
        return

    print(f"[*] Sanitizing layout specifications for: {file_path.name}")
    content = file_path.read_text(encoding="utf-8")

    # 1. Strip copy-paste artifacts and dynamic typing anomalies
    content = content.replace('\xa0', ' ')
    content = content.replace('...', '')
    content = content.replace('NoneType, ', '').replace(', NoneType', '')

    # 2. Convert python style type unions
    content = content.replace(' | ', ' or ')

    # 3. Remove empty class brackets entirely
    content = re.sub(r'\{\s*\}', '', content)

    # 4. ADAPTIVE ORIENTATION: Handle Class Diagrams vs Flowchart Package Graphs
    if "direction " not in content:
        if "classDiagram" in content:
            content = content.replace("classDiagram", f"classDiagram\n  direction {direction}")
        elif "graph " in content:
            # If package diagram utilizes a standard 'graph TD' format, normalize its direction header
            content = re.sub(r'graph \w+', f'graph {direction}', content)

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
    print(f"[+] Cleaned artifact saved: {file_path.name}")

if __name__ == "__main__":
    args = parse_arguments()
    
    # Unpack both file handles using clean Python tuple unpacking
    classes_path, packages_path = run_pyreverse(
        source=args.source,
        output=args.output,
        ignore=args.ignore,
        depth=args.depth
    )
    
    # Process both target documents sequentially using your orientation settings
    sanitize_mermaid_file(classes_path, args.orientation)
    sanitize_mermaid_file(packages_path, args.orientation)
    
    print("\n[✓] Architecture documentation generation completed successfully.")