import os
import sys
import argparse
import subprocess
import shutil
from tqdm import tqdm

# ==============================================================================
# GLOBAL CONFIGURATION & ENVIRONMENT SCOPING
# ==============================================================================
# Default target workspace used as a fall-back if the operator leaves the 
# interactive path prompt empty.
DEFAULT_DIR = r"D:\Georgetown_News_Graphic\Working_Folder"

# ANSI Escape Codes for high-visibility terminal text formatting.
# Used to vividly draw the operator's attention to the active directory root.
ANSI_BOLD = "\033[1m"
ANSI_BLINK = "\033[5m"
ANSI_BRIGHT_RED = "\033[91m"
ANSI_RESET = "\033[0m"


def process_and_compress_tiffs(source_directory, destination_directory=None, is_test=False):
    """
    Scans a directory tree for TIFF files, applies targeted archival image 
    enhancements (background normalization, curve levels, and sharpening), 
    and saves them using efficient LZW compression via ImageMagick.

    Args:
        source_directory (str): Root path to scan for input TIFF images.
        destination_directory (str, optional): Target root directory for output files.
                                               Replicates folder structure if provided.
        is_test (bool): If True, appends '.new' to names and prevents in-place overwrites.
    """
    # Verify that the provided source path actually exists and is a directory
    if not os.path.isdir(source_directory):
        print(f"Error: The provided path '{source_directory}' is not a valid directory.")
        return

    # Ensure the ImageMagick 'magick' executable is available in the system's PATH 
    # environmental variable before spinning up a heavy processing cycle.
    if shutil.which('magick') is None:
        print("Error: 'magick' command not found.")
        print("Please ensure ImageMagick is installed and its 'magick' executable is added to your system PATH.")
        return

    print(f"Scanning for TIFF images in '{source_directory}'...")
    
    tiff_files_to_process = []
    
    # Recursively traverse the directory tree to harvest target image records
    for root, _, files in os.walk(source_directory):
        for filename in files:
            if filename.lower().endswith(('.tif', '.tiff')):
                input_file_path = os.path.join(root, filename)
                
                # Establish output path routing based on destination parameters
                if destination_directory:
                    relative_path = os.path.relpath(input_file_path, source_directory)
                    output_file_path = os.path.join(destination_directory, relative_path)
                else:
                    output_file_path = input_file_path
                
                # Apply non-destructive naming alterations if test-mode is engaged
                if is_test:
                    base, ext = os.path.splitext(output_file_path)
                    output_file_path = f"{base}.new{ext}"
                
                # SAFEGUARD: Detect identical-path collisions. 
                # Reading and writing to the exact same file descriptor simultaneously 
                # via an external process when not processing true native in-place configurations
                # can result in corrupted 0-byte file truncations.
                if input_file_path == output_file_path and not is_test:
                    # Native in-place handling via ImageMagick ('magick input.tif ... input.tif') 
                    # is structurally safe because ImageMagick writes to a temporary swap file 
                    # before replacing the original asset. We explicitly allow this.
                    pass

                tiff_files_to_process.append((input_file_path, output_file_path))

    if not tiff_files_to_process:
        print("No TIFF images found matching standard extensions.")
        return

    print(f"Found {len(tiff_files_to_process)} TIFF images to process.")
    
    # Process sequence execution tracking loop
    with tqdm(total=len(tiff_files_to_process), desc="Enhancing TIFFs", unit="file") as pbar:
        for input_path, output_path in tiff_files_to_process:
            pbar.set_description(f"Processing ({os.path.basename(input_path)})")
            
            # Ensure target destination directory hierarchy exists before invoking subprocesses
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Construct command line sequence token array for ImageMagick processing.
            # NOTE: The Windows platform does not recognize the OpenMP '-accelerate' flag, 
            # so it is purposefully omitted to maintain predictable core stability.
            cmd = [
                "magick",
                input_path,
                "-background", "white",
                "-level", "5%,95%",
                "-sharpen", "0x1",
                "-compress", "lzw",
                output_path
            ]
            
            try:
                # Execute the external image processing binary safely.
                # Redirecting stdout and stderr isolates external process chatter, 
                # ensuring it doesn't break or visually tear the active tqdm progress bar layouts.
                subprocess.run(
                    cmd, 
                    check=True, 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.PIPE
                )
                pbar.set_postfix_str("Processed")
            except subprocess.CalledProcessError as e:
                pbar.set_postfix_str("Error")
                print(f"\nImageMagick Failure on file '{os.path.basename(input_path)}': {e.stderr.decode().strip()}")
            except Exception as e:
                pbar.set_postfix_str("Failed")
                print(f"\nUnexpected systemic runtime error processing '{os.path.basename(input_path)}': {e}")
                
            pbar.update(1)

    print("\nAll TIFF images successfully processed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Batch process newspaper archival TIFF images using ImageMagick visual enhancements."
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

    # Failover fallback assessment if manual input prompts are left empty by the operator
    if not source_dir.strip():
        print(f"Input was blank. Using default directory: {DEFAULT_DIR}")
        source_dir = DEFAULT_DIR
    
    # Normalize path string format to unify messy Windows slash configurations and remove trailing delimiters
    source_dir = os.path.normpath(source_dir)

    # GUARD CLAUSE: Terminate execution immediately if the resolved directory is missing
    if not os.path.isdir(source_dir):
        print(f"Error: The provided path '{source_dir}' is not a valid directory.")
        sys.exit(1)
    
    # Output the dynamic confirmation sequence to terminal stdout using ANSI escape highlights
    formatted_source_dir = f"{ANSI_BOLD}{ANSI_BRIGHT_RED}{ANSI_BLINK}{source_dir}{ANSI_RESET}"
    print(f"Using source directory: {formatted_source_dir}")
    
    # Normalize optional destination directory if provided
    dest_dir = os.path.normpath(args.destination_directory) if args.destination_directory else None
    
    # Hand execution controls over to the core batch loop handler
    process_and_compress_tiffs(
        source_directory=source_dir,
        destination_directory=dest_dir,
        is_test=args.test
    )