import os
import sys
import argparse
from PIL import Image
from tqdm import tqdm

# ANSI Escape Codes for console text formatting
ANSI_BOLD = "\033[1m"
ANSI_BRIGHT_RED = "\033[91m"
ANSI_BLINK = "\033[5m"
ANSI_RESET = "\033[0m"

def create_pdf_from_tiffs(source_directory, destination_directory=None):
    """
    Finds all subdirectories containing TIFF files and creates a single PDF
    from those TIFFs, saving it to the parent directory of the subfolder
    (or to a mirrored structure in the destination directory if provided).

    Args:
        source_directory (str): The top-level directory to start scanning.
        destination_directory (str, optional): Target root directory for output PDFs.
    """
    print(f"Scanning for TIFF files in subdirectories of '{source_directory}'...")
    
    directories_to_process = []
    for root, dirs, files in os.walk(source_directory):
        tiff_files_in_dir = sorted([os.path.join(root, f) for f in files if f.lower().endswith(('.tif', '.tiff'))])
        if tiff_files_in_dir:
            directories_to_process.append((root, tiff_files_in_dir))

    if not directories_to_process:
        print("No TIFF files found in any subdirectories. Exiting.")
        return

    print(f"Found {len(directories_to_process)} directories to process.")
    
    # Outer progress bar for directories
    with tqdm(total=len(directories_to_process), desc="Converting directories to PDF", unit="dir", position=0) as pbar_dirs:
        for directory_path, tiff_file_paths in directories_to_process:
            pdf_filename = os.path.basename(directory_path) + ".pdf"
            
            if destination_directory:
                # Replicate nested hierarchy into destination root safely
                rel_dir = os.path.relpath(directory_path, source_directory)
                out_dir = os.path.join(destination_directory, rel_dir)
                # We want the PDF to sit alongside the images' destination directory clone
                pdf_output_path = os.path.normpath(os.path.join(os.path.dirname(out_dir), pdf_filename))
            else:
                # Fallback to the parent directory of the target subfolder
                parent_dir = os.path.dirname(directory_path)
                pdf_output_path = os.path.join(parent_dir, pdf_filename)
            
            # Ensure target directory structure exists
            os.makedirs(os.path.dirname(pdf_output_path), exist_ok=True)
            pbar_dirs.set_description(f"Processing '{os.path.basename(directory_path)}'")
            
            try:
                # Open the first TIFF file to serve as the base for the PDF
                with Image.open(tiff_file_paths[0]) as first_image:
                    original_dpi = first_image.info.get('dpi')
                    
                    if original_dpi and isinstance(original_dpi, tuple):
                        dpi_value = original_dpi[0]
                    elif original_dpi and isinstance(original_dpi, (int, float)):
                        dpi_value = original_dpi
                    else:
                        dpi_value = None

                    # Convert base image to RGB (PDF requirement)
                    base_pdf_img = first_image.convert("RGB")
                    other_images = []
                    
                    # Inner progress bar for files within a directory
                    with tqdm(total=len(tiff_file_paths) - 1, desc="Processing files", unit="file", position=1, leave=False) as pbar_files:
                        for tiff_path in tiff_file_paths[1:]:
                            # EFFICIENCY FIX: Open, convert, load data, and close file handle immediately
                            with Image.open(tiff_path) as img:
                                rgb_img = img.convert("RGB")
                                rgb_img.load()  # Forces loading pixel data into memory so handle can close
                                other_images.append(rgb_img)
                            pbar_files.update(1)

                    # Save complete PDF matrix sequence
                    if dpi_value:
                        base_pdf_img.save(
                            pdf_output_path, 
                            "PDF", 
                            resolution=dpi_value,
                            save_all=True, 
                            append_images=other_images
                        )
                    else:
                        base_pdf_img.save(
                            pdf_output_path, 
                            "PDF", 
                            save_all=True, 
                            append_images=other_images
                        )
                
                # Explicit clean up of allocated images to free system RAM immediately
                for img in other_images:
                    img.close()
                base_pdf_img.close()
                
                pbar_dirs.set_postfix_str("Converted")

            except Exception as e:
                pbar_dirs.set_postfix_str(f"Failed")
                print(f"\nError converting directory '{os.path.basename(directory_path)}' to PDF: {e}")

            pbar_dirs.update(1)
            
    print("\nAll directories processed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
         description="Batch convert subdirectories containing TIFF images into single PDF files."
    )
    parser.add_argument(
        "-s",
        "--source_directory",
        type=str,
        help="The full path to the root directory containing your source TIFF subfolders.",
    )
    parser.add_argument(
        "-d",
        "--destination_directory",
        type=str,
        help="The destination path where your output PDF files should be written.",
    )
    args = parser.parse_args()

    if args.source_directory:
        source_dir = args.source_directory
    else:
        source_dir = input("Please enter the full path to the root directory containing the subfolders: ")
   
    DEFAULT_DIR = r"D:\Georgetown_News_Graphic\Working_Folder"

    if not source_dir.strip():
        print(f"Input was blank. Using default directory: {DEFAULT_DIR}")
        source_dir = DEFAULT_DIR
    
    # Normalize path strings to strip messy trailing slash characters
    source_dir = os.path.normpath(source_dir)

    # CRITICAL FIX: Direct guard clause validation to prevent execution on invalid directories
    if not os.path.isdir(source_dir):
        print(f"Error: The provided path '{source_dir}' is not a valid directory.")
        sys.exit(1)
    
    formatted_source_dir = f"{ANSI_BOLD}{ANSI_BRIGHT_RED}{ANSI_BLINK}{source_dir}{ANSI_RESET}"
    print(f"Using source directory: {formatted_source_dir}")
    
    # Resolve optional destination directory
    dest_dir = os.path.normpath(args.destination_directory) if args.destination_directory else None

    create_pdf_from_tiffs(
        source_directory=source_dir,
        destination_directory=dest_dir
    )