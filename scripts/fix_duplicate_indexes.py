"""
Script to fix duplicate index definitions in SQLAlchemy models.

This script finds columns that have index=True and also have an explicit Index()
declaration in __table_args__, and removes the explicit Index() to avoid duplicates.
"""

import re
from pathlib import Path


def find_and_fix_duplicate_indexes(dry_run=True):
    """
    Find and fix duplicate index definitions.

    Args:
        dry_run: If True, only prints what would be changed without modifying files
    """
    models_path = Path("src/models")
    fixed_files = []

    for py_file in models_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()
            original_content = content
            lines = content.split("\n")

        # Find columns with index=True
        indexed_columns = set()
        for i, line in enumerate(lines):
            if "Column(" in line:
                # Get column name
                col_match = re.search(r"(\w+)\s*=\s*Column", line)
                if not col_match:
                    continue

                col_name = col_match.group(1)

                # Check if this column has index=True (in this or next lines)
                check_lines = "\n".join(lines[i : min(len(lines), i + 15)])
                if "index=True" in check_lines and "__table_args__" not in check_lines:
                    indexed_columns.add(col_name)

        if not indexed_columns:
            continue

        # Find and remove duplicate explicit Index() declarations
        modified = False
        new_lines = []
        in_table_args = False
        skip_next_comma = False

        for i, line in enumerate(lines):
            if "__table_args__" in line:
                in_table_args = True
                new_lines.append(line)
                continue

            if in_table_args and line.strip() == ")":
                in_table_args = False
                new_lines.append(line)
                continue

            # Check if this is an Index() line in __table_args__
            if in_table_args and "Index(" in line:
                # Extract column name from Index("ix_name", "column_name")
                match = re.search(r'Index\([^,]+,\s*"(\w+)"(?:\s*,|\s*\))', line)
                if match:
                    col_name = match.group(1)
                    if col_name in indexed_columns:
                        # This is a duplicate - comment it out
                        indent = len(line) - len(line.lstrip())
                        comment = " " * indent + f"# REMOVED DUPLICATE: {line.strip()} - {col_name} already has index=True"
                        new_lines.append(comment)
                        modified = True

                        # Check if next line is just a comma, skip it too
                        if i + 1 < len(lines) and lines[i + 1].strip() == ",":
                            skip_next_comma = True
                        continue

            if skip_next_comma and line.strip() == ",":
                skip_next_comma = False
                continue

            new_lines.append(line)

        if modified:
            new_content = "\n".join(new_lines)

            if dry_run:
                print(f"\nWould fix {py_file}:")
                print(f"  Indexed columns: {indexed_columns}")
                print(f"  Changes: {len(lines) - len(new_lines)} lines would be removed/commented")
            else:
                with open(py_file, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Fixed {py_file}")

            fixed_files.append(str(py_file))

    return fixed_files


if __name__ == "__main__":
    import sys

    dry_run = "--apply" not in sys.argv

    if dry_run:
        print("DRY RUN MODE - No files will be modified")
        print("Run with --apply to actually fix the files\n")
    else:
        print("APPLYING FIXES\n")

    fixed = find_and_fix_duplicate_indexes(dry_run=dry_run)

    print(f"\n{'Would fix' if dry_run else 'Fixed'} {len(fixed)} files")

    if dry_run:
        print("\nRun again with --apply to apply these fixes")
