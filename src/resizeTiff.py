import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
from PIL import Image
from tqdm import tqdm


def process_tiff_image(
    image_path,
    target_width=3300,
    target_height=6600,
    background_color=(255, 255, 255),
):
    """Resizes a TIFF image to fit within target_width and target_height,

    maintaining aspect ratio, and adds a white background if needed.
    Preserves the original DPI/PPI.
    """
    if not os.path.exists(image_path):
        return "Error: Path does not exist"

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

                if original_dpi:
                    output_image.save(image_path, dpi=original_dpi)
                else:
                    output_image.save(image_path)

                return "Processed"
            else:
                return "Skipped: Already target size"

    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parallel batch resize and pad TIFF images to target dimensions."
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        help="The full path to the directory containing TIFF images.",
    )
    args = parser.parse_args()

    if args.directory:
        target_directory = args.directory
    else:
        target_directory = input(
            "Please enter the full path to the directory containing your TIFF images: "
        )

    TARGET_WIDTH = 3300
    TARGET_HEIGHT = 6600

    if os.path.isdir(target_directory):
        print(
            f"Scanning for TIFF images in directory: '{target_directory}'..."
        )

        tiff_files = []
        for root, dirs, files in os.walk(target_directory):
            for filename in files:
                if filename.lower().endswith(('.tif', '.tiff')):
                    tiff_files.append(os.path.join(root, filename))

        if not tiff_files:
            print("No TIFF images found.")
        else:
            # Detect CPU cores and leave 2 free for system stability
            cpu_cores = os.cpu_count() or 1
            max_workers = max(1, cpu_cores - 2)
            print(
                f"Found {len(tiff_files)} TIFF images. Processing using {max_workers} CPU cores..."
            )

            # Use ProcessPoolExecutor for true CPU parallelism
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks to the pool and map them to their futures
                future_to_file = {
                    executor.submit(
                        process_tiff_image,
                        file_path,
                        TARGET_WIDTH,
                        TARGET_HEIGHT,
                    ): file_path
                    for file_path in tiff_files
                }

                # Monitor progress as tasks complete
                with tqdm(
                    total=len(tiff_files),
                    desc="Parallel Processing TIFFs",
                    unit="file",
                ) as pbar:
                    for future in as_completed(future_to_file):
                        file_path = future_to_file[future]
                        filename = os.path.basename(file_path)
                        try:
                            result_status = future.result()
                            pbar.set_postfix_str(
                                f"{filename[:15]}: {result_status}"
                            )
                        except Exception as exc:
                            pbar.set_postfix_str(f"{filename[:15]}: Failed")

                        pbar.update(1)

            print("All TIFF images processed.")
    else:
        print("The provided path is not a valid directory.")