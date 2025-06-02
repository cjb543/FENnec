from PyQt6.QtWidgets import (QVBoxLayout, QListWidget, QPushButton)
from chess_board import *


class ThemeWindow(QWidget):
    """Theme/Color Scheme Window"""
    def __init__(self, board: ChessBoard):
        super().__init__()
        self.theme_base = board
        self.theme_classic = ThemeBase
        self.theme_retro = RetroTheme
        self.theme_catpuccin = CatpuccinTheme
        self.theme_gruvbox = GruvboxTheme
        self.theme_grayscale = GrayscaleTheme
        self.theme_lettering = LetteringTheme
        self.theme_minimalist = MinimalistTheme
        self.theme_map = {
            "Classic": ThemeBase,
            "Retro": RetroTheme,
            "Catpuccin": CatpuccinTheme,
            "Gruvbox": GruvboxTheme,
            "Grayscale": GrayscaleTheme,
            "Lettering": LetteringTheme,
            "Minimalist": MinimalistTheme,
        }
        self.chess_board = board
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
            theme_cls = self.theme_map.get(theme_name)

        match theme_name:
            case "RetroTheme":
                self.assets_dir = Path(__file__).parent.parent / "assets" / "retro-theme"
            case "CatpuccinTheme":
                self.assets_dir = Path(__file__).parent.parent / "assets" / "catpuccin-theme"
            case "GrayscaleTheme":
                self.assets_dir = Path(__file__).parent.parent / "assets" / "grayscale-theme"
            case "GruvboxTheme":
                self.assets_dir = Path(__file__).parent.parent / "assets" / "gruvbox-theme"
            case "LetteringTheme":
                self.assets_dir = Path(__file__).parent.parent / "assets" / "lettering-theme"
            case "Minimalist":
                self.assets_dir = Path(__file__).parent.parent / "assets" / "minimalist-theme"
            case _:
                self.assets_dir = Path(__file__).parent.parent / "assets" / "classic-theme"

        if theme_cls:
            self.chess_board.apply_theme(theme_cls)
            self.close()


