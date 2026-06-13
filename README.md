# newspaper_scripts

A collection of Python scripts for batch processing newspaper digitization files, primarily focused on TIFF image manipulation, file renaming, and PDF generation.

## Project Overview

These scripts are designed to handle common tasks in newspaper archival workflows, including image enhancement, compression, format conversion, and batch file organization.

## Scripts

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
python combineTiff2PDF.py
# Prompts for root directory path
```

**Dependencies:** Pillow (PIL), tqdm

---

### 2. **compressTiffLZW.py**
Applies image enhancements and LZW compression to TIFF files using ImageMagick.

**Features:**
- Multi-core parallel processing
- Automatic image enhancements:
  - Devignetting (removes vignette effect)
  - Brightness and saturation adjustment (85,115,100)
  - Sigmoidal contrast enhancement (30%)
  - Sharpening
  - Level adjustment for GIMP-compatible output
- LZW compression
- In-place file modification (overwrites originals)
- Configurable core usage (3 or 6 cores)

**Usage:**
```bash
python compressTiffLZW.py
# Prompts for core count and directory path
```

**Dependencies:** ImageMagick (magick command), tqdm, concurrent.futures

**Warning:** This script modifies original files. Requires user confirmation.

---

### 3. **grayscale.py**
Converts color TIFF images to grayscale while preserving DPI information.

**Features:**
- Recursively processes color TIFF files
- Maintains original DPI/PPI values
- Creates parallel directory structure (Color → Grayscale)
- Progress tracking with tqdm
- Handles errors gracefully

**Usage:**
```bash
python grayscale.py
# Prompts for Color root directory path
# Creates Grayscale directory at same parent level
```

**Dependencies:** Pillow (PIL), tqdm

---

### 4. **removeRoll#.py**
Removes "Roll ####" prefixes from PDF filenames.

**Features:**
- Regex pattern matching for "Roll #### SCPL yyyyMMdd.pdf" format
- Recursive directory traversal
- Conflict detection (prevents overwriting existing files)
- Detailed logging of all operations
- Command-line argument support

**Usage:**
```bash
python removeRoll#.py --target_dir C:\path\to\files
# Or without arguments for interactive prompt
```

**Dependencies:** argparse, os, re

---

### 5. **renameDate.py**
Batch renames TIFF files by replacing date strings in filenames.

**Features:**
- Targets files matching "Roll 0001 SCPL*.tif" pattern
- Replaces old date with new date (YYYYMMDD format)
- Command-line argument support
- Interactive fallback for missing arguments
- Prevents accidental file overwrites

**Usage:**
```bash
python renameDate.py -old_date 20250520 -new_date 20250523 -directory C:\path
# Or with partial/no arguments for interactive prompts
```

**Dependencies:** argparse, os, re

---

### 6. **renumberFiles.py**
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
python renumberFiles.py -d C:\path\to\files
# Or: python renumberFiles.py --source_dir C:\path\to\files
# Interactive prompt if directory not provided
```

**Dependencies:** argparse, os, re

---

### 7. **resizeTiff.py**
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
python resizeTiff.py -d C:\path\to\tiff\files
# Or: python resizeTiff.py --directory C:\path\to\tiff\files
# Interactive prompt if directory not provided
```

**Dependencies:** Pillow (PIL), argparse, concurrent.futures, tqdm

---

### 8. **splitTiff.py**
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
python splitTiff.py
# Prompts for starting directory path
```

**Dependencies:** ImageMagick (magick command), os, re, subprocess, shutil

---

### 9. **test_magick.py**
Test script that applies image enhancements and LZW compression to TIFF files.

**Features:**
- Similar enhancements to compressTiffLZW.py
- Creates new `.new.tiff` files (non-destructive)
- Preserves original files
- Progress tracking with tqdm
- User confirmation before processing

**Usage:**
```bash
python test_magick.py
# Prompts for directory (or press Enter for default)
```

**Dependencies:** ImageMagick (magick command), tqdm, subprocess, shutil

---

## Common Dependencies

- **Pillow (PIL)**: Image processing (grayscale.py, combineTiff2PDF.py, resizeTiff.py)
- **tqdm**: Progress bars (all scripts)
- **ImageMagick**: Command-line image manipulation (compressTiffLZW.py, splitTiff.py, test_magick.py)
  - Ensure `magick` command is in system PATH
  - Windows: Download from [ImageMagick.org](https://imagemagick.org)

## Installation

### Python Packages
```bash
pip install Pillow tqdm
```

### ImageMagick
- **Windows**: Download installer from [imagemagick.org](https://imagemagick.org/script/download.php)
- **macOS**: `brew install imagemagick`
- **Linux**: `apt-get install imagemagick` (Ubuntu/Debian)

## Typical Workflow

1. **Input**: Original color TIFF files
2. **grayscale.py**: Convert to grayscale
3. **compressTiffLZW.py** or **test_magick.py**: Enhance and compress
4. **splitTiff.py**: Split multi-page TIFFs if needed
5. **renumberFiles.py**: Ensure sequential numbering
6. **combineTiff2PDF.py**: Generate PDFs from TIFF collections

## Notes

- Most scripts support recursive directory traversal
- Many provide interactive prompts as fallback to command-line arguments
- File overwrite protection is implemented where appropriate
- Progress bars are shown for long-running operations
- ImageMagick-dependent scripts require the `magick` command in PATH

## Author Notes

These scripts are optimized for the Georgetown News Graphic project workflow and handle newspaper digitization files. Adjust default directories and parameters as needed for your use case.
