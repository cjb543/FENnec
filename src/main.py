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

# help_window.py, theme_window.py
from help_windows import PGNWindow
from help_windows import FENWindow
from theme_window import ThemeWindow
from chess_board import ChessBoard

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.chess_board = ChessBoard()
        self.help_window = PGNWindow()
        self.fen_window = FENWindow()
        self.theme_window = ThemeWindow()
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
        self.summon_the_fish()
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

        # Change positioning of window for better experience
        main_center = QPoint(self.x() + self.width() // 2, self.y() + self.height() // 2)
        child_x = main_center.x() - self.w.width() // 2
        child_y = main_center.y() - self.w.height() // 2
        self.w.move(child_x,child_y)

        self.w.show()


    def show_fen_window(self, checked):
        """Shows the help window, allowing the user to educate themselves"""
        self.w = FENWindow()

        # Change positioning of window for better experience
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
        if self._is_valid_fen(user_input):
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
        
        if self._is_valid_fen(fen_string):
            self._set_fish_position(fen_string)

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

            # Ensure castling rights are in right order
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
            self.update_stockfish_evaluation()


    def handle_previous_move_action(self):
        """Calls the previous_move method and updates the game label accordingly"""
        if self.chess_board.previous_move():
            self.chess_board.update_move_count_label(self.turn_label)
            self.update_stockfish_evaluation()


    def handle_last_move_action(self):
        """Calls the last_move method and updates the game label accordingly"""
        if self.chess_board.last_move():
            self.chess_board.update_move_count_label(self.turn_label)
            self.update_stockfish_evaluation()


    def handle_reset_action(self):
        """Calls the reset_to_start method and updates the game label accordingly"""
        self.chess_board.reset_to_start()
        self.chess_board.update_move_count_label(self.turn_label)
        self.update_stockfish_evaluation()


    def create_info_panel(self):
        """Creates the non-move information panel"""
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.StyledPanel)
        info_frame.setFrameShadow(QFrame.Shadow.Raised)
        info_layout = QVBoxLayout(info_frame)

        # Game information section
        info_group = QGroupBox("Game Information")
        info_group.setStyleSheet("padding-top: 16px;")
        info_group_layout = QVBoxLayout(info_group)
        info_group_layout.addStretch(1)

        # Player 1 (White)
        player1_container = QWidget()
        player1_layout = QHBoxLayout(player1_container)
        player1_layout.setContentsMargins(0, 0, 0, 0)
        player1_image = QLabel()
        player1_image.setFixedSize(60, 60)
        player1_image.setStyleSheet("color: white")
        player1_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        player1_image.setText("♔")
        player1_image.setFont(QFont("Arial", 24))
        player1_info = QWidget()
        player1_info_layout = QVBoxLayout(player1_info)
        player1_info_layout.setContentsMargins(0, 0, 0, 0)
        self.white_name_label = QLabel("White:")
        self.white_elo_label = QLabel("Elo:")
        player1_info_layout.addWidget(self.white_name_label)
        player1_info_layout.addWidget(self.white_elo_label)
        player1_layout.addWidget(player1_image)
        player1_layout.addWidget(player1_info, 1)

        # Player 2 (Black)
        player2_container = QWidget()
        player2_layout = QHBoxLayout(player2_container)
        player2_layout.setContentsMargins(0, 0, 0, 0)
        player2_image = QLabel()
        player2_image.setFixedSize(60, 60)
        player2_image.setStyleSheet("color: black;")
        player2_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        player2_image.setText("♚")
        player2_image.setFont(QFont("Arial", 24))
        player2_info = QWidget()
        player2_info_layout = QVBoxLayout(player2_info)
        player2_info_layout.setContentsMargins(0, 0, 0, 0)
        self.black_name_label = QLabel("Black:")
        self.black_elo_label = QLabel("Elo:")
        player2_info_layout.addWidget(self.black_name_label)
        player2_info_layout.addWidget(self.black_elo_label)
        player2_layout.addWidget(player2_image)
        player2_layout.addWidget(player2_info, 1)

        # Additional game info
        self.event_label = QLabel("Event:")
        self.date_label = QLabel("Date:")
        self.turn_label = QLabel("Turn:")
        self.winner_label = QLabel("Result:")
        self.best_move_label = QLabel("Best Move:")
        self.evaluation_bar = QProgressBar()
        self.event_label.setWordWrap(True)
        info_group_layout.addWidget(player1_container)
        info_group_layout.addWidget(player2_container)
        info_group_layout.addSpacing(10)
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

        # Add components to info panel
        info_layout.addWidget(info_group)
        info_layout.addWidget(import_group)
        info_layout.addWidget(fish_group)
        info_layout.addStretch(1)

        # Return entire information frame
        return info_frame


    def summon_the_fish(self):
        """Initializes and parameterizes the local stockfish engine"""
        self.stockfish = Stockfish("/usr/games/stockfish",depth=2,parameters={"Threads":2, "Minimum Thinking Time": 5})


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


    def _set_fish_position(self, moves):
        """Sets a stockfish position for evaluation based on a passed in position (moves)"""
        if self.stockfish.is_fen_valid(moves):
            self.stockfish.set_fen_position(moves)
        else:
            self.stockfish.set_position(moves)
        self.update_stockfish_evaluation()


    def update_stockfish_evaluation(self):
        """Updates the stockfish evaluation bar and percentages"""
        # Ensure a move is loaded and that a game instance exists
        if not hasattr(self, 'chess_board') or not self.chess_board:
            return

        print("stockfish_eval function reached")

        # Ensure there is a position on the board
        current_position = self.chess_board.get_current_position()
        if not current_position:
            return

        # Pass stockfish board position, get evaluation
        self.stockfish.set_fen_position(current_position)
        evaluation = self.stockfish.get_evaluation()

        # Get best move
        best_move = self.stockfish.get_best_move()
        if best_move:
            self.best_move_label.setText(f"Best Move: {best_move}")
        else:
            self.best_move_label.setText("Best Move: N/A")

        # Calculate win percentages
        win_percentage = 50
        if evaluation['type'] == 'cp':
            advantage = evaluation['value'] / 100.0
            win_percentage = 50 + 50 * (2 / (1 + math.exp(-0.5 * advantage)) - 1)
        elif evaluation['type'] == 'mate':  # Checkmate found
            # If mate is found, give a high percentage to the winning side
            if evaluation['value'] > 0:
                win_percentage = 99
            else:
                win_percentage = 1

            # Ensure win percentage is within bounds
            win_percentage = max(1, min(99, win_percentage))

            # Update the progress bar (0-100 scale)
            self.evaluation_bar.setValue(int(win_percentage))

            # Update percentage labels
            white_percentage = win_percentage
            black_percentage = 100 - white_percentage
            self.white_percentage.setText(f"{int(white_percentage)}%")
            self.black_percentage.setText(f"{int(black_percentage)}%")
            self.update()



    def change_window_theme(self):
        """Opens a program windw to allow the user to change board themes"""
        # Open the general theme window for selecting
        self.w = ThemeWindow()

        # Change positioning of window for better experience
        main_center = QPoint(self.x() + self.width() // 2, self.y() + self.height() // 2)
        child_x = main_center.x() - self.w.width() // 2
        child_y = main_center.y() - self.w.height() // 2
        self.w.move(child_x,child_y)

        # Show window (self keeps it perpetual)
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
                extracted_info = self.chess_board.process_pgn(pgn_content)
                self.game_info = extracted_info
                self.update_labels()
            else:
                QMessageBox.warning(self, "Invalid PGN", "The file does not contain valid PGN notation")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading file: {e}")


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
        self.update_stockfish_evaluation()

# Static processing functions
def is_valid_pgn(content):
    """Determines if a PGN file has valid formatting"""
    if not re.search(r'\[.+]', content):
        return False
    if not re.search(r'\d+\.', content):
        return False
    return True


def extract_moves_from_pgn(pgn_content):
    """Removes non-move info from PGN file"""
    if '\n\n' in pgn_content:
        return pgn_content.split('\n\n', 1)[1]
    return pgn_content


def extract_moves_list(moves_text):
    """Returns a list of moves from PGN file"""
    moves_text = re.sub(r'\{[^}]*}', '', moves_text)
    moves_text = re.sub(r'\([^)]*\)', '', moves_text)
    moves_text = re.sub(r'1-0|0-1|1/2-1/2|\*', '', moves_text)
    move_pattern = r'(?:\d+\.+\s*)?([KQRBNP]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?|O-O(?:-O)?)'
    moves = re.findall(move_pattern, moves_text)
    return [move for move in moves if move.strip()]


def apply_move_to_position(move, position, player, board):
    """Applies the move data to the chess board"""
    new_position = position.copy()
    if move == "O-O":
        if player == 'w':
            if (7, 4) in new_position and (7, 7) in new_position:
                new_position[(7, 6)] = new_position.pop((7, 4))
                new_position[(7, 5)] = new_position.pop((7, 7))
        else:
            if (0, 4) in new_position and (0, 7) in new_position:
                new_position[(0, 6)] = new_position.pop((0, 4))
                new_position[(0, 5)] = new_position.pop((0, 7))
        return new_position
    if move == "O-O-O":
        if player == 'w':
            new_position[(7, 2)] = new_position.pop((7, 4))
            new_position[(7, 3)] = new_position.pop((7, 0))
        else:
            new_position[(0, 2)] = new_position.pop((0, 4))
            new_position[(0, 3)] = new_position.pop((0, 0))
        return new_position

    move_data = parse_move_notation(move, player)
    source_square = find_source_square(move_data, new_position, player, board)
    if source_square:
        target_square = (move_data['target_row'], move_data['target_col'])
        if target_square in new_position:
            del new_position[target_square]
        piece = new_position.pop(source_square)
        if move_data['promotion']:
            piece = player + move_data['promotion']
        new_position[target_square] = piece
    return new_position


def parse_move_notation(move, player):
    result: dict[str, str | None | bool | int] = {
        'piece': 'P',
        'source_file': None,
        'source_rank': None,
        'target_col': None,
        'target_row': None,
        'is_capture': 'x' in move,
        'promotion': None
    }

    move = move.replace('+', '').replace('#', '')
    if '=' in move:
        move_part, promotion = move.split('=')
        result['promotion'] = promotion
        move = move_part
    if move[0] in "KQRBNP":
        result['piece'] = move[0]
        move = move[1:]
    target_file = move[-2]
    target_rank = move[-1]
    result['target_col'] = ord(target_file) - ord('a')
    result['target_row'] = 8 - int(target_rank)
    move = move[:-2]
    if 'x' in move:
        move = move.replace('x', '')
    if len(move) > 0 and 'a' <= move[0] <= 'h':
        result['source_file'] = ord(move[0]) - ord('a')
    if len(move) > 0 and '1' <= move[-1] <= '8':
        result['source_rank'] = 8 - int(move[-1])
    return result


def find_source_square(move_data, position, player, board):
    target_row = move_data['target_row']
    target_col = move_data['target_col']
    piece = move_data['piece']
    piece_code = player + piece
    source_file = move_data['source_file']
    source_rank = move_data['source_rank']
    is_capture = move_data['is_capture']

    # Handle pawn special cases first
    if piece == 'P':
        pawn_source = find_pawn_source(move_data, position, player)
        if pawn_source:
            return pawn_source
    # Find all pieces of the correct type
    candidates = []
    for (row, col), board_piece in position.items():
        if board_piece != piece_code:
            continue

        # Filter by source file/rank if specified
        if source_file is not None and col != source_file:
            continue
        if source_rank is not None and row != source_rank:
            continue

        # Check if the piece can legally move to the target
        if can_piece_move_to_target(piece, row, col, target_row,
                                    target_col, position, player,
                                    is_capture, board):
            candidates.append((row, col))

    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) > 1:
        return candidates[0]

    return None


