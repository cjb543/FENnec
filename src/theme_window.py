from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QPushButton)

class ThemeWindow(QWidget):
    """Theme/Color Scheme Window"""
    def __init__(self):
        super().__init__()
        self.confirm_button = None
        self.setWindowTitle("Themes")
        self.setMinimumSize(480,640)
        self.setup_theme_list()


    def setup_theme_list(self):
        """List different themes in itemized format"""
        layout = QVBoxLayout()

        self.themes_list = QListWidget()
        self.themes_list.addItem("Classic")
        self.themes_list.addItem("Retro")
        self.themes_list.addItem("Catpuccin")
        self.themes_list.addItem("Gruvbox")
        self.themes_list.addItem("Grayscale")
        self.themes_list.addItem("Lettering")
        self.themes_list.addItem("Minimalist")


        self.confirm_button.setStyleSheet("margin: 0px 70px 0px 70px;")
        self.confirm_button = QPushButton("Confirm")

        if self.themes_list.currentItem() is not None:
            self.confirm_button.clicked.connect(self.close)

        layout.addWidget(self.themes_list)
        layout.addWidget(self.confirm_button)

        self.setLayout(layout)
