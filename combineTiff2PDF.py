import os
from PIL import Image
from tqdm import tqdm

def create_pdf_from_tiffs(root_directory):
    """
    Finds all subdirectories containing TIFF files and creates a single PDF
    from those TIFFs, saving it to the parent directory of the subfolder.

    Args:
        root_directory (str): The top-level directory to start scanning.
    """
    if not os.path.isdir(root_directory):
        print(f"Error: The provided path '{root_directory}' is not a valid directory.")
        return

    print(f"Scanning for TIFF files in subdirectories of '{root_directory}'...")
    
    directories_to_process = []
    
    for root, dirs, files in os.walk(root_directory):
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
            parent_dir = os.path.dirname(directory_path)
            pdf_output_path = os.path.join(parent_dir, pdf_filename)
            
            pbar_dirs.set_description(f"Processing '{os.path.basename(directory_path)}'")
            
            try:
                # Open the first TIFF file to serve as the base for the PDF
                first_image = Image.open(tiff_file_paths[0])
                
                original_dpi = first_image.info.get('dpi')
                
                if original_dpi and isinstance(original_dpi, tuple):
                    dpi_value = original_dpi[0]
                elif original_dpi and isinstance(original_dpi, (int, float)):
                    dpi_value = original_dpi
                else:
                    dpi_value = None

                other_images = []
                
                # Inner progress bar for files within a directory
                with tqdm(total=len(tiff_file_paths) - 1, desc="Processing files", unit="file", position=1, leave=False) as pbar_files:
                    for tiff_path in tiff_file_paths[1:]:
                        img = Image.open(tiff_path)
                        other_images.append(img.convert("RGB"))
                        pbar_files.update(1)

                if dpi_value:
                    first_image.save(
                        pdf_output_path, 
                        "PDF", 
                        resolution=dpi_value,
                        save_all=True, 
                        append_images=other_images
                    )
                else:
                    first_image.save(
                        pdf_output_path, 
                        "PDF", 
                        save_all=True, 
                        append_images=other_images
                    )
                
                pbar_dirs.set_postfix_str("Converted")

            except Exception as e:
                pbar_dirs.set_postfix_str(f"Error: {e}")
                print(f"\nError converting directory '{os.path.basename(directory_path)}' to PDF: {e}")

            pbar_dirs.update(1)
            
    print("\nAll directories processed.")

if __name__ == "__main__":
    target_dir = input("Please enter the full path to the root directory containing the subfolders: ")
    create_pdf_from_tiffs(target_dir)