def find_pawn_source(move_data, position, player):
    target_row = move_data['target_row']
    target_col = move_data['target_col']
    source_file = move_data['source_file']
    is_capture = move_data['is_capture']

    # Define direction and starting rank based on player color
    direction = 1 if player == 'b' else -1
    pawn_code = player + 'P'
    starting_rank = 1 if player == 'b' else 6
    double_move_rank = 3 if player == 'b' else 4

    if source_file is None and not is_capture:
        one_square = (target_row + direction, target_col)
        if one_square in position and position[one_square] == pawn_code:
            return one_square

    if target_row == double_move_rank:
        two_square = (starting_rank, target_col)
        if two_square in position and position[two_square] == pawn_code:
            return two_square

    elif is_capture and source_file is not None:
        capture_square = (target_row + direction, source_file)
        if capture_square in position and position[capture_square] == pawn_code:
            return capture_square

    return None


def can_piece_move_to_target(piece_type, row, col, target_row, target_col,
                             position, player, is_capture, board):
    # Pawn movement rules
    if piece_type == 'P':
        return can_pawn_move_to_target(row, col, target_row,
                                       target_col, player, is_capture)
    # Knight movement rules
    elif piece_type == 'N':
        return ((abs(row - target_row) == 2 and abs(col - target_col) == 1) or
                (abs(row - target_row) == 1 and abs(col - target_col) == 2))
    # Bishop movement rules
    elif piece_type == 'B':
        return (abs(row - target_row) == abs(col - target_col) and
                is_diagonal_path_clear(position, row, col,
                                       target_row, target_col))
    # Rook movement rules
    elif piece_type == 'R':
        return ((row == target_row or col == target_col) and
                is_straight_path_clear(position, row, col,
                                       target_row, target_col))
    # Queen movement rules
    elif piece_type == 'Q':
        if row == target_row or col == target_col:
            return is_straight_path_clear(position, row, col,
                                          target_row, target_col)
        elif abs(row - target_row) == abs(col - target_col):
            return is_diagonal_path_clear(position, row, col,
                                          target_row, target_col)
        return False
    # King movement rules
    elif piece_type == 'K':
        return abs(row - target_row) <= 1 and abs(col - target_col) <= 1
    return False


