
from PyQt6.QtWidgets import QStyledItemDelegate, QStyle
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QPen, QColor, QBrush, QFontMetrics

class ThumbnailDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.padding = 4 # Reduced padding

    def paint(self, painter, option, index):
        painter.save()
        
        # 1. Draw Selection Background
        if option.state & QStyle.StateFlag.State_Selected:
            painter.setBrush(QBrush(QColor("#45475a"))) 
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(option.rect, 6, 6)
        
        # 2. Get Data
        icon = index.data(Qt.ItemDataRole.DecorationRole)
        text = index.data(Qt.ItemDataRole.DisplayRole)
        
        rect = option.rect
        icon_size = 180
        
        # 3. Draw Icon
        if icon and not icon.isNull():
            icon_rect = QRect(rect.left() + (rect.width() - icon_size) // 2, 
                              rect.top() + self.padding, 
                              icon_size, icon_size)
            icon.paint(painter, icon_rect, Qt.AlignmentFlag.AlignCenter)
        
        # 4. Draw Text
        if text:
            # We assume text is "Filename\nDate" or just "Filename"
            lines = text.split("\n")
            filename = lines[0]
            date_str = lines[1] if len(lines) > 1 else ""
            
            # Start slightly closer to icon (padding instead of padding*2)
            text_y = rect.top() + icon_size + self.padding + 2
            
            # Draw Filename
            painter.setPen(QColor("#cdd6f4"))
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
            
            filename_rect = QRect(rect.left() + self.padding, text_y, 
                                  rect.width() - 2*self.padding, 18) # Height 18 ample for single line
            
            fm = painter.fontMetrics()
            elided_filename = fm.elidedText(filename, Qt.TextElideMode.ElideMiddle, filename_rect.width())
            painter.drawText(filename_rect, Qt.AlignmentFlag.AlignCenter, elided_filename)
            
            # Draw Date
            if date_str:
                text_y += 18 + 2 # compact spacing
                painter.setPen(QColor("#89b4fa"))
                font.setBold(False)
                # Ensure slightly smaller font? default is usually fine
                painter.setFont(font)
                
                date_rect = QRect(rect.left() + self.padding, text_y, 
                                  rect.width() - 2*self.padding, 18)
                
                fm_date = painter.fontMetrics()
                elided_date = fm_date.elidedText(date_str, Qt.TextElideMode.ElideMiddle, date_rect.width())
                painter.drawText(date_rect, Qt.AlignmentFlag.AlignCenter, elided_date)

        painter.restore()

    def sizeHint(self, option, index):
        # Tighter size: 200w x 240h
        return QSize(200, 240)
