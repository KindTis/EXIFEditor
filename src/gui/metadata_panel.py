
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QDateTimeEdit, 
                             QPushButton, QFormLayout, QGroupBox, QMessageBox, QScrollArea)
from PyQt6.QtCore import Qt, QDateTime, pyqtSignal

class MetadataPanel(QWidget):
    save_clicked = pyqtSignal(str, str) 

    def __init__(self):
        super().__init__()
        self.current_file = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Scroll Area for Info
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.info_layout = QFormLayout()
        self.scroll_content.setLayout(self.info_layout)
        self.scroll.setWidget(self.scroll_content)
        
        self.info_group = QGroupBox("Detailed Info")
        group_layout = QVBoxLayout()
        group_layout.addWidget(self.scroll)
        self.info_group.setLayout(group_layout)
        
        # Date Edit Group
        self.date_group = QGroupBox("Date & Time")
        date_layout = QVBoxLayout()
        
        self.lbl_date_source = QLabel("Source: -")
        self.lbl_date_source.setStyleSheet("color: #89b4fa; font-style: italic;")
        
        self.date_edit = QDateTimeEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setEnabled(False)
        
        self.btn_save = QPushButton("Apply Change")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.on_save)
        
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6; 
                color: white; 
                font-weight: bold; 
                padding: 8px; 
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:disabled {
                background-color: #475569;
                color: #94a3b8;
            }
        """)

        date_layout.addWidget(self.lbl_date_source)
        date_layout.addWidget(self.date_edit)
        date_layout.addSpacing(10)
        date_layout.addWidget(self.btn_save)
        self.date_group.setLayout(date_layout)

        layout.addWidget(self.info_group)
        layout.addWidget(self.date_group)
        layout.setStretch(0, 1) # Info takes available space
        
        self.setLayout(layout)

    def load_file(self, filepath, metadata_dummy, exif_handler):
        self.current_file = filepath
        
        # Clear previous info
        while self.info_layout.count():
            item = self.info_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Basic Info
        self.info_layout.addRow("Filename:", QLabel(os.path.basename(filepath)))
        
        # Get Full Metadata
        full_meta = exif_handler.get_metadata(filepath)
        if full_meta:
            # Selected relevant tags to display
            # We filter for nice common names
            interesting_keys = [
                ('Make', 'Camera Make'),
                ('Model', 'Camera Model'),
                ('LensID', 'Lens'),
                ('LensModel', 'Lens Model'),
                ('ISO', 'ISO'),
                ('FNumber', 'Aperture'),
                ('ExposureTime', 'Shutter Speed'),
                ('FocalLength', 'Focal Length'),
                ('ImageWidth', 'Width'),
                ('ImageHeight', 'Height'),
                ('GPSPosition', 'GPS'),
                ('MIMEType', 'Type')
            ]
            
            # Simple fuzzy match attempt or direct lookup
            # ExifTool keys might be 'EXIF:Model' or just 'Model' depending on options.
            # We iterate to find matching suffix.
            
            for key, label in interesting_keys:
                # Find key ending with this name
                found_val = None
                for meta_key, meta_val in full_meta.items():
                    if meta_key == key or meta_key.endswith(f":{key}"):
                        found_val = meta_val
                        break
                
                if found_val:
                    self.info_layout.addRow(f"{label}:", QLabel(str(found_val)))
        
        # Date Info
        date_str, source_tag = exif_handler.get_date_info(filepath)
        
        if date_str:
            self.lbl_date_source.setText(f"Source: {source_tag}")
            try:
                parts = str(date_str).split(" ") # Ensure string
                if len(parts) >= 2:
                    ymd = parts[0].split(":")
                    hms = parts[1].split(":")
                    dt = QDateTime(int(ymd[0]), int(ymd[1]), int(ymd[2]), 
                                   int(hms[0]), int(hms[1]), int(hms[2]))
                    self.date_edit.setDateTime(dt)
                else:
                    self.date_edit.setDateTime(QDateTime.currentDateTime())    
            except Exception as e:
                 # fallback
                 print(f"Date parse error: {e}")
                 self.date_edit.setDateTime(QDateTime.currentDateTime())
        else:
            self.lbl_date_source.setText("Source: Not Found")
            self.date_edit.setDateTime(QDateTime.currentDateTime())

        self.date_edit.setEnabled(True)
        self.btn_save.setEnabled(True)

    def on_save(self):
        if self.current_file:
            dt = self.date_edit.dateTime()
            new_date_str = dt.toString("yyyy:MM:dd HH:mm:ss")
            self.save_clicked.emit(self.current_file, new_date_str)
