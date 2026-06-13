import os
import re
import argparse
import sys

# --- Constants for Renaming Passes ---
INTERMEDIATE_PREFIX = "8" # Prefix used for the first pass (e.g., 8001)
FINAL_PREFIX = "0"        # Prefix used for the second pass (e.g., 0001)

# Pattern to match the 4-digit number: (start) + (four digits) + (end)
# The pattern r"(.+ )(\d{4})(\..+)" is implemented below:
PATTERN_4_DIGITS = re.compile(r"(.+ )(\d{4})(\..+)")


def rename_files_in_folder(folder_path, total_renamed_count):
    """
    Performs a double-pass rename operation in a single folder.
    
    Pass 1: Renames matching files to an intermediate 8xxx format.
    Pass 2: Renames the 8xxx files to the final 0xxx format.
    
    Returns the updated total_renamed_count.
    """
    
    files_renamed_in_folder = 0

    print(f"\nProcessing folder: {folder_path}")

    # 1. Get a list of files that match the original pattern
    original_matching_files = []
    try:
        for filename in os.listdir(folder_path):
            full_path = os.path.join(folder_path, filename)
            if os.path.isfile(full_path) and PATTERN_4_DIGITS.match(filename):
                original_matching_files.append(filename)
    except Exception as e:
        print(f"  Error reading directory {folder_path}: {e}")
        return total_renamed_count

    num_files = len(original_matching_files)

    if num_files == 0:
        print("  No files found matching the original pattern.")
        return total_renamed_count

    print(f"  Found {num_files} files to rename in two passes.")

    # 2. Sort and reverse the list for reverse renaming logic
    original_matching_files.sort()
    original_matching_files.reverse()

    # ==========================================================
    # PASS 1: Rename to Intermediate (8001, 8002, ...)
    # ==========================================================
    print("  PASS 1: Renaming to temporary 8xxx sequence...")
    intermediate_files = []
    
    for index, old_filename in enumerate(original_matching_files):
        # Calculate sequential number (1 to num_files) in reverse order
        new_number_int = num_files - index
        
        # Format as 4 digits, but prepend the '8'
        # Example: 1 -> 8001, 12 -> 8012
        new_number_str = f"{INTERMEDIATE_PREFIX}{new_number_int:03d}" 

        match = PATTERN_4_DIGITS.match(old_filename)
        if match:
            start_part = match.group(1)
            end_part = match.group(3)
            
            # Construct the intermediate filename
            intermediate_filename = f"{start_part}{new_number_str}{end_part}"

            old_path = os.path.join(folder_path, old_filename)
            intermediate_path = os.path.join(folder_path, intermediate_filename)

            try:
                os.rename(old_path, intermediate_path)
                intermediate_files.append(intermediate_filename)
            except OSError as e:
                print(f"    ERROR renaming {old_filename} in PASS 1: {e}")
        
    
    # ==========================================================
    # PASS 2: Rename from Intermediate (8xxx) to Final (0xxx)
    # ==========================================================
    print("  PASS 2: Renaming from temporary 8xxx to final 0xxx sequence...")

    # We must process the intermediate_files in the same order to preserve the sequence
    intermediate_files.sort()
    
    # Recalculate the sequence for the final names
    for index, temp_filename in enumerate(intermediate_files):
        # The number is already sequential, but now we'll format it with '0'
        new_number_int = index + 1
        
        # Format as 4 digits, ensuring leading zeros (e.g., 1 -> 0001)
        final_number_str = f"{new_number_int:04d}" 

        # We rely on the fact that the intermediate file still matches the original PATTERN_4_DIGITS
        match = PATTERN_4_DIGITS.match(temp_filename)
        if match:
            start_part = match.group(1)
            end_part = match.group(3)
            
            # Construct the final filename
            final_filename = f"{start_part}{final_number_str}{end_part}"

            intermediate_path = os.path.join(folder_path, temp_filename)
            final_path = os.path.join(folder_path, final_filename)

            try:
                os.rename(intermediate_path, final_path)
                print(f"    Final Renamed: {temp_filename} -> {final_filename}")
                files_renamed_in_folder += 1
            except OSError as e:
                print(f"    ERROR renaming {temp_filename} in PASS 2: {e}")
    
    return total_renamed_count + files_renamed_in_folder


def traverse_and_rename(source_dir):
    """
    Recursively traverses the source directory and calls the renaming function
    for each folder, tracking the total count.
    """
    total_renamed_count = 0
    
    # Walk the directory structure
    for root, dirs, files in os.walk(source_dir):
        # The function returns the updated total count
        total_renamed_count = rename_files_in_folder(root, total_renamed_count)
        
    return total_renamed_count


def main():
    # 1. Setup argparse
    parser = argparse.ArgumentParser(
        description="Recursively rename files in folders using a double-pass system (8xxx intermediate) to ensure sequential 0001-to-X numbering in reverse file order.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Use -d or --source_dir
    parser.add_argument(
        '-d', 
        '--source_dir',
        nargs='?', 
        default=None,
        help='The source directory path where files will be renamed.'
    )

    args = parser.parse_args()

    source_dir = args.source_dir

    # 2. Handle missing source_dir by prompting the user
    if source_dir is None:
        source_dir = input("Please enter the source directory path: ")

    # 3. Validate and clean the path
    source_dir = os.path.abspath(source_dir)

    if not os.path.isdir(source_dir):
        print(f"Error: Directory not found at '{source_dir}'")
        sys.exit(1)

    print("-" * 60)
    print(f"Starting double-pass file rename process in: {source_dir}")
    print(f"Pass 1: Renames to temporary {INTERMEDIATE_PREFIX}xxx format.")
    print(f"Pass 2: Renames to final {FINAL_PREFIX}xxx (0001-to-X) format.")
    print("-" * 60)

    # 4. Execute the renaming process and get the total count
    try:
        total_renamed = traverse_and_rename(source_dir)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        total_renamed = 0 

    # 5. Print the final sum
    print("-" * 60)
    print("File renaming process complete.")
    print(f"✅ Total files successfully renamed (two passes completed): {total_renamed}")
    print("-" * 60)


if __name__ == "__main__":
    main()