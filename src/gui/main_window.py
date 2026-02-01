
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QSplitter, QFileDialog, QToolBar, QMessageBox,
                             QAbstractItemView)
from PyQt6.QtCore import Qt, QSize, QThreadPool, QSettings, QRunnable, pyqtSignal, QObject
from PyQt6.QtGui import QAction, QIcon, QPixmap, QColor

from src.gui.metadata_panel import MetadataPanel
from src.gui.custom_delegate import ThumbnailDelegate
from src.core.exif_handler import ExifHandler
from src.core.thumbnail_loader import ThumbnailWorker

class DateWorkerSignals(QObject):
    finished = pyqtSignal(dict) # {filepath: date_str}

class DateLoaderWorker(QRunnable):
    def __init__(self, filepaths, exif_handler):
        super().__init__()
        self.filepaths = filepaths
        self.exif_handler = exif_handler
        self.signals = DateWorkerSignals()

    def run(self):
        try:
            results = self.exif_handler.get_batch_date_info(self.filepaths)
            self.signals.finished.emit(results)
        except Exception as e:
            print(f"Date loader error: {e}")
            self.signals.finished.emit({})

class MainWindow(QMainWindow):
    def __init__(self, exiftool_path=None):
        super().__init__()
        self.setWindowTitle("EXIF Editor")
        self.settings = QSettings("MyCompany", "ExifEditor")
        
        # Init Core
        self.exif_handler = ExifHandler(exiftool_path)
        self.thread_pool = QThreadPool()
        print(f"Multithreading with maximum {self.thread_pool.maxThreadCount()} threads")

        self.init_ui()
        self.restore_state()

    def init_ui(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        action_open = QAction("Open Folder", self)
        action_open.triggered.connect(self.open_folder)
        toolbar.addAction(action_open)

        central_widget = QWidget()
        main_layout = QHBoxLayout()
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(180, 180))
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list_widget.setGridSize(QSize(200, 240)) 
        self.list_widget.setSpacing(5)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDragEnabled(False)
        
        # Use Custom Delegate using setItemDelegate
        # We need to hold a reference to it
        self.delegate = ThumbnailDelegate()
        self.list_widget.setItemDelegate(self.delegate)

        self.metadata_panel = MetadataPanel()
        self.metadata_panel.save_clicked.connect(self.update_metadata)

        self.splitter.addWidget(self.list_widget)
        self.splitter.addWidget(self.metadata_panel)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)

        main_layout.addWidget(self.splitter)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def restore_state(self):
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(1000, 700)
            
        splitter_state = self.settings.value("splitterState")
        if splitter_state:
            self.splitter.restoreState(splitter_state)

        self.last_folder = self.settings.value("lastFolder", "")
        if self.last_folder and os.path.exists(self.last_folder):
             self.load_files(self.last_folder)

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("splitterState", self.splitter.saveState())
        self.settings.setValue("lastFolder", self.last_folder)
        super().closeEvent(event)

    def open_folder(self):
        start_dir = self.last_folder if (self.last_folder and os.path.exists(self.last_folder)) else ""
        folder = QFileDialog.getExistingDirectory(self, "Select Directory", start_dir)
        if folder:
            self.last_folder = folder
            self.load_files(folder)

    def load_files(self, folder):
        self.list_widget.clear()
        
        supported_ext = ('.jpg', '.jpeg', '.png', '.mp4', '.mov')
        
        try:
            files_to_load = []
            for f in os.listdir(folder):
                if f.lower().endswith(supported_ext):
                    files_to_load.append(os.path.join(folder, f))
        except Exception as e:
            print(f"Error reading folder {folder}: {e}")
            return
        
        for f in files_to_load:
            basename = os.path.basename(f)
            # Initial text: Filename \n status
            item = QListWidgetItem(f"{basename}\nLoading...")
            item.setData(Qt.ItemDataRole.UserRole, f)
            # Default empty icon
            item.setIcon(QIcon(QPixmap(100, 100))) 
            self.list_widget.addItem(item)
            
            worker = ThumbnailWorker(f)
            worker.signals.finished.connect(self.on_thumbnail_ready)
            self.thread_pool.start(worker)

        if files_to_load:
            date_worker = DateLoaderWorker(files_to_load, self.exif_handler)
            date_worker.signals.finished.connect(self.on_dates_loaded)
            self.thread_pool.start(date_worker)

    def on_thumbnail_ready(self, filepath, pixmap):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            try:
                if item.data(Qt.ItemDataRole.UserRole) == filepath:
                    item.setIcon(QIcon(pixmap))
                    break
            except RuntimeError:
                pass

    def on_dates_loaded(self, results):
        # results = {norm_abs_path_lower: date_str}
        
        # Create a fallback map based on basenames (lowercase) for easier matching
        # key = basename.lower(), value = date_str
        basename_map = {}
        for k, v in results.items():
            # k is full path lower
            basename = os.path.basename(k)
            basename_map[basename] = v
        
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            try:
                filepath = item.data(Qt.ItemDataRole.UserRole)
                # 1. Try Full Path Match
                abs_norm_key = os.path.abspath(filepath).lower()
                date_val = results.get(abs_norm_key)
                
                # 2. Try Basename Match (Fallback)
                if not date_val:
                    name = os.path.basename(filepath).lower()
                    date_val = basename_map.get(name)
                
                basename = os.path.basename(filepath)
                if date_val:
                    # Clean up date display
                    display_date = date_val.replace(":", "-", 2)
                    item.setText(f"{basename}\n{display_date}")
                else:
                    item.setText(f"{basename}\n-")
                    
            except RuntimeError:
                pass

    def on_item_clicked(self, item):
        filepath = item.data(Qt.ItemDataRole.UserRole)
        self.metadata_panel.load_file(filepath, None, self.exif_handler)

    def update_metadata(self, filepath, new_date_str):
        success = self.exif_handler.update_date(filepath, new_date_str)
        if success:
            QMessageBox.information(self, "Success", "Date updated successfully!")
            self.metadata_panel.load_file(filepath, None, self.exif_handler)
            
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == filepath:
                    basename = os.path.basename(filepath)
                    display_date = new_date_str.replace(":", "-", 2)
                    item.setText(f"{basename}\n{display_date}")
                    break
        else:
            QMessageBox.critical(self, "Error", "Failed to update date.")
