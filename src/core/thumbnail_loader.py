
import os
import cv2
from PyQt6.QtCore import QRunnable, pyqtSignal, QObject, Qt
from PyQt6.QtGui import QImage, QPixmap
from PIL import Image, ImageOps

class WorkerSignals(QObject):
    finished = pyqtSignal(str, QPixmap) # filepath, pixmap
    error = pyqtSignal(str, str)

class ThumbnailWorker(QRunnable):
    def __init__(self, filepath, size=(200, 200)):
        super().__init__()
        self.filepath = filepath
        self.size = size
        self.signals = WorkerSignals()

    def run(self):
        try:
            pixmap = self.generate_thumbnail(self.filepath)
            if pixmap:
                try:
                    self.signals.finished.emit(self.filepath, pixmap)
                except RuntimeError:
                    # Handle case where receiver is gone if app closed
                    pass
            else:
                self.signals.error.emit(self.filepath, "Could not generate thumbnail")
        except Exception as e:
            self.signals.error.emit(self.filepath, str(e))

    def generate_thumbnail(self, path):
        if path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            return self.get_video_thumbnail(path)
        else:
            return self.get_image_thumbnail(path)

    def get_image_thumbnail(self, path):
        try:
            img = Image.open(path)
            img = ImageOps.exif_transpose(img) # Handle rotation
            img.thumbnail(self.size, Image.Resampling.LANCZOS)
            
            # Correct Color Conversion: Format_RGBA8888 expects R,G,B,A order in memory.
            # PIL convert("RGBA") ensures R,G,B,A order.
            img = img.convert("RGBA")
            data = img.tobytes("raw", "RGBA")
            
            qim = QImage(data, img.width, img.height, QImage.Format.Format_RGBA8888)
            return QPixmap.fromImage(qim)

        except Exception as e:
            print(f"Error loading image thumbnail {path}: {e}")
            return None

    def get_video_thumbnail(self, path):
        try:
            cap = cv2.VideoCapture(path)
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return None
                
            # OpenCV is BGR. Convert to RGB.
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            # Scale it down
            pixmap = QPixmap.fromImage(qimg)
            # Fix: Use correct positional/keyword arguments for Qt6
            # scaled(w, h, aspectRatioMode)
            return pixmap.scaled(self.size[0], self.size[1], Qt.AspectRatioMode.KeepAspectRatio)
            
        except Exception as e:
            print(f"Error loading video thumbnail {path}: {e}")
            return None
