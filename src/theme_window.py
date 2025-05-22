from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QPushButton)
from themes import ClassicTheme, RetroTheme, CatpuccinTheme, GruvboxTheme, GrayscaleTheme, LetteringTheme, MinimalistTheme
from chess_board import ChessBoard

theme_map = {
    "Classic": ClassicTheme,
    "Retro": RetroTheme,
    "Catpuccin": CatpuccinTheme,
    "Gruvbox": GruvboxTheme,
    "Grayscale": GrayscaleTheme,
    "Lettering": LetteringTheme,
    "Minimalist": MinimalistTheme,
}


class ThemeWindow(QWidget):
    """Theme/Color Scheme Window"""
    def __init__(self, board: ChessBoard):
        super().__init__()
        self.board = board
        self.confirm_button = None
        self.setWindowTitle("Themes")
        self.setMinimumSize(480,640)
        self.setup_theme_list()


    def setup_theme_list(self):
        """List different themes in itemized format"""
        layout = QVBoxLayout()
        self.themes_list = QListWidget()
        self.themes_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.themes_list.addItem("Classic")
        self.themes_list.addItem("Retro")
        self.themes_list.addItem("Catpuccin")
        self.themes_list.addItem("Gruvbox")
        self.themes_list.addItem("Grayscale")
        self.themes_list.addItem("Lettering")
        self.themes_list.addItem("Minimalist")
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.setStyleSheet("margin: 0px 70px 0px 70px;")
        self.confirm_button.clicked.connect(self.handle_confirm)
        layout.addWidget(self.themes_list)
        layout.addWidget(self.confirm_button)
        self.setLayout(layout)


    def handle_confirm(self):
        selected_items = self.themes_list.selectedItems()
        if selected_items:
            theme_name = selected_items[0].text()
            theme_cls = theme_map.get(theme_name)
            if theme_cls:
                self.apply_theme(theme_cls)
                self.close()