def can_pawn_move_to_target(row, col, target_row,
                            target_col, player, is_capture):
    if not is_capture:
        if player == 'w':
            return row > target_row and col == target_col
        else:
            return row < target_row and col == target_col
    else:
        if player == 'w':
            return row > target_row and abs(col - target_col) == 1
        else:
            return row < target_row and abs(col - target_col) == 1


def is_diagonal_path_clear(position, start_row, start_col, end_row, end_col):
    row_step = 1 if end_row > start_row else -1
    col_step = 1 if end_col > start_col else -1
    row, col = start_row + row_step, start_col + col_step
    while (row, col) != (end_row, end_col):
        if (row, col) in position:
            return False
        row += row_step
        col += col_step
    return True


def is_straight_path_clear(position, start_row, start_col, end_row, end_col):
    if start_row == end_row:
        col_step = 1 if end_col > start_col else -1
        for col in range(start_col + col_step, end_col, col_step):
            if (start_row, col) in position:
                return False
    else:
        row_step = 1 if end_row > start_row else -1
        for row in range(start_row + row_step, end_row, row_step):
            if (row, start_col) in position:
                return False
    return True


def generate_positions_from_moves(moves, initial_position):
    current_position = initial_position
    current_player = 'w'
    positions_history = []
    for i, move in enumerate(moves):
        try:
            current_position = apply_move_to_position(move, current_position,
                                                      current_player, None)
            positions_history.append(current_position.copy())
            current_player = 'b' if current_player == 'w' else 'w'
        except Exception as e:
            print(f"Error at move {i+1} ({move}): {e}")
            break
    return positions_history


