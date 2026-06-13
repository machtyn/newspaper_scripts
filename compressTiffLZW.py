import os
import subprocess
import shutil
from tqdm import tqdm
from datetime import datetime
import concurrent.futures
import multiprocessing

# ANSI Escape Codes for formatting
ANSI_BOLD = "\033[1m"
ANSI_BLINK = "\033[5m"
ANSI_BRIGHT_RED = "\033[91m"
ANSI_RESET = "\033[0m"

# Define the allowed core limits
ALLOWED_CORES = [3, 6]
DEFAULT_CORES = 3


def process_file_with_magick(file_path):
    """
    Constructs and executes the ImageMagick command for a single file.
    Relies on ImageMagick's native multi-threading (OpenMP) for speed.
    """
    
    # --- ImageMagick Command Construction ---
    command = [
        'magick',
        '-define', 'opencl:device=GPU',           # Enable OpenCL
        file_path,                                # 1. Input file
        '(', '+clone', '-vignette', '0x600-0+0', '-negate', ')', # 2. Devignette stack
        '-compose', 'Multiply', '-composite',     # 3. Composite for devignette
        '-modulate', '85,115,100',               # 4. Brightness 85, Saturation 115
        '-sigmoidal-contrast', '5,30%',           # 5. Contrast 30
        '-sharpen', '0x3.0',                      # 6. Sharpening 30
        '-level', '35%,100%,0.60',                # 7. GIMP Input Levels
        '-compress', 'lzw',                      # 8. LZW Compression
        file_path                                # 9. Output file (OVERWRITES original)
    ]
    
    filename = os.path.basename(file_path)

    try:
        # Execute the complex 'magick' command. 
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, filename, ""
    except subprocess.CalledProcessError as e:
        return False, filename, f"Command failed with return code {e.returncode}"
    except FileNotFoundError:
        return False, filename, "'magick' command not found. Ensure ImageMagick is installed."
    except Exception as e:
        return False, filename, str(e)


def process_and_compress_tiffs(target_directory, max_workers):
    """
    Finds all TIFF files and processes them in parallel using a limited number of cores.
    """
    if not os.path.isdir(target_directory):
        print(f"Error: The provided path '{target_directory}' is not a valid directory.")
        return

    if shutil.which('magick') is None:
        print("Error: 'magick' command not found.")
        print("Please ensure ImageMagick is installed and its 'magick' executable is in your system's PATH.")
        return

    print(f"Scanning for TIFF files to process and compress in '{target_directory}'...")

    files_to_process = []
    # Recursively find all TIFF files
    for root, _, files in os.walk(target_directory):
        for filename in files:
            if filename.lower().endswith(('.tif', '.tiff')):
                files_to_process.append(os.path.join(root, filename))

    if not files_to_process:
        print("No TIFF files found in the specified directory or its subdirectories.")
        return

    print(f"Found {len(files_to_process)} TIFF files to process.")
    
    print("\nWARNING: This script WILL modify and **OVERWRITE** the original files in place.")
    print(f"Processing will run concurrently using **{max_workers}** dedicated processes.")
    confirmation = input("Are you sure you want to proceed? (yes/no): ").lower().strip()

    if confirmation != 'yes':
        print("Operation cancelled by user.")
        return

    print("Starting image processing and compression...")
    
    start_time = datetime.now()
    
    # --- PARALLEL EXECUTION USING PROCESS POOL ---
    processed_count = 0
    failed_files = []
    
    # Using ProcessPoolExecutor to truly utilize multiple CPU cores
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Map the processing function to all files
        results = executor.map(process_file_with_magick, files_to_process)
        
        # Wrap the results iteration with tqdm for a dynamic progress bar
        for success, filename, error in tqdm(results, total=len(files_to_process), 
                                             desc="Parallel Processing", unit="file"):
            if success:
                processed_count += 1
            else:
                failed_files.append((filename, error))
                print(f"\nFailed to process {filename}: {error}")
    # --------------------------------------------
            
    end_time = datetime.now()
    total_time = end_time - start_time
    time_str = str(total_time).split('.')[0]
    
    print("\nImage processing and LZW compression complete.")
    print(f"Total files processed: {processed_count}")
    print(f"Files that failed: {len(failed_files)}")
    print(f"Total time taken: {ANSI_BOLD}{time_str}{ANSI_RESET}")


if __name__ == "__main__":
    # Define the default directory path
    DEFAULT_DIR = r"D:\Georgetown_News_Graphic\Working_Folder"
    
    # --- CORE SELECTION ---
    while True:
        cores_input = input(f"Enter number of cores to use ({ALLOWED_CORES[0]} or {ALLOWED_CORES[1]}) [Default: {DEFAULT_CORES}]: ").strip()
        
        if not cores_input:
            # Use default if input is blank
            MAX_WORKERS = DEFAULT_CORES
            print(f"Using default core count: {MAX_WORKERS}")
            break
        
        try:
            cores = int(cores_input)
            if cores in ALLOWED_CORES:
                MAX_WORKERS = cores
                break
            else:
                print(f"Invalid input. Please enter {ALLOWED_CORES[0]} or {ALLOWED_CORES[1]}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    # ----------------------
    
    # Directory input
    target_dir = input(f"Please enter the full path to the root directory containing the TIFF files (or press Enter for default: {DEFAULT_DIR}): ")
    
    if not target_dir.strip():
        print(f"Input was blank. Using default directory: {DEFAULT_DIR}")
        target_dir = DEFAULT_DIR
    
    # Print statement with ANSI codes
    formatted_target_dir = f"{ANSI_BOLD}{ANSI_BRIGHT_RED}{ANSI_BLINK}{target_dir}{ANSI_RESET}"
    print(f"Using {formatted_target_dir}")
    
    # Pass the selected core count to the processing function
    process_and_compress_tiffs(target_dir, MAX_WORKERS)