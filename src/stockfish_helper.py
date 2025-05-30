import math
import os
import re
import sys
from pathlib import Path
from stockfish import Stockfish
from PyQt6.QtCore import (Qt, QPoint, QThread)
from PyQt6.QtGui import (QShortcut, QKeySequence, QAction,
                         QIcon, QFont,
                         QFontDatabase, QIcon)
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                             QMessageBox, QPushButton, QFileDialog, QLineEdit,
                             QMainWindow, QApplication, QFrame, QGroupBox, QProgressBar)

class StockfishHelper(QThread):
    def __init__(self):
        super().__init__()
