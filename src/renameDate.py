import os
import re
import argparse
import sys

def rename_files(directory, old_date, new_date):
    """
    Renames files in a directory by replacing a specific date string.

    Args:
        directory (str): The path to the directory containing the files.
        old_date (str): The date string to find (e.g., '20250520').
        new_date (str): The date string to replace it with (e.g., '20250523').
    """
    if not os.path.isdir(directory):
        print(f"Error: Directory not found at '{directory}'")
        return

    # 1. Define the pattern to look for the old date
    pattern = re.compile(re.escape(old_date))
    
    # 2. Define the expected file prefix for targeted renaming
    prefix = "Roll 0001 SCPL"
    suffix = ".tif"
    
    print(f"\n--- Starting File Rename Operation ---")
    print(f"Directory: {directory}")
    print(f"Replacing '{old_date}' with '{new_date}'")
    print(f"--------------------------------------")
    
    renamed_count = 0
    
    try:
        # Loop through all items in the directory
        for filename in os.listdir(directory):
            # Check if the filename matches the expected structure and contains the old date
            if filename.startswith(prefix) and filename.endswith(suffix) and pattern.search(filename):
                
                # Create the new filename by substituting the old date
                new_filename = pattern.sub(new_date, filename)
                
                # Construct the full paths
                old_path = os.path.join(directory, filename)
                new_path = os.path.join(directory, new_filename)

                # Check to prevent accidental renaming (e.g., if old_date == new_date)
                if filename != new_filename:
                    print(f"Renaming: '{filename}'")
                    print(f"      To: '{new_filename}'")
                    
                    # Perform the actual rename
                    os.rename(old_path, new_path)
                    renamed_count += 1
                
    except Exception as e:
        print(f"\nAn error occurred during processing: {e}")
        return

    print(f"\n--- Rename Complete ---")
    print(f"Successfully renamed {renamed_count} files.")
    print(f"-----------------------")


def main():
    # Define the default directory path
    DEFAULT_DIR = r"D:\Georgetown_News_Graphic\Working_Folder"
    
    parser = argparse.ArgumentParser(
        description="Batch renames TIFF files by replacing a specific date string."
    )
    
    # Set required=False for dates so we can handle missing input interactively
    parser.add_argument(
        '-old_date', 
        type=str, 
        default=None,
        help="The date string to find and replace (e.g., 20250520)."
    )
    parser.add_argument(
        '-new_date', 
        type=str, 
        default=None,
        help="The replacement date string (e.g., 20250523)."
    )
    parser.add_argument(
        '-directory', 
        type=str, 
        default=None, 
        help=f"The target directory. Default is: {DEFAULT_DIR}"
    )
    
    # --- Check if NO arguments were provided ---
    # len(sys.argv) == 1 means only the script name itself was passed.
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    # Parse the arguments
    args = parser.parse_args()
    
    # --- Interactive Input Check ---
    # (These will trigger only if at least ONE argument was provided, but others are missing)
    
    # 1. Check for directory
    if args.directory is None:
        print(f"Default directory is: {DEFAULT_DIR}")
        dir_input = input("Enter target directory (or press ENTER to use default): ").strip()
        
        if dir_input:
            args.directory = dir_input
        else:
            args.directory = DEFAULT_DIR

    # 2. Check for old_date
    if args.old_date is None:
        while True:
            date_input = input("Enter the OLD date (e.g., 20250520): ").strip()
            if date_input:
                args.old_date = date_input
                break
            print("Old date cannot be blank. Please enter a value.")

    # 3. Check for new_date
    if args.new_date is None:
        while True:
            date_input = input("Enter the NEW date (e.g., 20250523): ").strip()
            if date_input:
                args.new_date = date_input
                break
            print("New date cannot be blank. Please enter a value.")
            
    # -------------------------------

    # Call the main renaming function
    rename_files(args.directory, args.old_date, args.new_date)


if __name__ == "__main__":
    main()