def extract_game_info(pgn_content):
    game_info = {
        'white_player': 'N/A',
        'white_elo': 'N/A',
        'black_player': 'N/A',
        'black_elo': 'N/A',
        'date': 'N/A',
        'event': 'N/A',
        'winner': 'N/A'
    }

    # Find info panel patterns
    white_player_pattern = r'\[White\s+"([^"]+)"\]'
    white_elo_pattern = r'\[WhiteElo\s+"([^"]+)"\]'
    black_player_pattern = r'\[Black\s+"([^"]+)"\]'
    black_elo_pattern = r'\[BlackElo\s+"([^"]+)"\]'
    date_pattern = r'\[Date\s+"([^"]+)"\]'
    event_pattern = r'\[Event\s+"([^"]+)"\]'
    result_pattern = r'\[Result\s+"([^"]+)"\]'

    # The standards for inserting names into PGN files is an non-standard mess, so just
    # try to catch everything up to 3 "words" long
    white_player_match = re.search(white_player_pattern, pgn_content)
    if white_player_match:
        full_name = white_player_match.group(1)
        name_parts = full_name.split()[:3] # 3 "words" long
        name_parts = [part.replace(',', '') for part in name_parts][::1]
        game_info['white_player'] = ' '.join(name_parts)

    white_elo_match = re.search(white_elo_pattern, pgn_content)
    if white_elo_match:
        game_info['white_elo'] = white_elo_match.group(1)

    black_player_match = re.search(black_player_pattern, pgn_content)
    if black_player_match:
        full_name = black_player_match.group(1)
        name_parts = full_name.split()[:3] # 3 "words" long
        name_parts = [part.replace(',', '') for part in name_parts][::1]
        game_info['black_player'] = ' '.join(name_parts)

    black_elo_match = re.search(black_elo_pattern, pgn_content)
    if black_elo_match:
        game_info['black_elo'] = black_elo_match.group(1)

    date_match = re.search(date_pattern, pgn_content)
    if date_match:
        game_info['date'] = date_match.group(1)

    event_match = re.search(event_pattern, pgn_content)
    if event_match:
        game_info['event'] = event_match.group(1)

    result_match = re.search(result_pattern, pgn_content)
    if result_match:
        result = result_match.group(1)
        if result == "1-0":
            game_info['winner'] = "White"
        elif result == "0-1":
            game_info['winner'] = "Black"
        elif result == "1/2-1/2":
            game_info['winner'] = "Draw"
        else:
            game_info['winner'] = "Unknown"

    return game_info

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
    window.show()
    app.exec()
