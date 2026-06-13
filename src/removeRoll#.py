import os
import re
import argparse
import sys

def rename_pdf_files(target_directory):
    """
    Searches recursively for PDF files matching "Roll #### SCPL yyyyMMdd.pdf" 
    and renames them to "SCPL yyyyMMdd.pdf" by removing the 'Roll #### ' prefix.

    Args:
        target_directory (str): The root directory to start searching from.
    """
    if not os.path.isdir(target_directory):
        print(f"Error: The provided path '{target_directory}' is not a valid directory. ❌")
        return

    # Regex to match the desired pattern and capture the parts we want to keep.
    # We use \d{4} for the Roll number, \s+ for one or more spaces, and (\.pdf) for the extension.
    # Group 1: SCPL
    # Group 2: yyyyMMdd
    # Group 3: The extension (.pdf)
    filename_pattern = re.compile(r"Roll\s+\d{4}\s+(SCPL)\s+(\d{8})(\.pdf)$", re.IGNORECASE)

    print(f"Starting file renaming process in '{target_directory}'...")
    renamed_count = 0
    skipped_count = 0

    # 3. Recurses directories using os.walk
    for root, _, files in os.walk(target_directory):
        for filename in files:
            match = filename_pattern.match(filename)
            
            if match:
                # Capture the groups needed for the new filename
                scpl_part = match.group(1)    # "SCPL"
                date_part = match.group(2)    # yyyyMMdd
                extension_part = match.group(3) # .pdf

                # 2. Construct the new filename (without "Roll #### ")
                new_filename = f"{scpl_part} {date_part}{extension_part}"

                old_filepath = os.path.join(root, filename)
                new_filepath = os.path.join(root, new_filename)

                try:
                    if os.path.exists(new_filepath):
                        print(f"Skipping: New filename '{new_filename}' already exists in '{root}'. ⚠️")
                        skipped_count += 1
                        continue

                    os.rename(old_filepath, new_filepath)
                    print(f"Renamed: '{filename}' to '{new_filename}' in '{root}'")
                    renamed_count += 1
                except OSError as e:
                    print(f"Error renaming '{filename}' in '{root}': {e} 🛑")
                    skipped_count += 1
                except Exception as e:
                    print(f"An unexpected error occurred with '{filename}': {e} 🛑")
                    skipped_count += 1

    print(f"\nFile renaming process completed. ✅")
    print(f"Total files renamed: {renamed_count}")
    print(f"Total files skipped (due to conflicts/errors): {skipped_count}")

# --- Main Execution Block ---
if __name__ == "__main__":
    # 5. Define the command line option for the target directory
    parser = argparse.ArgumentParser(
        description="Rename PDFs by removing the 'Roll #### ' prefix.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "--target_dir",
        help="The root directory to start searching files from. If not provided, you will be prompted."
    )
    
    args = parser.parse_args()

    target_directory = args.target_dir

    # 4. Request the target directory if one is not provided
    if not target_directory:
        print("Directory path was not provided via '--target_dir'.")
        target_directory = input(
            "Enter the starting directory for PDF renaming (e.g., 'C:\\MyDocs' or '.' for current directory): "
        )
    
    # Run the renaming function
    rename_pdf_files(target_directory)