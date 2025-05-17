# System paths, regex, math operations
import sys
import re
import math

# The G.O.A.T
from stockfish import Stockfish

# Project file paths
from pathlib import Path

# PyQt6 suite
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                             QMessageBox, QPushButton, QFileDialog, QLineEdit,
                             QMainWindow, QApplication, QFrame, QGroupBox, QProgressBar)
from PyQt6.QtGui import (QShortcut, QKeySequence, QAction,
                         QIcon, QPainter, QColor, QFont,
                         QPen, QPainterPath, QFontDatabase)
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import (Qt, QRectF, QPoint)

class ThemeWindow(QWidget):
    """Theme/Color Scheme Window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Themes")
        self.setMinimumSize(480,640)
        self.setup_theme_list()


    def setup_theme_list(self):
        """ List different themes in itemized format"""
        layout = QVBoxLayout()
        self.label = QLabel("Themes")
        layout.addWidget(self.label)
        self.setLayout(layout)
