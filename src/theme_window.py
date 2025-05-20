# PyQt6 suite
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QListWidget)


class ThemeWindow(QWidget):
    """Theme/Color Scheme Window"""
    def __init__(self):
        super().__init__()
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


        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.setStyleSheet("margin: 0px 70px 0px 70px;")

        layout.addWidget(self.themes_list)
        layout.addWidget(self.confirm_button)

        self.setLayout(layout)
