import os
import subprocess
import shutil
from tqdm import tqdm

# ANSI Escape Codes for formatting
ANSI_BOLD = "\033[1m"
ANSI_BLINK = "\033[5m"
ANSI_BRIGHT_RED = "\033[91m"
ANSI_RESET = "\033[0m"


def process_and_compress_tiffs(target_directory):
    """
    Finds all TIFF files in a directory and its subdirectories and applies
    image enhancements and LZW compression, saving the result to a new file 
    with a '.new.tiff' suffix.

    Args:
        target_directory (str): The root directory to start scanning for files.
    """
    if not os.path.isdir(target_directory):
        print(f"Error: The provided path '{target_directory}' is not a valid directory.")
        return

    # Check if 'magick' command is available on the system's PATH
    if shutil.which('magick') is None:
        print("Error: 'magick' command not found.")
        print("Please ensure ImageMagick is installed and its 'magick' executable is in your system's PATH.")
        return

    print(f"Scanning for TIFF files to process and compress in '{target_directory}'...")

    files_to_process = []
    for root, _, files in os.walk(target_directory):
        for filename in files:
            # Check for TIFF files (case-insensitive)
            if filename.lower().endswith(('.tif', '.tiff')):
                files_to_process.append(os.path.join(root, filename))

    if not files_to_process:
        print("No TIFF files found in the specified directory or its subdirectories.")
        return

    print(f"Found {len(files_to_process)} TIFF files to process.")
    
    # Safety confirmation step is removed since original files are not overwritten.
    print("\nNOTE: This script will NOT modify original files. It will create new '.new.tiff' files.")
    confirmation = input("Are you sure you want to proceed? (yes/no): ").lower().strip()

    if confirmation != 'yes':
        print("Operation cancelled by user.")
        return

    print("Starting image processing and compression...")
    
    # Wrap the loop with tqdm for a progress bar
    with tqdm(total=len(files_to_process), desc="Applying enhancements and compression", unit="file") as pbar:
        for file_path in files_to_process:
            pbar.set_description(f"Processing ({os.path.basename(file_path)})")
            
            # --- CREATE NEW FILE PATH ---
            # Construct the new output filename with the desired suffix
            base, ext = os.path.splitext(file_path)
            new_file_path = base + ".new" + ext
            # ----------------------------

            # Construct the full 'magick' command
            command = [
                'magick',
                file_path,                               # 1. Input file
                # --- STEP 1: CONTINUOUS LEVEL MAPPING ---
                # Clips the paper background smoothly to white while protecting photo midtones
                '-level', '14%,90%,0.95', 
                # --- STEP 2: WHITE MARGIN CLEANUP ---
                # Safely forces the absolute brightest 0.5% of pixels (the margins) to pure white
                '-contrast-stretch', '0.5%x0.5%', 
                # --- STEP 3: TEXT SHARPENING ---
                # Tends to text crispness without introducing edge artifacts in photos
                '-unsharp', '0x1.2+1.2+0.03', 
                # --- STEP 4: OUTPUT COMPRESSION ---
                '-strip',                                # Removes heavy scanner profiles/hidden metadata
                '-compress', 'lzw',                      
                new_file_path                            # Output file
            ]

            try:
                # Execute the complex 'magick' command
                subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                pbar.set_postfix_str(f"Success -> {os.path.basename(new_file_path)}")
            except subprocess.CalledProcessError as e:
                pbar.set_postfix_str("Failed")
                print(f"\nError processing file '{file_path}': {e}")
            except FileNotFoundError:
                pbar.set_postfix_str("Magick not found")
                print("\nError: 'magick' command not found. Please ensure ImageMagick is installed.")
                return

            pbar.update(1)
            
    print("\nImage processing and LZW compression complete. New files were saved with the '.new.tiff' suffix.")


if __name__ == "__main__":
    # The default path to use if the user doesn't enter anything
    DEFAULT_DIR = r"D:\Georgetown_News_Graphic\Working_Folder"
    
    # Prompt the user for input
    target_dir = input(f"Please enter the full path to the root directory containing the TIFF files (or press Enter for default: {DEFAULT_DIR}): ")
    
    # Check if the input is empty or just whitespace
    if not target_dir.strip():
        print(f"Input was blank. Using default directory: {DEFAULT_DIR}")
        target_dir = DEFAULT_DIR
    
    # Print statement with ANSI codes
    formatted_target_dir = f"{ANSI_BOLD}{ANSI_BRIGHT_RED}{ANSI_BLINK}{target_dir}{ANSI_RESET}"
    print(f"Using {formatted_target_dir}")
    
    process_and_compress_tiffs(target_dir)