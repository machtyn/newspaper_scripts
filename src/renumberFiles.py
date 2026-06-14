import os
import re
import argparse
import sys

# ==============================================================================
# GLOBAL CONFIGURATION & SCOPING
# ==============================================================================
# Constants for Renaming Passes
INTERMEDIATE_PREFIX = "8"  # Temporary prefix used for pass one (e.g., 8001)
FINAL_PREFIX = "0"         # Final prefix used for pass two (e.g., 0001)

# ANSI Escape Codes for console text formatting
ANSI_BOLD = "\033[1m"
ANSI_BLINK = "\033[5m"
ANSI_BRIGHT_RED = "\033[91m"
ANSI_RESET = "\033[0m"

# STRICT REGEX: Enforces a strict space trailing the textual root prefix
PATTERN_4_DIGITS = re.compile(r"(.+ )(\d{4})(\..+)")


def rename_files_in_folder(folder_path, total_renamed_count):
    """
    Performs a double-pass rename operation in a single folder.
    Pass 1: Renames matching files to an intermediate 8xxx format.
    Pass 2: Renames the 8xxx files to the final 0xxx format.
    """
    files_renamed_in_folder = 0

    # Clean and normalize path representation
    folder_path = os.path.normpath(folder_path)

    # Harvest a list of files that match our target sequence pattern
    original_matching_files = []
    try:
        for filename in os.listdir(folder_path):
            full_path = os.path.join(folder_path, filename)
            if os.path.isfile(full_path) and PATTERN_4_DIGITS.match(filename):
                original_matching_files.append(filename)
    except Exception as e:
        print(f"  🚨 Error reading or accessing directory {folder_path}: {e}")
        return total_renamed_count

    num_files = len(original_matching_files)
    if num_files == 0:
        return total_renamed_count

    print(f"\nProcessing folder: '{folder_path}'")
    print(f"  Found {num_files} matching assets to process.")

    # Sort and reverse the array elements to safely execute reverse renaming logic
    original_matching_files.sort()
    original_matching_files.reverse()

    # ==========================================================
    # PASS 1: Rename to Intermediate (8001, 8002, ...)
    # ==========================================================
    print("  PASS 1: Shifting assets to temporary 8xxx buffer sequence...")
    intermediate_files = []
    
    for index, old_filename in enumerate(original_matching_files):
        # Calculate sequential number (1 to num_files) in reverse order
        new_number_int = num_files - index
        
        # Format as 4 digits, but prepend the temporary '8' marker
        new_number_str = f"{INTERMEDIATE_PREFIX}{new_number_int:03d}"

        match = PATTERN_4_DIGITS.match(old_filename)
        if match:
            start_part = match.group(1)
            end_part = match.group(3)
            
            intermediate_filename = f"{start_part}{new_number_str}{end_part}"
            old_path = os.path.join(folder_path, old_filename)
            intermediate_path = os.path.join(folder_path, intermediate_filename)

            try:
                os.rename(old_path, intermediate_path)
                intermediate_files.append(intermediate_filename)
            except OSError as e:
                print(f"    ❌ ERROR renaming '{old_filename}' in PASS 1: {e}")
        
    # ==========================================================
    # PASS 2: Rename from Intermediate (8xxx) to Final (0xxx)
    # ==========================================================
    print("  PASS 2: Remapping temporary buffer sequence to final 0xxx array...")

    # We must explicitly sort intermediate files to guarantee sequence consistency
    intermediate_files.sort()
    
    for index, temp_filename in enumerate(intermediate_files):
        new_number_int = index + 1
        final_number_str = f"{new_number_int:04d}"

        match = PATTERN_4_DIGITS.match(temp_filename)
        if match:
            start_part = match.group(1)
            end_part = match.group(3)
            
            final_filename = f"{start_part}{final_number_str}{end_part}"
            intermediate_path = os.path.join(folder_path, temp_filename)
            final_path = os.path.join(folder_path, final_filename)

            try:
                os.rename(intermediate_path, final_path)
                files_renamed_in_folder += 1
            except OSError as e:
                print(f"    ❌ ERROR renaming '{temp_filename}' in PASS 2: {e}")
    
    print(f"  Successfully re-indexed {files_renamed_in_folder} files inside this folder directory.")
    return total_renamed_count + files_renamed_in_folder


def traverse_and_rename(source_dir):
    """
    Recursively traverses the source directory structure to execute 
    two-pass file sequential restructuring workflows.
    """
    total_renamed_count = 0
    
    for root, dirs, files in os.walk(source_dir):
        total_renamed_count = rename_files_in_folder(root, total_renamed_count)
        
    return total_renamed_count


def main():
    parser = argparse.ArgumentParser(
        description="Recursively rename portfolio images via a double-pass system to prevent overwrites.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    # Unified parameter format (-s / --source_directory)
    parser.add_argument(
        '-s', 
        '--source_directory',
        type=str,
        help='The source directory path where target files will be sequentially processed.'
    )
    args = parser.parse_args()

    source_dir = args.source_directory

    # Prompt user for folder path input if command-line args are missing
    if source_dir is None:
        source_dir = input("Please enter the target source directory path: ")

    # Fallback to the default path schema if input prompt string matches whitespace or is blank
    DEFAULT_DIR = r"D:\Georgetown_News_Graphic\Working_Folder"
    if not source_dir.strip():
        print(f"Input was blank. Using default workspace folder: {DEFAULT_DIR}")
        source_dir = DEFAULT_DIR

    # Normalize path string format to unify messy OS/Windows backslashes
    source_dir = os.path.normpath(source_dir)

    # Stop runtime loop execution immediately if target directory does not exist
    if not os.path.isdir(source_dir):
        print(f"Error: Target directory not found at path destination '{source_dir}'")
        sys.exit(1)

    print("-" * 60)
    formatted_source_dir = f"{ANSI_BOLD}{ANSI_BRIGHT_RED}{ANSI_BLINK}{source_dir}{ANSI_RESET}"
    print(f"Starting double-pass file rename process in: {formatted_source_dir}")
    print(f"Pass 1 Validation Prefix: {INTERMEDIATE_PREFIX}xxx")
    print(f"Pass 2 Production Prefix: {FINAL_PREFIX}xxx")
    print("-" * 60)

    try:
        total_renamed = traverse_and_rename(source_dir)
    except Exception as e:
        print(f"\nAn unexpected systemic script runtime execution error occurred: {e}")
        total_renamed = 0 

    print("-" * 60)
    print("Sequential renumbering processing block complete.")
    print(f"✅ Total portfolio files successfully re-indexed: {total_renamed}")
    print("-" * 60)


if __name__ == "__main__":
    main()