import math
import os
import re
import sys
from pathlib import Path
from PyQt6.QtCore import (Qt, QPoint)
from PyQt6.QtGui import (QShortcut, QKeySequence, QAction,
                         QIcon, QFont,
                         QFontDatabase, QIcon)
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                             QMessageBox, QPushButton, QFileDialog, QLineEdit,
                             QMainWindow, QApplication, QFrame, QGroupBox, QProgressBar)
from chess_board import ChessBoard
from help_windows import FENWindow
from help_windows import PGNWindow
from theme_window import ThemeWindow
from processing import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.chess_board = ChessBoard()
        self.help_window = PGNWindow()
        self.fen_window = FENWindow()
        self.theme_window = ThemeWindow(self.chess_board)
        self.game_info = None
        self.prevMoveShortcut = None
        self.nextMoveShortcut = None
        self.fen_input = None
        self.date_label = None
        self.black_elo_label = None
        self.event_label = None
        self.white_elo_label = None
        self.white_name_label = None
        self.black_name_label = None
        self.white_percentage = None
        self.black_percentage = None
        self.turn_label = None
        self.setup_ui()


    def setup_ui(self):
        """Defines all UI elements"""
        central_widget = QWidget()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Add chess board
        layout.addWidget(self.chess_board)

        # Set Window Title, Size, and Icon
        self.setWindowTitle("FENnec")
        self.setWindowIcon(QIcon(''))
        self.setMinimumSize(900,700)

        # Main Widget
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Create Menu Bar
        menu_bar = self.create_menu_bar()

        # Left side: Game info panel
        info_panel = self.create_info_panel()

        # Center: Chess board and controls
        center_panel = self.create_center_panel()

        main_layout.addWidget(info_panel,1)
        main_layout.addWidget(center_panel,3)
        self.setCentralWidget(main_widget)


    def show_pgn_window(self, checked):
        """Shows the help window, allowing the user to educate themselves"""
        self.w = PGNWindow()
        main_center = QPoint(self.x() + self.width() // 2, self.y() + self.height() // 2)
        child_x = main_center.x() - self.w.width() // 2
        child_y = main_center.y() - self.w.height() // 2
        self.w.move(child_x,child_y)
        self.w.show()


    def show_fen_window(self, checked):
        """Shows the help window, allowing the user to educate themselves"""
        self.w = FENWindow()
        main_center = QPoint(self.x() + self.width() // 2, self.y() + self.height() // 2)
        child_x = main_center.x() - self.w.width() // 2
        child_y = main_center.y() - self.w.height() // 2
        self.w.move(child_x,child_y)
        self.w.show()


    def create_menu_bar(self):
        """Creates the programs menu bar"""
        menu_bar = self.menuBar()

        # "File"
        file_menu = menu_bar.addMenu('&File')

        # "File -> Import PGN..."
        import_pgn = QAction(QIcon('./assets/import_pgn.png'),
                                   'Import PGN...', self)
        import_pgn.triggered.connect(self.upload_file)
        import_pgn.setStatusTip('Import PGN')
        import_pgn.setShortcut('Ctrl+U')
        file_menu.addAction(import_pgn)

        # "Edit"
        edit_menu = menu_bar.addMenu('&Edit')

        # "Edit -> Modify Position"
        modify_position = QAction(QIcon('./assets/modify_position.png'),
                                        'Modify Position...', self)
        modify_position.triggered.connect(self.chess_board.unlock_board)
        modify_position.setStatusTip('Modify Position')
        modify_position.setShortcut('Ctrl+H')
        edit_menu.addAction(modify_position)

        # "Settings"
        settings_menu = menu_bar.addMenu('&Settings')

        # "Settings -> Change Theme"
        change_theme = QAction(QIcon('./assets/change_theme.png'),
                                     '&Change Theme...', self)
        change_theme.triggered.connect(self.change_window_theme)
        change_theme.setStatusTip('Change Theme')
        change_theme.setShortcut('Ctrl+T')
        settings_menu.addAction(change_theme)

        # "Help"
        help_menu = menu_bar.addMenu('&Help')
        help_menu.setStatusTip("Learn how to use this program")

        # "Help -> What is PGN?"
        what_is_pgn = QAction(QIcon('./assets/what_is.png'),
                                    '&What Is PGN?', self)
        what_is_pgn.triggered.connect(self.show_pgn_window)
        help_menu.addAction(what_is_pgn)

        # "Help -> What is FEN?"
        what_is_fen = QAction(QIcon('./assets/what_is_fen.png'),
                                    '&What is FEN?', self)
        what_is_fen.triggered.connect(self.show_fen_window)
        help_menu.addAction(what_is_fen)

        # Return entire menu
        return menu_bar


    def on_fen_editing_finished(self):
        """Processes user input from the FEN string box"""
        # Receive user input after Enter is pressed
        user_input = self.fen_input.text()

        # Validate provided string
        if processing._is_valid_fen(user_input):
            self.load_fen_position(user_input)

        # Print helpful error message when failed
        else:
            error_message = QMessageBox()
            error_message.setWindowTitle("Error")
            error_message.setIcon(QMessageBox.Icon.Critical)
            error_message.setStandardButtons(QMessageBox.StandardButton.Ok)
            error_message.setText("Please enter a valid FEN string.")
            error_message.exec()
        self.fen_input.clear()


    def load_fen_position(self, fen_string):
        """Loads a chess position based on a given FEN-string"""
        # Clear board
        self.chess_board.pieces = {}
        self.chess_board.positions_history = []
        self.chess_board.current_move_index = -1
        self.chess_board.is_opened = True
        
        # Parse FEN string
        parts = fen_string.split()
        position = parts[0]

        # Set board according to string
        row = 0
        col = 0

        for char in position:
            if char == '/':
                row += 1
                col = 0
            elif char.isdigit():
                col += int(char)
            else:
                # Place a piece
                color = 'w' if char.isupper() else 'b'
                piece_type = char.upper() if char.isalpha() else char
                self.chess_board.pieces[(row, col)] = color + piece_type
                col += 1

        # Update the UI
        self.chess_board.update()

        # Reset any move count label if it exists
        if hasattr(self, 'turn_label'):
           self.chess_board.update_move_count_label(self.turn_label)


    def _is_valid_fen(self, fen_string):
        """Checks the validity of a supplied FEN-string"""
        # Raw Size Constraints
        if len(fen_string) < 28:
            return False
        if len(fen_string) > 106:
            return False

        # Split into parts
        components = fen_string.split()

        # Parts size constraint
        if len(components) != 6:
            return False

        # All valid FEN strings consist of six components.
        # They are assigned here.
        # Each of these components have their own requirements
        piece_placement, active_color, castling_rights, en_passant, halfmove_clock, fullmove_number = components

        # Check if we have 8 rows
        ranks = piece_placement.split('/')
        if len(ranks) != 8:
            return False

        # Check for valid square content (valid piece/character?)
        for rank in ranks:
            squares_count = 0
            for char in rank:
                if char.isdigit():
                    squares_count += int(char)
                elif char.upper() in 'KQRBNP':
                    squares_count += 1
                else:
                    return False
            # Ensure we have 8 squares per row before continuing
            if squares_count != 8:
                return False

        # Ensure we're working with white and black pieces
        if active_color not in ['w','b']:
            return False

        # Ensure castling rights is correctly labeled
        if not all(c in 'KQkq-' for c in castling_rights):
            return False

        if castling_rights != '-':
            # No duplicate castling rights syntax
            if len(set(castling_rights)) != len(castling_rights):
                return False

            # Ensure castling rights are in the correct order
            valid_order = ''
            for c in 'KQkq':
                if c in castling_rights:
                    valid_order += c
            if castling_rights != valid_order:
                return False

        # Check en-passant square
        if en_passant != '-':
            if len(en_passant) != 2:
                return False
            if en_passant[0] not in 'abcdefgh' or en_passant[1] not in '36':
                return False

        # All checks pass
        return True


    def handle_next_move_action(self):
        """Calls the next_move method and updates the game label accordingly"""
        if self.chess_board.next_move():
            self.chess_board.update_move_count_label(self.turn_label)


    def handle_previous_move_action(self):
        """Calls the previous_move method and updates the game label accordingly"""
        if self.chess_board.previous_move():
            self.chess_board.update_move_count_label(self.turn_label)


    def handle_last_move_action(self):
        """Calls the last_move method and updates the game label accordingly"""
        if self.chess_board.last_move():
            self.chess_board.update_move_count_label(self.turn_label)


    def handle_reset_action(self):
        """Calls the reset_to_start method and updates the game label accordingly"""
        self.chess_board.reset_to_start()
        self.chess_board.update_move_count_label(self.turn_label)


    def create_info_panel(self):
        """Creates the non-move information panel"""
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.StyledPanel)
        info_frame.setFrameShadow(QFrame.Shadow.Raised)
        info_layout = QVBoxLayout(info_frame)

        # Game information section
        info_group = QGroupBox("Game Information")
        info_group_layout = QVBoxLayout(info_group)
        info_group_layout.addStretch(1)

        # Additional game info
        self.white_name_label = QLabel("White:")
        self.white_elo_label = QLabel("Elo:")
        self.black_name_label = QLabel("Black:")
        self.black_elo_label = QLabel("Elo:")
        self.event_label = QLabel("Event:")
        self.date_label = QLabel("Date:")
        self.turn_label = QLabel("Turn:")
        self.winner_label = QLabel("Result:")
        self.best_move_label = QLabel("Best Move:")
        self.evaluation_bar = QProgressBar()
        self.event_label.setWordWrap(True)
        info_group_layout.addWidget(self.white_name_label)
        info_group_layout.addWidget(self.white_elo_label)
        info_group_layout.addWidget(self.black_name_label)
        info_group_layout.addWidget(self.black_elo_label)
        info_group_layout.addWidget(self.event_label)
        info_group_layout.addWidget(self.date_label)
        info_group_layout.addWidget(self.turn_label)
        info_group_layout.addWidget(self.winner_label)

        # PGN Import and FEN-string section
        import_group = QGroupBox("Import Game")
        import_layout = QVBoxLayout(import_group)
        self.fen_input = QLineEdit()
        self.fen_input.editingFinished.connect(self.on_fen_editing_finished)
        self.fen_input.setPlaceholderText("Import FEN String...")
        upload_button = QPushButton("Import PGN")
        upload_button.setIcon(QIcon('./assets/import_pgn.png'))
        upload_button.clicked.connect(self.upload_file)
        import_layout.addWidget(self.fen_input)
        import_layout.addWidget(upload_button)

        # Stockfish group
        self.white_percentage = QLabel("0%")
        self.white_percentage.setStyleSheet("font-size: 11px;")
        self.black_percentage = QLabel("0%")
        self.black_percentage.setStyleSheet("font-size: 11px;")
        self.black_percentage.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.evaluation_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.evaluation_bar.setRange(0,1000)
        self.evaluation_bar.setValue(500)
        self.evaluation_bar.setTextVisible(False)
        fish_group = QGroupBox("Stockfish")
        fish_group.setStyleSheet("margin-bottom: 6px")
        fish_layout = QVBoxLayout(fish_group)
        fish_layout.addWidget(self.best_move_label)
        fish_layout.addWidget(self.evaluation_bar)
        percentages_layout = QHBoxLayout(fish_group)
        percentages_layout.addWidget(self.white_percentage)
        percentages_layout.addWidget(self.black_percentage)
        fish_layout.addLayout(percentages_layout)
        fish_layout.addStretch(1)

        # Capture Count
        capture_count_group = QGroupBox("Capture Count")
        capture_count_layout = QVBoxLayout(capture_count_group)
        capture_count_layout.addStretch(1)

        # Add components to info panel
        info_layout.addWidget(info_group)
        info_layout.addWidget(import_group)
        info_layout.addWidget(fish_group)
        info_layout.addWidget(capture_count_group)
        info_layout.addStretch(1)

        # Return entire information frame
        return info_frame


    def create_center_panel(self):
        """Creates the panel containing the chess board, as well as arrow buttons"""
        center_frame = QFrame()
        center_layout = QVBoxLayout(center_frame)

        # Arrow key layout
        nav_container = QWidget()
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)

        # First Move (<<)
        first_move_button = QPushButton("⟪")
        first_move_button.setToolTip("First Move")
        first_move_button.clicked.connect(self.handle_reset_action)

        # Previous Move (<-)
        previous_move_button = QPushButton("◂")
        previous_move_button.setToolTip("Previous Move")
        previous_move_button.clicked.connect(self.handle_previous_move_action)
        self.prevMoveShortcut = QShortcut(QKeySequence('Left'), self)
        self.prevMoveShortcut.activated.connect(self.handle_previous_move_action)

        # Next Move (->)
        next_move_button = QPushButton("▸")
        next_move_button.setToolTip("Next Move")
        next_move_button.clicked.connect(self.handle_next_move_action)
        self.nextMoveShortcut = QShortcut(QKeySequence('Right'), self)
        self.nextMoveShortcut.activated.connect(self.handle_next_move_action)

        # Last Move (>>)
        last_move_button = QPushButton("⟫")
        last_move_button.setToolTip("Last Move")
        last_move_button.clicked.connect(self.handle_last_move_action)

        # Add to navigation layout
        nav_layout.addStretch(1)
        nav_layout.addWidget(first_move_button)
        nav_layout.addWidget(previous_move_button)
        nav_layout.addWidget(next_move_button)
        nav_layout.addWidget(last_move_button)
        nav_layout.addStretch(1)

        # Add board and nav to same layout
        center_layout.addWidget(self.chess_board, 1)
        center_layout.addWidget(nav_container)

        # Return board and nav layout together
        return center_frame


    def change_window_theme(self):
        """Opens a program window to allow the user to change board themes"""
        self.w = ThemeWindow(self.chess_board)
        main_center = QPoint(self.x() + self.width() // 2, self.y() + self.height() // 2)
        child_x = main_center.x() - self.w.width() // 2
        child_y = main_center.y() - self.w.height() // 2
        self.w.move(child_x,child_y)
        self.w.show()


    def upload_file(self):
        """Prompts the user to upload a PGN file"""
        documents_dir = str(Path.home() / "Documents")
        file_name = QFileDialog.getOpenFileName(
            self,
            'Open PGN File',
            documents_dir,
            'PGN Files(*.pgn);;Text Files(*.txt);;All Files (*.*)',
        )
        if file_name[0]:
            self.load_file(file_name[0])


    def load_file(self, filepath):
        """Attempts to load the user-selected PGN file"""
        try:
            file_extension = Path(filepath).suffix.lower()
            if file_extension not in ['.pgn', '.txt']:
                QMessageBox.warning(self, "Invalid File", "Please select a .pgn or .txt file")
                return
            with open(filepath, 'r') as file:
                pgn_content = file.read()
            if is_valid_pgn(pgn_content):
                self.game_info = process_pgn(pgn_content)
                self.update_labels()
            else:
                QMessageBox.warning(self, "Invalid PGN", "The file does not contain valid PGN notation")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading file: {e}")


    def process_pgn(self, pgn_content):
        """Fills the game_info list with PGN content"""
        game_info = extract_game_info(pgn_content)
        parse_pgn(pgn_content)
        self.reset_to_start()
        return game_info


    def update_labels(self):
        """Updates the UI labels with information from the loaded PGN game."""
        if hasattr(self, 'game_info') and isinstance(self.game_info, dict) and self.game_info:
            white_player = self.game_info.get('white_player', 'N/A')
            black_player = self.game_info.get('black_player', 'N/A')
            white_elo = self.game_info.get('white_elo', 'N/A')
            black_elo = self.game_info.get('black_elo', 'N/A')
            game_date = self.game_info.get('date', 'N/A')
            game_event = self.game_info.get('event', 'N/A')
            winner = self.game_info.get('winner', 'N/A')

            # Set all labels to their respective fields
            self.white_name_label.setText(f"White: {white_player}")
            self.black_name_label.setText(f"Black: {black_player}")
            self.white_elo_label.setText(f"Elo: {white_elo}")
            self.black_elo_label.setText(f"Elo: {black_elo}")
            self.date_label.setText(f"Date: {game_date}")
            self.event_label.setText(f"Event: {game_event}")
            self.winner_label.setText(f"Winner: {winner}")
        else:
            self.white_name_label.setText("White: N/A")
            self.black_name_label.setText("Black: N/A")
            self.white_elo_label.setText("Elo: N/A")
            self.black_elo_label.setText("Elo: N/A")
            self.date_label.setText("Date: N/A")
            self.event_label.setText("Event: N/A")
            self.winner_label.setText("Winner: N/A")
        self.chess_board.update_move_count_label(self.turn_label)


    def update_move_count_label(self, label_widget: QLabel):
        """Update the turn label to show the current move count and total moves."""
        current_move = self.current_move_index + 1
        total_moves = self.get_move_count()
        if label_widget:
            label_widget.setText(f"({current_move}/{total_moves})")

    # TODO:
    def unlock_board(self):
        """Allows the user to edit the chess board"""
        self.board_unlocked = True
        self.selected_square = None
        pass


# Only run if called directly
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Windows')

    # Enable app CSS
    QFontDatabase.addApplicationFont('../resources/Avenir_Light.ttf')
    with open("./styles.qss", "r") as f:
        style = f.read()
        app.setStyleSheet(style)

    # Run app
    window = MainWindow()

    # Set Icons
    if sys.platform == "win32":
        window.setWindowIcon(QIcon("../assets/icons/icon512x512ico.ico"))
        import ctypes
        myappid ='cjb543.FENnec.FENnec.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    elif sys.platform.startswith("linux"):
        window.setWindowIcon(QIcon("../assets/icons/icon512x512png.png"))
    else:
        print("Incompatible OS")
    
    window.show()
    app.exec()
