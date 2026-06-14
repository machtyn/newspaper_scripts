# newspaper_scripts

A collection of Python scripts for batch processing newspaper digitization files, primarily focused on TIFF image manipulation, sequential file renaming, and archival PDF generation.

## Project Overview

These scripts are engineered to automate and optimize common tasks in high-volume newspaper archival and digitization workflows (specifically tailored for the Georgetown News Graphic project). The portfolio addresses image enhancement, compression, multi-core resizing, split workflows, and collision-free reindexing.

## Installation & Setup

### Prerequisites

- **Python 3.7+**
- **pip3** (Python package manager)
- **ImageMagick** (Required for command-line image enhancement and layout splitting)

### Step 1: Install Python Dependencies

Clone or download this repository, navigate to the root directory, and install the required Python packages from the ecosystem manifest:

```bash
pip3 install -r requirements.txt

This ensures the availability of:

    Pillow (PIL) >=10.0.0 — Core pixel and metadata adjustments.

    tqdm >=4.65.0 — Visual progress indicators for long-running batches.

Step 2: Install ImageMagick

Scripts utilizing external binary executions require ImageMagick's magick tool.
Windows

    Download the executable installer from imagemagick.org.

    Run the installer and verify that "Add ImageMagick to system PATH" is explicitly checked.

    Verify global accessibility by opening a fresh command prompt and executing:
    DOS

    magick --version

macOS
Bash

brew install imagemagick

Linux (Ubuntu/Debian)
Bash

sudo apt-get install imagemagick

Unified Command Line Parameter Schema

To provide a seamless operational experience across the portfolio, all script entry points have been standardized around a rigid flag naming layout:

    -s, --source_directory : Denotes the input target directory tree containing the raw source files.

    -d, --destination_directory : Denotes the output target path where transformed assets will be safely generated.

If a mandatory path parameter is omitted when executing a script via the command line, the execution layer will smoothly fall back to an interactive user console prompt, or gracefully apply your hardcoded default backup path (D:\Georgetown_News_Graphic\Working_Folder).
Core Tool Belt Reference
1. renumberFiles.py

Performs a strict, collision-free numerical indexing run to re-sequence page sets sequentially from 0001 to X.

    Key Features:

        Double-Pass Logic: Pass 1 maps files into an intermediate 8xxx buffer; Pass 2 cleans and down-steps indices to their final 0xxx production schema. This completely eliminates filename collisions.

        Explicitly requires a strict whitespace separator before the 4-digit token, bypassing malformed strings to maintain project uniformity.

    CLI Syntax & Usage:
    Bash

    python3 src/renumberFiles.py -s /path/to/raw_working_folder

2. resizeTiff.py

Resizes asymmetric newspaper image arrays to fixed core canvas bounds using true CPU-bound parallelism.

    Key Features:

        Leverages ProcessPoolExecutor utilizing os.cpu_count() - 2 threads to maximize processing throughput.

        Preserves aspect ratio using premium LANCZOS filtration before centering onto a white padded background.

        Targets standard dimensions: 3300 x 6600 pixels.

        Safety Shield: Requires explicit user keyword affirmation (yes) if running without a destination flag to prevent accidental in-place asset overwrites.

    CLI Syntax & Usage:
    Bash

    python3 src/resizeTiff.py -s /path/to/source -d /path/to/output_padded

3. magickTiff.py

Executes batch background white normalization, sharpening matrices, and curve level balances on archival text, wrapping results in LZW compression.

    Key Features:

        Omitted -accelerate rendering parameters to prevent crashes on Windows environments.

        Redirects image processor noise streams away from active tqdm timeline updates.

        -t/--test execution flag writes safely to temporary .new.tiff spaces to preview layout calibrations.

    CLI Syntax & Usage:
    Bash

    python3 src/magickTiff.py -s /path/to/source -d /path/to/destination

4. grayscale.py

Converts color TIFF images to 8-bit grayscale layouts while strictly safeguarding underlying image metrics.

    Key Features:

        Preserves original source DPI/PPI image header fields.

        Replicates complex nested directory trees cleanly from a Color root to a parallel Grayscale node.

    CLI Syntax & Usage:
    Bash

    python3 src/grayscale.py -s /path/to/source -d /path/to/destination

5. combineTiff2PDF.py

Consolidates organized collections of independent, sequentially ordered TIFF pages into single document deliverable PDFs.

    Key Features:

        Maps nested issue paths to generate one unified PDF per subdirectory node.

        Dual-layer tqdm monitoring displays active folder-by-folder progress alongside localized image processing stacks.

        Implements explicit image descriptor resource closing commands to completely prevent out-of-memory crashes on large volumes.

    CLI Syntax & Usage:
    Bash

    python3 src/combineTiff2PDF.py -s /path/to/source -d /path/to/destination

6. splitTiff.py

Parses incoming multi-page TIFF layers, splits them into individual pages via ImageMagick, converts raw hyphenated dates to clean numerical structures, and archives originals securely.

    Key Features:

        Strict regex validation matching SCPL yyyy-MM-dd.tiff layouts.

        Auto-formats output strings into standard archival nomenclature: Roll 0001 SCPL yyyyMMdd %04d.tif.

        Isolates multi-page source files into a dedicated MultiTiff subfolder to preserve raw context.

    CLI Syntax & Usage:
    Bash

    python3 src/splitTiff.py -s /path/to/raw/tiffs

7. removeRoll#.py (Optional)

Recursively strips out legacy or operational tape roll headers from final compiled document files before publishing.

    Key Features:

        Target regex filters match Roll #### SCPL yyyyMMdd.pdf structures.

        Safe name-clash checking flags and skips files if a shortened target filename is already occupied on disk.

    CLI Syntax & Usage:
    Bash

    python3 src/removeRoll#.py -s /path/to/final_pdfs

8. renameDate.py

An administrative file-matching maintenance utility used to quickly find and alter specific historical date indexing parameters.

    Key Features:

        Validates prefix boundaries against standard archival schemas (Roll 0001 SCPL).

        Seamlessly swaps target date strings without touching surrounding volume indices or page numbering fields.

    CLI Syntax & Usage:
    Bash

    python3 src/renameDate.py -s /path/to/target_directory --old_date 20260520 --new_date 20260523

Typical Production Workflow

For standard archival batches, run the scripts sequentially in this exact order to manage your transformations and preserve data nodes:
Plaintext

  [1. renumberFiles.py]   ---> Resolves file index sequences securely from 0001 to X first.
         │
         ▼
  [2. resizeTiff.py]      ---> Standardizes files to a uniform 3300x6600 canvas using parallel cores.
         │
         ▼
  [3. magickTiff.py]      ---> Pass 1: Run image enhancements. Save outputs to 'Roll0001-magicked'.
         │
         ├──► [5. grayscale.py] ---> Transforms the 'Roll0001-magicked' files to standard 
         │                           archival grayscale. Save to 'Roll0001-grayscale'.
         ▼
  [4. magickTiff.py]      ---> Pass 2: Run a second pass on the magicked files for secondary 
         │                           tuning/checks. Save outputs to 'Roll0001-compressed'.
         ▼
  [6. combineTiff2PDF.py] ---> Packages the final 'Roll0001-compressed' subfolders into final publication 
                              PDFs. Save results to 'SCPL GEORGETOWN NEWS GRAPHIC MMMYYYY - MMMYYYY'.

Detailed Pipeline Execution Reference

    renumberFiles.py Run this first on your raw working directory to ensure strict double-pass chronological ordering (0001 to X) before any structural changes occur.
    Bash

    python3 src/renumberFiles.py -s /path/to/raw_working_folder

    resizeTiff.py Standardize the newly renumbered files onto your uniform 3300 x 6600 canvas.
    Bash

    python3 src/resizeTiff.py -s /path/to/raw_working_folder -d /path/to/resized_folder

    magickTiff.py (Pass 1 - Enhancements) Execute your first ImageMagick pass for level adjustments and sharpening. Route these explicitly to your primary magicked workspace directory.
    Bash

    python3 src/magickTiff.py -s /path/to/resized_folder -d /path/to/Roll0001-magicked

    magickTiff.py (Pass 2 - Final Tuning/Compression) Run the script a second time using the results of your first pass as the new source inputs. Route this delivery layer to your compressed workspace directory.
    Bash

    python3 src/magickTiff.py -s /path/to/Roll0001-magicked -d /path/to/Roll0001-compressed

    grayscale.py Branch off from your first enhanced pass to generate your preservation grayscale copies, using Roll0001-magicked as the source input.
    Bash

    python3 src/grayscale.py -s /path/to/Roll0001-magicked -d /path/to/Roll0001-grayscale

    combineTiff2PDF.py Compile the final ordered TIFF sets from your second compressed pass into finished documents. Assign the explicit publication-ready naming schema.
    Bash

    python3 src/combineTiff2PDF.py -s /path/to/Roll0001-compressed -d "/path/to/SCPL GEORGETOWN NEWS GRAPHIC MMMYYYY - MMMYYYY"

Note: Depending on your specific client delivery specs, removeRoll#.py may be optional if your final path structures do not require post-compile filename stripping.
Architectural Notes & Best Practices

    Path Normalization: All scripts utilize os.path.normpath internally. You can safely copy and paste Windows backslashes (\) or POSIX forward slashes (/) directly into CLI prompts without encountering pathing errors.

    I/O Bottlenecks & Concurrency: When managing memory-heavy operations or single-threaded consolidation tasks (like combineTiff2PDF.py), run operations at the subfolder level (2 to 4 folders concurrently). Avoid setting multi-core parallel processing values too high on a single folder, as this can cause drive thrashing and drop throughput.

    Data Protection Policy: Always attempt to provide separate -s and -d paths during production operations. Running actions in-place should only be executed once backup images have been secured offsite.