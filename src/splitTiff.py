import os
import re
import subprocess
import shutil

def process_tiff_files(start_directory):
    """
    Parses directories, runs a magick convert command on specific TIFF files,
    and then copies the original TIFF to a 'MultiTiff' subdirectory.

    Args:
        start_directory (str): The root directory to start searching from.
    """
    # Regex to match "SCPL yyyy-MM-dd.tiff"
    # Group 1: "SCPL "
    # Group 2: yyyy-MM-dd (the date part)
    # Group 3: ".tiff"
    tiff_pattern = re.compile(r"(SCPL\s)(\d{4}-\d{2}-\d{2})(\.tiff)", re.IGNORECASE)

    for root, dirs, files in os.walk(start_directory):
        # Create MultiTiff subdirectory if it doesn't exist in the current root
        multi_tiff_dir = os.path.join(root, "MultiTiff")
        os.makedirs(multi_tiff_dir, exist_ok=True)

        for filename in files:
            match = tiff_pattern.match(filename)
            if match:
                original_filepath = os.path.join(root, filename)
                date_part = match.group(2) # e.g., "2023-01-01"

                # Convert date from yyyy-MM-dd to yyyyMMdd for the output filename
                output_date_part = date_part.replace('-', '') # e.g., "20230101"

                # Construct the output filename pattern for magick convert
                # Example: "Roll 0001 SCPL 20230101 %04d.tif"
                output_filename_pattern = f"Roll 0001 SCPL {output_date_part} %04d.tif"

                # Construct the magick convert command
                # Note: We are using 'magick' directly as it's the modern ImageMagick command.
                # Ensure ImageMagick is installed and its 'magick' command is in your system's PATH.
                # For Windows, you might need to specify the full path to magick.exe
                # e.g., command = [r"C:\Program Files\ImageMagick-7.1.1-Q16\magick.exe", ...]
                command = [
                    "magick",
                    "convert",
                    "-units", "PixelsPerInch",
                    original_filepath,
                    "-density", "300",
                    os.path.join(root, output_filename_pattern) # Output to current directory
                ]

                print(f"\nProcessing '{original_filepath}'...")
                print(f"Executing command: {' '.join(command)}")

                try:
                    # Run the command
                    result = subprocess.run(command, check=True, capture_output=True, text=True)
                    print("Magick Convert Output:")
                    print(result.stdout)
                    if result.stderr:
                        print("Magick Convert Errors/Warnings:")
                        print(result.stderr)
                    print(f"Successfully ran magick convert for '{filename}'")

                    # Copy the original file to the MultiTiff directory
                    destination_path = os.path.join(multi_tiff_dir, filename)
                    shutil.copy2(original_filepath, destination_path)
                    print(f"Copied '{filename}' to '{multi_tiff_dir}'")

                except subprocess.CalledProcessError as e:
                    print(f"Error running magick convert for '{filename}':")
                    print(f"Command: {e.cmd}")
                    print(f"Return Code: {e.returncode}")
                    print(f"STDOUT: {e.stdout}")
                    print(f"STDERR: {e.stderr}")
                except FileNotFoundError:
                    print(f"Error: 'magick' command not found. Please ensure ImageMagick is installed and in your system's PATH.")
                except Exception as e:
                    print(f"An unexpected error occurred while processing '{filename}': {e}")

if __name__ == "__main__":
    # IMPORTANT: Set the directory where your files are located.
    # Be very careful with the start_directory.
    target_directory = input("Enter the starting directory for TIFF processing (e.g., 'C:\\MyFiles' or '.' for current directory): ")

    if not os.path.isdir(target_directory):
        print(f"Error: The directory '{target_directory}' does not exist.")
    else:
        print(f"Starting TIFF processing in '{target_directory}'...")
        process_tiff_files(target_directory)
        print("\nTIFF processing completed.")