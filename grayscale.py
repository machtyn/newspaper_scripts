from PIL import Image
import os
from tqdm import tqdm

def convert_to_grayscale(input_image_path, output_image_path):
    """
    Converts a TIFF image to grayscale and saves it to a specified path,
    preserving the original DPI/PPI.

    Args:
        input_image_path (str): The path to the input TIFF image.
        output_image_path (str): The path where the grayscale TIFF will be saved.
    Returns:
        bool: True if conversion was successful, False otherwise.
    """
    try:
        with Image.open(input_image_path) as img:
            if img.format != 'TIFF':
                # print(f"Skipping '{os.path.basename(input_image_path)}': Not a TIFF image.")
                return False

            original_dpi = img.info.get('dpi') # Get original DPI if it exists

            # Convert to grayscale
            # 'L' mode is for 8-bit pixels, black and white
            grayscale_img = img.convert('L') 
            
            # Ensure the output directory exists
            os.makedirs(os.path.dirname(output_image_path), exist_ok=True)

            # Save the grayscale image, preserving DPI
            if original_dpi:
                grayscale_img.save(output_image_path, dpi=original_dpi)
            else:
                grayscale_img.save(output_image_path)
            
            return True

    except Exception as e:
        # print(f"Error converting '{os.path.basename(input_image_path)}': {e}")
        return False

if __name__ == "__main__":
    color_root_dir = input("Please enter the full path to the 'Color' root folder (e.g., C:\\Images\\Color): ")

    if not os.path.isdir(color_root_dir):
        print(f"Error: The provided path '{color_root_dir}' is not a valid directory.")
    else:
        # Construct the grayscale root directory path
        # Assuming the 'Grayscale' folder is a sibling of 'Color'
        parent_dir = os.path.dirname(color_root_dir)
        grayscale_root_dir = os.path.join(parent_dir, "Grayscale")
        
        # Create the base Grayscale directory if it doesn't exist
        os.makedirs(grayscale_root_dir, exist_ok=True)
        print(f"Grayscale images will be saved to: '{grayscale_root_dir}'")

        print(f"Scanning for TIFF images in '{color_root_dir}' and its subdirectories...")

        tiff_files_to_process = []
        for root, _, files in os.walk(color_root_dir):
            for filename in files:
                if filename.lower().endswith(('.tif', '.tiff')):
                    input_file_path = os.path.join(root, filename)
                    # Determine the relative path from the color_root_dir
                    relative_path = os.path.relpath(input_file_path, color_root_dir)
                    # Construct the output path in the grayscale_root_dir
                    output_file_path = os.path.join(grayscale_root_dir, relative_path)
                    tiff_files_to_process.append((input_file_path, output_file_path))

        if not tiff_files_to_process:
            print("No TIFF images found in the specified 'Color' directory or its subdirectories.")
        else:
            print(f"Found {len(tiff_files_to_process)} TIFF images to convert.")
            
            with tqdm(total=len(tiff_files_to_process), desc="Converting to Grayscale", unit="file") as pbar:
                for input_path, output_path in tiff_files_to_process:
                    pbar.set_description(f"Converting ({os.path.basename(input_path)})")
                    
                    converted = convert_to_grayscale(input_path, output_path)
                    
                    if converted:
                        pbar.set_postfix_str("Converted")
                    else:
                        pbar.set_postfix_str("Skipped/Error")
                    pbar.update(1)
            print("All TIFF images processed for grayscale conversion.")