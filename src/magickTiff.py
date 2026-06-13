import os
import argparse
import subprocess
import shutil
from tqdm import tqdm

# ANSI Escape Codes for console text formatting and visibility
ANSI_BOLD = "\033[1m"
ANSI_BLINK = "\033[5m"
ANSI_BRIGHT_RED = "\033[91m"
ANSI_RESET = "\033[0m"


def process_and_compress_tiffs(source_directory, destination_directory=None, is_test=False):
    """
    Scans a directory tree for TIFF files, applies targeted archival image 
    enhancements (background normalization, curve levels, and sharpening), 
    and saves them using efficient LZW compression.

    Args:
        source_directory (str): Root path to scan for input TIFF images.
        destination_directory (str, optional): Target root directory for output files.
        is_test (bool): If True, appends '.new' to names and prevents in-place overwrites.
    """
    # Verify that the provided source path actually exists and is a directory
    if not os.path.isdir(source_directory):
        print(f"Error: The provided path '{source_directory}' is not a valid directory.")
        return

    # Ensure the ImageMagick 'magick' executable is available in the system's PATH environmental variable
    if shutil.which('magick') is None:
        print("Error: 'magick' command not found.")
        print("Please ensure ImageMagick is installed and its 'magick' executable is in your system's PATH.")
        return

    print(f"Scanning for TIFF files to process and compress in '{source_directory}'...")

    # Recursively traverse the directory tree to find eligible image targets
    files_to_process = []
    for root, _, files in os.walk(source_directory):
        for filename in files:
            # Match both standard .tiff and short .tif extensions case-insensitively
            if filename.lower().endswith(('.tif', '.tiff')):
                files_to_process.append(os.path.join(root, filename))

    # Exit safely if no target files match the required criteria
    if not files_to_process:
        print("No TIFF files found in the specified directory or its subdirectories.")
        return

    print(f"Found {len(files_to_process)} TIFF files to process.")
    
    # --- RUNTIME MODE VALIDATION & SAFETY WARNINGS ---
    # Present a context-specific warning depending on the destructive risk of the current parameters
    need_confirm = True
    if is_test:
        print("\nNOTE: Test mode active. New files will append '.new.tiff' and originals will NOT be modified.")
        need_confirm = False
    if destination_directory:
        print(f"\nNOTE: Output files will be mirrored into destination: {destination_directory}. Originals will NOT be modified.")
        need_confirm = False

    if need_confirm:
        # Hard warning if running without flags, which results in modifying production data in-place
        print(f"\n{ANSI_BOLD}{ANSI_BRIGHT_RED}🚨 WARNING: No test flag or destination directory provided. This will OVERWRITE original files in place!{ANSI_RESET}")
        # Require explicit user intent before kicking off bulk disk input/output loops
        confirmation = input("Are you sure you want to proceed? (yes/no): ").lower().strip()
        if confirmation != 'yes':
            print("Operation cancelled by user.")
            return

    print("Starting image processing and compression...")
    
    # Initialize the progress bar with tracking units focused on total discovered files
    with tqdm(total=len(files_to_process), desc="Applying enhancements and compression", unit="file") as pbar:
        for file_path in files_to_process:
            # Update progress bar label to indicate which file is actively being worked on
            pbar.set_description(f"Processing ({os.path.basename(file_path)})")
            
            # Determine target director and filename
            if destination_directory:
                # Replicate the nested subfolder hierarchy inside the new destination root
                rel_dir = os.path.relpath(os.path.dirname(file_path), source_directory)
                out_dir = os.path.join(destination_directory, rel_dir)
                os.makedirs(out_dir, exist_ok=True)
                target_base_path = os.path.join(out_dir, os.path.basename(file_path))
            else:
                # Working in place
                target_base_path = file_path

            if is_test:
                base, ext = os.path.splitext(target_base_path)
                new_file_path = f"{base}.new{ext}"
            else:
                new_file_path = target_base_path
            # ----------------------------------

            # Assemble the fine-tuned ImageMagick processing arguments list
            command = [
                'magick',
                file_path,                               # Source input file path
                # --- STEP 1: CONTINUOUS LEVEL MAPPING ---
                # Sets the dark threshold to 14% to deepen gray text, cleans paper aging to pure white 
                # at 90%, and maintains photo tones using a gentle 0.95 midtone gamma correction curve.
                '-level', '14%,90%,0.95', 
                # --- STEP 2: WHITE MARGIN CLEANUP ---
                # Drops the extreme 0.5% outliers on both ends of the histogram to strip border dust and noise.
                '-contrast-stretch', '0.5%x0.5%', 
                # --- STEP 3: TEXT SHARPENING ---
                # Sharpens edges using a tight unsharp mask radius to bridge broken font loops without creating photo artifacts.
                '-unsharp', '0x1.2+1.2+0.03', 
                # --- STEP 4: METADATA & COMPRESSION CLEANUP ---
                '-strip',                                # Drops bloated scanner profiles, thumbnails, and custom tags
                '-compress', 'lzw',                      # Applies standard archival-safe LZW compression
                new_file_path                            # Resulting destination output path
            ]

            try:
                # Dispatch execution to ImageMagick, hiding verbose streams unless an error raises
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
            
    print("\nImage processing and compression complete.")


if __name__ == "__main__":
    # Configure the command line interface parser layout
    parser = argparse.ArgumentParser(
         description="Batch clean, adjust curves, and compress archive TIFF files using ImageMagick."
    )
    parser.add_argument(
        "-s",
        "--source_directory",
        type=str,
        help="The full path to the directory containing your source TIFF images.",
    )
    parser.add_argument(
        "-d",
        "--destination_directory",
        type=str,
        help="The destination path where your processed TIFF files should be written.",
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Run script in test mode. Appends '.new' to filenames and protects originals from manipulation.",
    )
    args = parser.parse_args()

    # Route source directories based on whether flags were passed or manual fallbacks are required
    if args.source_directory:
        source_dir = args.source_directory
    else:
        source_dir = input("Please enter the full path to the directory containing your TIFF images: ")
   
    # Failover fallback variable if manual input prompts are left empty by the operator
    DEFAULT_DIR = r"D:\Georgetown_News_Graphic\Working_Folder"

    if not source_dir.strip():
        print(f"Input was blank. Using default directory: {DEFAULT_DIR}")
        source_dir = DEFAULT_DIR
    
    # Output the dynamic confirmation sequence to terminal stdout using ANSI escape highlights
    formatted_source_dir = f"{ANSI_BOLD}{ANSI_BRIGHT_RED}{ANSI_BLINK}{source_dir}{ANSI_RESET}"
    print(f"Using source directory: {formatted_source_dir}")
    
    # Hand execution controls over to the core batch loop handler
    process_and_compress_tiffs(
        source_directory=source_dir,
        destination_directory=args.destination_directory,
        is_test=args.test
    )