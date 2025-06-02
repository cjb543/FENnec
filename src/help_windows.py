from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextBrowser)


class PGNWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("What is PGN?")
        self.setMinimumSize(540,640)
        self.setup_pgn_window()


    def setup_pgn_window(self):
        layout = QVBoxLayout()
        self.pgn_text = QTextBrowser(self)
        pgn_html_content = open("pgn_help.html", 'r').read()
        self.pgn_text.setHtml(pgn_html_content)
        layout.addWidget(self.pgn_text)
        self.setLayout(layout)


class FENWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("What is FEN?")
        self.setMinimumSize(540,640)
        self.setup_fen_window()


    def setup_fen_window(self):
        layout = QVBoxLayout()
        self.fen_text = QTextBrowser(self)
        fen_html_content = open("fen_help.html", 'r').read()
        self.fen_text.setHtml(fen_html_content)
        layout.addWidget(self.fen_text)
        self.setLayout(layout)