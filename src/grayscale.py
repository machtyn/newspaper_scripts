import os
import sys
import argparse
from PIL import Image
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

# ANSI Escape Codes for console text formatting
ANSI_BOLD = "\033[1m"
ANSI_BRIGHT_RED = "\033[91m"
ANSI_BLINK = "\033[5m"
ANSI_RESET = "\033[0m"

def convert_to_grayscale(input_image_path, output_image_path):
    """
    Converts a TIFF image to grayscale and saves it to a specified path,
    preserving the original DPI/PPI.

    Returns:
        tuple: (bool, str) indicating success/failure status and the filename.
    """
    filename = os.path.basename(input_image_path)
    try:
        with Image.open(input_image_path) as img:
            if img.format != 'TIFF':
                return False, filename

            original_dpi = img.info.get('dpi')

            # Convert to grayscale ('L' mode is 8-bit pixels, black and white)
            grayscale_img = img.convert('L') 
            
            # Ensure the output subdirectory structure exists
            os.makedirs(os.path.dirname(output_image_path), exist_ok=True)

            # Save the grayscale image, preserving DPI
            if original_dpi:
                grayscale_img.save(output_image_path, dpi=original_dpi)
            else:
                grayscale_img.save(output_image_path)
            
            return True, filename

    except Exception:
        return False, filename

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
         description="Batch convert color TIFF images to grayscale while preserving DPI."
    )
    parser.add_argument(
        "-s",
        "--source_directory",
        type=str,
        help="The full path to the 'Color' root folder containing your source TIFF images.",
    )
    parser.add_argument(
        "-d",
        "--destination_directory",
        type=str,
        help="The destination path where your grayscale TIFF files should be written.",
    )
    args = parser.parse_args()

    # Route source directory
    if args.source_directory:
        source_dir = args.source_directory
    else:
        source_dir = input("Please enter the full path to the 'Color' root folder (e.g., C:\\Images\\Color): ")
   
    DEFAULT_DIR = r"D:\Georgetown_News_Graphic\Working_Folder"

    if not source_dir.strip():
        print(f"Input was blank. Using default directory: {DEFAULT_DIR}")
        source_dir = DEFAULT_DIR
    
    # Normalize path to clear trailing slashes safely
    source_dir = os.path.normpath(source_dir)

    # CRITICAL FIX: Guard clause to prevent execution on invalid directory
    if not os.path.isdir(source_dir):
        print(f"Error: The provided path '{source_dir}' is not a valid directory.")
        sys.exit(1)

    formatted_source_dir = f"{ANSI_BOLD}{ANSI_BRIGHT_RED}{ANSI_BLINK}{source_dir}{ANSI_RESET}"
    print(f"Using source directory: {formatted_source_dir}")

    # Resolve output destination path safely
    if args.destination_directory:
        grayscale_root_dir = os.path.normpath(args.destination_directory)
    else:
        # Sibling fallback strategy (Grayscale folder next to Color folder)
        parent_dir = os.path.dirname(source_dir)
        grayscale_root_dir = os.path.join(parent_dir, "Grayscale")
    
    os.makedirs(grayscale_root_dir, exist_ok=True)
    print(f"Grayscale images will be saved to: '{grayscale_root_dir}'")
    print(f"Scanning for TIFF images in '{source_dir}' and its subdirectories...")

    # Gather files to process
    tiff_files_to_process = []
    for root, _, files in os.walk(source_dir):
        for filename in files:
            if filename.lower().endswith(('.tif', '.tiff')):
                input_file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(input_file_path, source_dir)
                output_file_path = os.path.join(grayscale_root_dir, relative_path)
                tiff_files_to_process.append((input_file_path, output_file_path))

    if not tiff_files_to_process:
        print("No TIFF images found in the specified directory or its subdirectories.")
        sys.exit(0)

    print(f"Found {len(tiff_files_to_process)} TIFF images to convert.")
    
    # Use max available CPU cores minus 2 to prevent machine freezing
    max_workers = max(1, os.cpu_count() - 2)
    print(f"Initializing parallel processing queue with {max_workers} worker cores...")

    # Execute batch processing using concurrent workers
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks to the pool
        futures = {
            executor.submit(convert_to_grayscale, inp, out): (inp, out) 
            for inp, out in tiff_files_to_process
        }
        
        # Track progress dynamically across threads
        with tqdm(total=len(futures), desc="Converting to Grayscale", unit="file") as pbar:
            for future in as_completed(futures):
                success, filename = future.result()
                pbar.set_description(f"Processing ({filename})")
                
                if success:
                    pbar.set_postfix_str("Converted")
                else:
                    pbar.set_postfix_str("Skipped/Error")
                pbar.update(1)

    print("All TIFF images processed for grayscale conversion.")