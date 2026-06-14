import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import sys
from PIL import Image
from tqdm import tqdm

# ==============================================================================
# GLOBAL CONFIGURATION & ENVIRONMENT SCOPING
# ==============================================================================
DEFAULT_DIR = r"D:\Georgetown_News_Graphic\Working_Folder"
TARGET_WIDTH = 3300
TARGET_HEIGHT = 6600

# ANSI Escape Codes for high-visibility terminal text formatting
ANSI_BOLD = "\033[1m"
ANSI_BLINK = "\033[5m"
ANSI_BRIGHT_RED = "\033[91m"
ANSI_RESET = "\033[0m"


def process_tiff_image(
    image_path,
    output_path,
    target_width=3300,
    target_height=6600,
    background_color=(255, 255, 255),
):
    """
    Resizes a TIFF image to fit within target_width and target_height,
    maintaining aspect ratio, and adds a white background if needed.
    Preserves the original DPI/PPI.

    Returns:
        str: Status message detailing the outcome.
    """
    if not os.path.exists(image_path):
        return "Error: Source path does not exist"

    try:
        with Image.open(image_path) as img:
            if img.format != "TIFF":
                return "Skipped: Not a TIFF"

            original_width, original_height = img.size
            original_dpi = img.info.get("dpi")

            width_ratio = target_width / original_width
            height_ratio = target_height / original_height
            scale_ratio = min(width_ratio, height_ratio)

            new_width = int(original_width * scale_ratio)
            new_height = int(original_height * scale_ratio)

            # Check if modification or padding adjustments are required
            if (
                new_width < original_width
                or new_height < original_height
                or original_width < target_width
                or original_height < target_height
            ):
                resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                output_image = Image.new(
                    "RGB", (target_width, target_height), background_color
                )

                paste_x = (target_width - new_width) // 2
                paste_y = (target_height - new_height) // 2
                output_image.paste(resized_img, (paste_x, paste_y))

                # Ensure output directory structures exist for target drops
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                if original_dpi:
                    output_image.save(output_path, dpi=original_dpi)
                else:
                    output_image.save(output_path)

                # Clean up resources explicitly inside the worker thread
                output_image.close()
                resized_img.close()
                return "Processed"
            else:
                # If already perfectly sized, duplicate to destination to preserve tree
                if image_path != output_path:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(image_path, 'rb') as src, open(output_path, 'wb') as dst:
                        dst.write(src.read())
                return "Skipped: Already target size"

    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parallel batch resize and pad TIFF images to target dimensions uniformly."
    )
    parser.add_argument(
        "-s",
        "--source_directory",
        type=str,
        help="The full path to the root directory containing your source TIFF images.",
    )
    parser.add_argument(
        "-d",
        "--destination_directory",
        type=str,
        help="The destination path where your padded TIFF files should be written.",
    )
    args = parser.parse_args()

    # Route source input directory paths
    if args.source_directory:
        source_dir = args.source_directory
    else:
        source_dir = input("Please enter the full path to the directory containing your TIFF images: ")

    if not source_dir.strip():
        print(f"Input was blank. Using default directory: {DEFAULT_DIR}")
        source_dir = DEFAULT_DIR

    # Normalize path string formats across OS parameters
    source_dir = os.path.normpath(source_dir)

    # GUARD CLAUSE: Break script lifecycle execution early if pathing fails
    if not os.path.isdir(source_dir):
        print(f"Error: The provided path '{source_dir}' is not a valid directory.")
        sys.exit(1)

    # Display high-visibility confirmation block
    formatted_source_dir = f"{ANSI_BOLD}{ANSI_BRIGHT_RED}{ANSI_BLINK}{source_dir}{ANSI_RESET}"
    print(f"Using source directory: {formatted_source_dir}")

    # Resolve optional output path structure
    if args.destination_directory:
        dest_dir = os.path.normpath(args.destination_directory)
        print(f"Resized images will be mirrored to: '{dest_dir}'")
    else:
        dest_dir = source_dir
        print(f"{ANSI_BOLD}{ANSI_BRIGHT_RED}?? WARNING: No destination directory provided. Process will modify assets IN-PLACE!{ANSI_RESET}")
        confirmation = input("Are you sure you want to proceed? (yes/no): ").lower().strip()
        if confirmation != 'yes':
            print("Operation cancelled by user.")
            sys.exit(0)

    tiff_files = []
    for root, dirs, files in os.walk(source_dir):
        for filename in files:
            if filename.lower().endswith(('.tif', '.tiff')):
                tiff_files.append(os.path.join(root, filename))

    if not tiff_files:
        print("No TIFF images found matching requirements.")
        sys.exit(0)

    # Detect physical core limits and allocate workers conservatively
    cpu_cores = os.cpu_count() or 1
    max_workers = max(1, cpu_cores - 2)
    print(f"Found {len(tiff_files)} TIFF images. Launching execution matrix across {max_workers} CPU cores...")

    # Execute asynchronous batch mapping safely inside parallel pool execution trees
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Construct task tracking maps
        future_to_file = {}
        for file_path in tiff_files:
            if dest_dir != source_dir:
                relative_path = os.path.relpath(file_path, source_dir)
                out_path = os.path.join(dest_dir, relative_path)
            else:
                out_path = file_path

            task = executor.submit(
                process_tiff_image,
                file_path,
                out_path,
                TARGET_WIDTH,
                TARGET_HEIGHT,
            )
            future_to_file[task] = file_path

        # Monitor dynamic status completions asynchronously
        with tqdm(total=len(tiff_files), desc="Parallel Processing TIFFs", unit="file") as pbar:
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                filename = os.path.basename(file_path)
                try:
                    result_status = future.result()
                    pbar.set_postfix_str(f"{filename[:15]}: {result_status}")
                    
                    # Surfacing background internal errors to terminal stream dynamically
                    if "Error" in result_status:
                        print(f"\nProcessing Failure on asset file '{filename}': {result_status}")
                        
                except Exception as exc:
                    pbar.set_postfix_str(f"{filename[:15]}: Failed")
                    print(f"\nSystemic process worker exception on asset file '{filename}': {exc}")

                pbar.update(1)

    print("All TIFF images successfully processed.")