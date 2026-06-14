# newspaper_scripts

A collection of Python scripts for batch processing newspaper digitization files, primarily focused on TIFF image manipulation, file renaming, and PDF generation.

## Project Overview

These scripts are designed to handle common tasks in newspaper archival workflows, including image enhancement, compression, format conversion, and batch file organization.

## Installation & Setup

### Prerequisites

- Python 3.7 or higher
- pip3 (Python package manager)
- ImageMagick (for image processing scripts)

### Step 1: Install Python Dependencies

Clone or download this repository, then install the required Python packages:

```bash
pip3 install -r requirements.txt
```

This will install:
- **Pillow** - Image processing library
- **tqdm** - Progress bar library

### Step 2: Install ImageMagick

Some scripts require ImageMagick's `magick` command-line tool. Install it for your operating system:

#### Windows
1. Download the installer from [imagemagick.org](https://imagemagick.org/script/download.php)
2. Run the installer and ensure "Add ImageMagick to system PATH" is checked
3. Verify installation by opening a terminal and running:
   ```bash
   magick --version
   ```

#### macOS
```bash
brew install imagemagick
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install imagemagick
```

#### Linux (Fedora/RHEL)
```bash
sudo dnf install ImageMagick
```

### Step 3: Verify Installation

Test that all dependencies are properly installed:

```bash
# Check Python version
python3 --version

# Check ImageMagick installation
magick --version
```

## Scripts

All scripts are located in the `src/` directory.

### 1. **combineTiff2PDF.py**
Converts directories containing TIFF images into single PDF files.

**Features:**
- Scans subdirectories recursively for TIFF files
- Creates one PDF per subdirectory
- Preserves original DPI/PPI information
- Dual progress bars (directory and file-level)
- Converts images to RGB format for PDF compatibility

**Usage:**
```bash
python3 src/combineTiff2PDF.py
# Prompts for root directory path
```

**Dependencies:** Pillow (PIL), tqdm

---

### 2. **grayscale.py**
Converts color TIFF images to grayscale while preserving DPI information.

**Features:**
- Recursively processes color TIFF files
- Maintains original DPI/PPI values
- Creates parallel directory structure (Color → Grayscale)
- Progress tracking with tqdm
- Handles errors gracefully

**Usage:**
```bash
python3 src/grayscale.py
# Prompts for Color root directory path
# Creates Grayscale directory at same parent level
```

**Dependencies:** Pillow (PIL), tqdm

---

### 3. **removeRoll#.py**
Removes "Roll ####" prefixes from PDF filenames.

**Features:**
- Regex pattern matching for "Roll #### SCPL yyyyMMdd.pdf" format
- Recursive directory traversal
- Conflict detection (prevents overwriting existing files)
- Detailed logging of all operations
- Command-line argument support

**Usage:**
```bash
python3 src/removeRoll#.py --target_dir C:\path\to\files
# Or without arguments for interactive prompt
```

**Dependencies:** argparse, os, re

---

### 4. **renameDate.py**
Batch renames TIFF files by replacing date strings in filenames.

**Features:**
- Targets files matching "Roll 0001 SCPL*.tif" pattern
- Replaces old date with new date (YYYYMMDD format)
- Command-line argument support
- Interactive fallback for missing arguments
- Prevents accidental file overwrites

**Usage:**
```bash
python3 src/renameDate.py -old_date 20250520 -new_date 20250523 -directory C:\path
# Or with partial/no arguments for interactive prompts
```

**Dependencies:** argparse, os, re

---

### 5. **renumberFiles.py**
Performs double-pass sequential renumbering of files in folders.

**Features:**
- Two-pass renaming system:
  - Pass 1: Renames to temporary 8xxx format (prevents conflicts)
  - Pass 2: Renames to final 0001-to-X format
- Recursive directory traversal
- Reverse-order numbering logic
- Comprehensive logging and progress tracking
- Command-line argument support

**Usage:**
```bash
python3 src/renumberFiles.py -d C:\path\to\files
# Or: python3 src/renumberFiles.py --source_dir C:\path\to\files
# Interactive prompt if directory not provided
```

**Dependencies:** argparse, os, re

---

### 6. **resizeTiff.py**
Resizes TIFF images to target dimensions with padding and aspect ratio preservation.

**Features:**
- Parallel batch processing (uses CPU count - 2 cores)
- Target dimensions: 3300 x 6600 pixels (customizable)
- Maintains aspect ratio
- Adds white background padding as needed
- Preserves original DPI information
- Progress tracking with tqdm

**Usage:**
```bash
python3 src/resizeTiff.py -d C:\path\to\tiff\files
# Or: python3 src/resizeTiff.py --directory C:\path\to\tiff\files
# Interactive prompt if directory not provided
```

**Dependencies:** Pillow (PIL), argparse, concurrent.futures, tqdm

---

### 7. **splitTiff.py**
Splits multi-page TIFF files into individual pages using ImageMagick.

**Features:**
- Parses files matching "SCPL yyyy-MM-dd.tiff" pattern
- Converts multi-page TIFFs to individual pages
- Renames output pages as "Roll 0001 SCPL yyyyMMdd %04d.tif"
- Sets DPI to 300 (configurable via command)
- Creates "MultiTiff" subdirectory for archived originals
- Detailed command and error logging

**Usage:**
```bash
python3 src/splitTiff.py
# Prompts for starting directory path
```

**Dependencies:** ImageMagick (magick command), os, re, subprocess, shutil

---

### 8. **magickTiff.py**
Applies sophisticated image enhancements and LZW compression to TIFF files.

**Features:**
- Creates new `.new.tiff` files (non-destructive)
- Preserves original files
- Applies continuous level mapping for smooth background-to-white clipping
- White margin cleanup for absolute brightness values
- Text sharpening using unsharp masking
- LZW compression for efficient file storage
- Progress tracking with tqdm
- User confirmation before processing

**Usage:**
```bash
python3 src/magickTiff.py
# Prompts for directory (or press Enter for default)
```

**Dependencies:** ImageMagick (magick command), tqdm, subprocess, shutil

---

## Common Dependencies

- **Pillow (PIL)**: Image processing (grayscale.py, combineTiff2PDF.py, resizeTiff.py)
- **tqdm**: Progress bars (all scripts)
- **ImageMagick**: Command-line image manipulation (splitTiff.py, magickTiff.py)
  - Ensure `magick` command is in system PATH
  - Windows: Download from [ImageMagick.org](https://imagemagick.org)

## Typical Workflow

1. **Input**: Original color TIFF files
2. **grayscale.py**: Convert to grayscale
3. **magickTiff.py**: Enhance and compress
4. **splitTiff.py**: Split multi-page TIFFs if needed
5. **renumberFiles.py**: Ensure sequential numbering
6. **combineTiff2PDF.py**: Generate PDFs from TIFF collections

## Notes

- Most scripts support recursive directory traversal
- Many provide interactive prompts as fallback to command-line arguments
- File overwrite protection is implemented where appropriate
- Progress bars are shown for long-running operations
- ImageMagick-dependent scripts require the `magick` command in PATH
- All scripts are located in the `src/` directory

## Author Notes

These scripts are optimized for the Georgetown News Graphic project workflow and handle newspaper digitization files. Adjust default directories and parameters as needed for your use case.
