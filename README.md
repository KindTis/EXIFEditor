# EXIF Editor

A modern, high-performance desktop application for viewing and editing EXIF metadata in images and videos. Built with Python and PyQt6.

## 🌟 Key Features

- **Multi-format Support**: Works with Images (`.jpg`, `.jpeg`, `.png`) and Videos (`.mp4`, `.mov`).
- **Rich User Interface**: Modern dark-themed GUI with a responsive layout.
- **Fast Thumbnails**: Asynchronous thumbnail loading for a smooth browsing experience.
- **Metadata Viewer**: Detailed display of camera information (Make, Model, ISO, Aperture, etc.).
- **Batch Date Editing**: Update 'Date Taken' across various metadata tags (EXIF, QuickTime, XMP, etc.) simultaneously.
- **State Persistence**: Remembers window size, splitter positions, and the last opened folder.

## 🛠️ Tech Stack

- **GUI**: [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- **Metadata Engine**: [ExifTool](https://exiftool.org/) (via [PyExifTool](https://github.com/smarnach/pyexiftool))
- **Image Processing**: [Pillow](https://python-pillow.org/)
- **Video Processing**: [OpenCV](https://opencv.org/)

## 📋 Prerequisites

This application requires **ExifTool** to be installed on your system.

1.  Download `exiftool` from [exiftool.org](https://exiftool.org/).
2.  Rename the executable (e.g., `exiftool(-k).exe`) to `exiftool.exe`.
3.  Place `exiftool.exe` in the project root directory OR add its location to your system's `PATH`.

## ⚙️ Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd EXIFEditor
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv .venv
    # On Windows:
    .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Usage

Run the application using Python:

```bash
python main.py
```

- **Open Folder**: Click the "Open Folder" button in the toolbar to load your media.
- **View Metadata**: Click on any item in the grid to see its detailed metadata in the right panel.
- **Edit Date**: Use the date picker in the metadata panel to modify the creation date and click "Apply Change".

## 📂 Project Structure

- `main.py`: Entry point of the application.
- `src/core/`: Contains core logic for metadata handling and background workers.
    - `exif_handler.py`: Interface for ExifTool operations.
    - `thumbnail_loader.py`: Asynchronous thumbnail generation.
- `src/gui/`: UI components and layouts.
    - `main_window.py`: Primary application window.
    - `metadata_panel.py`: Side panel for viewing and editing tags.
    - `custom_delegate.py`: Custom grid item rendering.
- `exiftool.exe`: (Optional) Local ExifTool executable.
