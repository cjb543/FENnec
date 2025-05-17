# PyQt6 suite
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                             QMessageBox, QPushButton, QFileDialog, QLineEdit,
                             QMainWindow, QApplication, QFrame, QGroupBox, QProgressBar, QTextBrowser)
from PyQt6.QtGui import (QShortcut, QKeySequence, QAction,
                         QIcon, QPainter, QColor, QFont,
                         QPen, QPainterPath, QFontDatabase)

class PGNWindow(QWidget):
    """PGN Help Window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("What is PGN?")
        self.setMinimumSize(480,640)
        self.setup_pgn_window()


    def setup_pgn_window(self):
        """Display information regarding PGN notation"""
        layout = QVBoxLayout()
        self.pgn_text = QTextBrowser(self)

        # Fetch HTML file for displaying
        pgn_html_content = open("pgn_help.html", 'r').read()
        self.pgn_text.setHtml(pgn_html_content)

        layout.addWidget(self.pgn_text)
        self.setLayout(layout)


class FENWindow(QWidget):
    """FEN Help Window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("What is FEN?")
        self.setMinimumSize(480,640)
        self.setup_fen_window()


    def setup_fen_window(self):
        """Display information regarding FEN strings"""
        layout = QVBoxLayout()
        self.fen_text = QTextBrowser(self)

        # Fetch HTML file for displaying
        fen_html_content = open("fen_help.html", 'r').read()
        self.fen_text.setHtml(fen_html_content)

        layout.addWidget(self.fen_text)
        self.setLayout(layout)
