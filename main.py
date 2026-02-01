
import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
import shutil

# Add src to python path to handle imports correctly if run from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.gui.main_window import MainWindow

def get_exiftool_path():
    # 1. Check if exiftool is in the system PATH
    img_ext = shutil.which("exiftool")
    if img_ext:
        return img_ext
    
    # 2. Check local 'libs' or 'core' or current dir
    #    (Common pattern: rename 'exiftool(-k).exe' to 'exiftool.exe')
    potential_paths = [
        "exiftool.exe",
        "src/core/exiftool.exe",
        "src/libs/exiftool.exe",
        "libs/exiftool.exe"
    ]
    
    for p in potential_paths:
        if os.path.exists(p):
            return os.path.abspath(p)
            
    return None

def main():
    app = QApplication(sys.argv)
    
    # "Rich Aesthetics" - Dark Theme Stylesheet
    # Inspired by modern VS Code / Dracula themes
    app.setStyle("Fusion")
    
    dark_stylesheet = """
    QMainWindow {
        background-color: #1e1e2e;
    }
    QWidget {
        color: #dce0e8;
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
    }
    QListWidget {
        background-color: #181825;
        border: 1px solid #313244;
        border-radius: 8px;
        padding: 10px;
    }
    QListWidget::item {
        background-color: #1e1e2e;
        border-radius: 6px;
        padding: 5px;
        margin: 5px;
    }
    QListWidget::item:selected {
        background-color: #45475a;
        border: 1px solid #89b4fa;
    }
    QGroupBox {
        border: 1px solid #313244;
        border-radius: 8px;
        margin-top: 10px;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px;
    }
    QLineEdit, QDateTimeEdit {
        background-color: #313244;
        border: 1px solid #45475a;
        border-radius: 4px;
        padding: 5px;
        color: #cdd6f4;
    }
    QPushButton {
        background-color: #89b4fa;
        color: #1e1e2e;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #b4befe;
    }
    QPushButton:disabled {
        background-color: #45475a;
        color: #7f849c;
    }
    QLabel {
        color: #bac2de;
    }
    QToolBar {
        background-color: #11111b;
        border-bottom: 1px solid #313244;
    }
    """
    app.setStyleSheet(dark_stylesheet)

    exif_path = get_exiftool_path()
    
    if not exif_path:
        # Warning but let them open it (some features might fail or they need to set it up)
        # Actually PyExifTool usually requires it to run.
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("ExifTool Not Found")
        msg.setText("Could not find 'exiftool.exe'.\n\nPlease download it from exiftool.org, rename it to 'exiftool.exe', and place it in the application folder or add it to PATH.\n\nMetadata features will not work without it.")
        msg.exec()

    window = MainWindow(exiftool_path=exif_path)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
