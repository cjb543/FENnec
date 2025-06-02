import re, sys , time, traceback, threading
from pathlib import Path
from stockfish import Stockfish
from PyQt6.QtCore import (Qt, QPoint, QThread, pyqtSignal, QThreadPool, pyqtSlot, QObject, QRunnable)
from PyQt6.QtGui import (QShortcut, QKeySequence, QAction,
                         QFontDatabase, QIcon)
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                             QMessageBox, QPushButton, QFileDialog, QLineEdit,
                             QMainWindow, QApplication, QFrame, QGroupBox, QProgressBar)
from chess_board import ChessBoard
from help_windows import FENWindow, PGNWindow
from theme_window import ThemeWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.fen_mode = False
        self.uci_pointer = 0
        self.uci_moves = None
        self.current_fen = ""
        self.stockfish = Stockfish("../resources/stockfish/stockfish-windows/stockfish.exe")
        self.chess_board = ChessBoard()
        self.Worker = Worker(self)
        self.WorkerSignals = WorkerSignals()
        self.help_window = PGNWindow()
        self.fen_window = FENWindow()
        self.theme_window = ThemeWindow(self.chess_board)
        self.menu_bar = None
        self.evaluation_bar = None
        self.best_move_label = None
        self.winner_label = None
        self.w = None
        self.is_opened = None
        self.current_move_index = None
        self.positions_history = None
        self.selected_square = None
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
        self.threadpool = QThreadPool()
        self.setup_ui()


    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.addWidget(self.chess_board)
        self.setWindowTitle("FENnec")
        self.setWindowIcon(QIcon(''))
        self.setFixedSize(900,700)
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.menu_bar = self.create_menu_bar()
        info_panel = self.create_info_panel()
        center_panel = self.create_center_panel()
        main_layout.addWidget(info_panel,1)
        main_layout.addWidget(center_panel,3)
        self.setCentralWidget(main_widget)


    def show_pgn_window(self):
        self.w = PGNWindow()
        main_center = QPoint(self.x() + self.width() // 2, self.y() + self.height() // 2)
        child_x = main_center.x() - self.w.width() // 2
        child_y = main_center.y() - self.w.height() // 2
        self.w.move(child_x,child_y)
        self.w.show()


    def show_fen_window(self):
        self.w = FENWindow()
        main_center = QPoint(self.x() + self.width() // 2, self.y() + self.height() // 2)
        child_x = main_center.x() - self.w.width() // 2
        child_y = main_center.y() - self.w.height() // 2
        self.w.move(child_x,child_y)
        self.w.show()


    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        import_pgn = QAction(QIcon('./assets/import_pgn.png'),
                                   'Import PGN...', self)
        import_pgn.triggered.connect(self.upload_file)
        import_pgn.setStatusTip('Import PGN')
        import_pgn.setShortcut('Ctrl+U')
        file_menu.addAction(import_pgn)
        edit_menu = menu_bar.addMenu('&Edit')
        modify_position = QAction(QIcon('./assets/modify_position.png'),
                                        'Modify Position...', self)
        modify_position.triggered.connect(unlock_board)
        modify_position.setStatusTip('Modify Position')
        modify_position.setShortcut('Ctrl+H')
        edit_menu.addAction(modify_position)
        settings_menu = menu_bar.addMenu('&Settings')
        change_theme = QAction(QIcon('./assets/change_theme.png'),
                                     '&Change Theme...', self)
        change_theme.triggered.connect(self.open_theme_window)
        change_theme.setStatusTip('Change Theme')
        change_theme.setShortcut('Ctrl+T')
        settings_menu.addAction(change_theme)
        help_menu = menu_bar.addMenu('&Help')
        help_menu.setStatusTip("Learn how to use this program")
        what_is_pgn = QAction(QIcon('./assets/what_is.png'),
                                    '&What Is PGN?', self)
        what_is_pgn.triggered.connect(self.show_pgn_window)
        help_menu.addAction(what_is_pgn)
        what_is_fen = QAction(QIcon('./assets/what_is_fen.png'),
                                    '&What is FEN?', self)
        what_is_fen.triggered.connect(self.show_fen_window)
        help_menu.addAction(what_is_fen)
        return menu_bar


    def on_fen_editing_finished(self):
        self.fen_mode = True
        user_input = self.fen_input.text().strip()
        if not user_input:
            return
        try:
            if hasattr(self, "stockfish") and self.stockfish.is_fen_valid(user_input):
                print("Valid FEN")
                self.load_fen_position(user_input)
                self.evaluate_position(user_input)
            else:
                print("Invalid FEN")
                error_message = QMessageBox()
                error_message.setWindowTitle("Error")
                error_message.setIcon(QMessageBox.Icon.Critical)
                error_message.setStandardButtons(QMessageBox.StandardButton.Ok)
                error_message.setText("Please enter a valid FEN string.")
                error_message.exec()
        except Exception as e:
            print(f"Error checking FEN: {e}")
        self.fen_input.clear()


    def load_fen_position(self, fen_string):
        self.chess_board.pieces = {}
        self.chess_board.positions_history = []
        self.chess_board.current_move_index = -1
        self.chess_board.is_opened = True
        parts = fen_string.split()
        position = parts[0]
        row = 0
        col = 0
        for char in position:
            if char == '/':
                row += 1
                col = 0
            elif char.isdigit():
                col += int(char)
            else:
                color = 'w' if char.isupper() else 'b'
                piece_type = char.upper() if char.isalpha() else char
                self.chess_board.pieces[(row, col)] = color + piece_type
                col += 1
        self.chess_board.update()
        if hasattr(self, 'turn_label'):
           self.chess_board.update_move_count_label(self.turn_label)


    def handle_next_move_action(self):
        if self.chess_board.next_move():
            self.uci_pointer+=1
            self.evaluate_position(self.uci_moves)
            self.chess_board.update_move_count_label(self.turn_label)
    def handle_previous_move_action(self):
        if self.chess_board.previous_move():
            self.uci_pointer-=1
            self.evaluate_position(self.uci_moves)
            self.chess_board.update_move_count_label(self.turn_label)
    def handle_last_move_action(self):
        if self.chess_board.last_move():
            self.uci_pointer = len(self.chess_board.positions_history)
            self.evaluate_position(self.uci_moves)
            self.chess_board.update_move_count_label(self.turn_label)
    def handle_reset_action(self):
        self.chess_board.reset_to_start()
        self.uci_pointer = 0
        self.evaluate_position(self.uci_moves)
        self.chess_board.update_move_count_label(self.turn_label)


    def create_info_panel(self):
        info_frame = QFrame()
        info_frame.setContentsMargins(0,75,0,125)
        info_frame.setFrameShape(QFrame.Shape.StyledPanel)
        info_frame.setFrameShadow(QFrame.Shadow.Raised)
        info_layout = QVBoxLayout(info_frame)
        info_group = QGroupBox("Game Information")
        info_group_layout = QVBoxLayout(info_group)
        info_group_layout.addStretch(1)
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
        fish_layout = QVBoxLayout(fish_group)
        fish_layout.addWidget(self.best_move_label)
        fish_layout.addWidget(self.evaluation_bar)
        percentages_layout = QHBoxLayout(fish_group)
        percentages_layout.addWidget(self.white_percentage)
        percentages_layout.addWidget(self.black_percentage)
        fish_layout.addLayout(percentages_layout)
        fish_layout.addStretch(1)
        info_layout.addWidget(info_group)
        info_layout.addWidget(import_group)
        info_layout.addWidget(fish_group)
        info_layout.addStretch(1)
        return info_frame


    def create_center_panel(self):
        center_frame = QFrame()
        center_layout = QVBoxLayout(center_frame)
        nav_container = QWidget()
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        first_move_button = QPushButton("⟪")
        first_move_button.setToolTip("First Move")
        first_move_button.clicked.connect(self.handle_reset_action)
        previous_move_button = QPushButton("◂")
        previous_move_button.setToolTip("Previous Move")
        previous_move_button.clicked.connect(self.handle_previous_move_action)
        self.prevMoveShortcut = QShortcut(QKeySequence('Left'), self)
        self.prevMoveShortcut.activated.connect(self.handle_previous_move_action)
        next_move_button = QPushButton("▸")
        next_move_button.setToolTip("Next Move")
        next_move_button.clicked.connect(self.handle_next_move_action)
        self.nextMoveShortcut = QShortcut(QKeySequence('Right'), self)
        self.nextMoveShortcut.activated.connect(self.handle_next_move_action)
        last_move_button = QPushButton("⟫")
        last_move_button.setToolTip("Last Move")
        last_move_button.clicked.connect(self.handle_last_move_action)
        nav_layout.addStretch(1)
        nav_layout.addWidget(first_move_button)
        nav_layout.addWidget(previous_move_button)
        nav_layout.addWidget(next_move_button)
        nav_layout.addWidget(last_move_button)
        nav_layout.addStretch(1)
        center_layout.addWidget(self.chess_board, 1)
        center_layout.addWidget(nav_container)
        return center_frame


    def open_theme_window(self):
        self.w = ThemeWindow(self.chess_board)
        main_center = QPoint(self.x() + self.width() // 2, self.y() + self.height() // 2)
        child_x = main_center.x() - self.w.width() // 2
        child_y = main_center.y() - self.w.height() // 2
        self.w.move(child_x,child_y)
        self.w.show()


    def upload_file(self):
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
        try:
            file_extension = Path(filepath).suffix.lower()
            if file_extension not in ['.pgn', '.txt']:
                QMessageBox.warning(self, "Invalid File", "Please select a .pgn or .txt file")
                return
            with open(filepath, 'r') as file:
                pgn_content = file.read()
            if is_valid_pgn(pgn_content):
                self.game_info = self.process_pgn(pgn_content)
                self.update_labels()
                self.fen_mode = False
                self.uci_pointer = 0
            else:
                QMessageBox.warning(self, "Invalid PGN", "The file does not contain valid PGN notation")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading file: {e}")


    def process_pgn(self, pgn_content):
        game_info = extract_game_info(pgn_content)
        self.parse_pgn(pgn_content)
        self.reset_to_start()
        return game_info


    def reset_to_start(self):
        self.current_move_index = -1
        self.update()


    def parse_pgn(self, pgn_content):
        self.chess_board.setup_starting_position()
        moves = extract_moves_list(pgn_content)
        positions, uci_moves = generate_positions_from_moves(moves, self.chess_board.pieces.copy())
        self.uci_moves = uci_moves
        print (self.uci_moves)
        self.evaluate_position(uci_moves)
        self.chess_board.positions_history = positions
        self.chess_board.is_opened = True
        self.chess_board.current_move_index = -1
        self.update()


    def update_labels(self):
        if hasattr(self, 'game_info') and isinstance(self.game_info, dict) and self.game_info:
            white_player = self.game_info.get('white_player', 'N/A')
            black_player = self.game_info.get('black_player', 'N/A')
            white_elo = self.game_info.get('white_elo', 'N/A')
            black_elo = self.game_info.get('black_elo', 'N/A')
            game_date = self.game_info.get('date', 'N/A')
            game_event = self.game_info.get('event', 'N/A')
            winner = self.game_info.get('winner', 'N/A')
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
        current_move = self.current_move_index + 1
        total_moves = self.get_move_count()
        if label_widget:
            label_widget.setText(f"({current_move}/{total_moves})")


    def evaluate_position(self, fen_or_uci):
        if self.fen_mode:
            worker = Worker(self.evaluate_fen, fen_or_uci)
        else:
            worker = Worker(self.evaluate_uci)
        worker.signals.result.connect(self.update_stockfish_ui)
        self.threadpool.start(worker)


    def evaluate_fen(self, fen, progress_callback):
        print("Running in thread:", threading.current_thread().name)
        self.stockfish.set_fen_position(fen)
        eval_info = self.stockfish.get_evaluation()
        best_move = self.stockfish.get_best_move()
        if eval_info["type"] == "cp":
            cp = eval_info["value"]
            evaluation_score = max(min(cp, 1000), -1000)
        elif eval_info["type"] == "mate":
            evaluation_score = 1000 if eval_info["value"] > 0 else -1000
        else:
            evaluation_score = 0
        bar_value = int((evaluation_score + 1000) / 2)
        white_pct = max(0, min(100, int(50 + (evaluation_score / 20))))
        black_pct = 100 - white_pct
        return {
            "best_move": best_move,
            "bar_value": bar_value,
            "white_pct": white_pct,
            "black_pct": black_pct,
        }


    def evaluate_uci(self, progress_callback):
        print("Running in thread:", threading.current_thread().name)
        print(self.uci_pointer)
        self.stockfish.set_position(self.uci_moves[:self.uci_pointer])
        eval_info = self.stockfish.get_evaluation()
        best_move = self.stockfish.get_best_move()
        if eval_info["type"] == "cp":
            cp = eval_info["value"]
            evaluation_score = max(min(cp, 1000), -1000)
        elif eval_info["type"] == "mate":
            evaluation_score = 1000 if eval_info["value"] > 0 else -1000
        else:
            evaluation_score = 0
        bar_value = int((evaluation_score + 1000) / 2)
        white_pct = max(0, min(100, int(50 + (evaluation_score / 20))))
        black_pct = 100 - white_pct
        return {
            "best_move": best_move,
            "bar_value": bar_value,
            "white_pct": white_pct,
            "black_pct": black_pct,
        }


    def update_stockfish_ui(self, result):
        self.best_move_label.setText(f"Best Move: {result['best_move']}")
        self.evaluation_bar.setValue(result["bar_value"])
        self.white_percentage.setText(f"White: {result['white_pct']}%")
        self.black_percentage.setText(f"Black: {result['black_pct']}%")


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(float)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs["progress_callback"] = self.signals.progress


    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


def unlock_board():
    error_message = QMessageBox()
    error_message.setWindowTitle("Error")
    error_message.setIcon(QMessageBox.Icon.Critical)
    error_message.setStandardButtons(QMessageBox.StandardButton.Ok)
    error_message.setText("This feature is still WIP! Sorry...")
    error_message.exec()


def coord_to_square(row, col):
    return chr(col + ord('a')) + str(8 - row)


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
    white_player_pattern = r'\[White\s+"([^"]+)"\]'
    white_elo_pattern = r'\[WhiteElo\s+"([^"]+)"\]'
    black_player_pattern = r'\[Black\s+"([^"]+)"\]'
    black_elo_pattern = r'\[BlackElo\s+"([^"]+)"\]'
    date_pattern = r'\[Date\s+"([^"]+)"\]'
    event_pattern = r'\[Event\s+"([^"]+)"\]'
    result_pattern = r'\[Result\s+"([^"]+)"\]'
    white_player_match = re.search(white_player_pattern, pgn_content)
    if white_player_match:
        full_name = white_player_match.group(1)
        name_parts = full_name.split()[:3]
        name_parts = [part.replace(',', '') for part in name_parts][::1]
        game_info['white_player'] = ' '.join(name_parts)
    white_elo_match = re.search(white_elo_pattern, pgn_content)
    if white_elo_match:
        game_info['white_elo'] = white_elo_match.group(1)
    black_player_match = re.search(black_player_pattern, pgn_content)
    if black_player_match:
        full_name = black_player_match.group(1)
        name_parts = full_name.split()[:3]
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


def _is_valid_fen(fen_string):
    if len(fen_string) < 28:
        return False
    if len(fen_string) > 106:
        return False
    components = fen_string.split()
    if len(components) != 6:
        return False
    piece_placement, active_color, castling_rights, en_passant, halfmove_clock, fullmove_number = components
    ranks = piece_placement.split('/')
    if len(ranks) != 8:
        return False
    for rank in ranks:
        squares_count = 0
        for char in rank:
            if char.isdigit():
                squares_count += int(char)
            elif char.upper() in 'KQRBNP':
                squares_count += 1
            else:
                return False
        if squares_count != 8:
            return False
    if active_color not in ['w', 'b']:
        return False
    if not all(c in 'KQkq-' for c in castling_rights):
        return False
    if castling_rights != '-':
        if len(set(castling_rights)) != len(castling_rights):
            return False
        valid_order = ''
        for c in 'KQkq':
            if c in castling_rights:
                valid_order += c
        if castling_rights != valid_order:
            return False
    if en_passant != '-':
        if len(en_passant) != 2:
            return False
        if en_passant[0] not in 'abcdefgh' or en_passant[1] not in '36':
            return False
    return True


def is_valid_pgn(content):
    if not re.search(r'\[.+]', content):
        return False
    if not re.search(r'\d+\.', content):
        return False
    return True


def extract_moves_from_pgn(pgn_content):
    if '\n\n' in pgn_content:
        return pgn_content.split('\n\n', 1)[1]
    return pgn_content


def extract_moves_list(moves_text):
    moves_text = re.sub(r'\{[^}]*}', '', moves_text)
    moves_text = re.sub(r'\([^)]*\)', '', moves_text)
    moves_text = re.sub(r'1-0|0-1|1/2-1/2|\*', '', moves_text)
    move_pattern = r'(?:\d+\.+\s*)?([KQRBNP]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?|O-O(?:-O)?)'
    moves = re.findall(move_pattern, moves_text)
    print ([move for move in moves if move.strip()])
    return [move for move in moves if move.strip()]


def apply_move_to_position(move, position, player):
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
    move_data = parse_move_notation(move)
    source_square = find_source_square(move_data, new_position, player)
    if source_square:
        target_square = (move_data['target_row'], move_data['target_col'])
        if target_square in new_position:
            del new_position[target_square]
        piece = new_position.pop(source_square)
        if move_data['promotion']:
            piece = player + move_data['promotion']
        new_position[target_square] = piece
    return new_position


def parse_move_notation(move):
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


def find_source_square(move_data, position, player):
    target_row = move_data['target_row']
    target_col = move_data['target_col']
    piece = move_data['piece']
    piece_code = player + piece
    source_file = move_data['source_file']
    source_rank = move_data['source_rank']
    is_capture = move_data['is_capture']
    if piece == 'P':
        pawn_source = find_pawn_source(move_data, position, player)
        if pawn_source:
            return pawn_source
    candidates = []
    for (row, col), board_piece in position.items():
        if board_piece != piece_code:
            continue
        if source_file is not None and col != source_file:
            continue
        if source_rank is not None and row != source_rank:
            continue
        if can_piece_move_to_target(piece, row, col, target_row,
                                    target_col, position, player,
                                    is_capture):
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
                             position, player, is_capture):
    if piece_type == 'P':
        return can_pawn_move_to_target(row, col, target_row,
                                       target_col, player, is_capture)
    elif piece_type == 'N':
        return ((abs(row - target_row) == 2 and abs(col - target_col) == 1) or
                (abs(row - target_row) == 1 and abs(col - target_col) == 2))
    elif piece_type == 'B':
        return (abs(row - target_row) == abs(col - target_col) and
                is_diagonal_path_clear(position, row, col,
                                       target_row, target_col))
    elif piece_type == 'R':
        return ((row == target_row or col == target_col) and
                is_straight_path_clear(position, row, col,
                                       target_row, target_col))
    elif piece_type == 'Q':
        if row == target_row or col == target_col:
            return is_straight_path_clear(position, row, col,
                                          target_row, target_col)
        elif abs(row - target_row) == abs(col - target_col):
            return is_diagonal_path_clear(position, row, col,
                                          target_row, target_col)
        return False
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
    move_squares = []
    for i, move in enumerate(moves):
        try:
            if move in ["O-O", "O-O-O"]:
                if current_player == 'w':
                    move_squares.append("e1g1" if move == "O-O" else "e1c1")
                else:
                    move_squares.append("e8g8" if move == "O-O" else "e8c8")
            else:
                move_data = parse_move_notation(move)
                source_square = find_source_square(move_data, current_position, current_player)
                if source_square:
                    target_square = (move_data['target_row'], move_data['target_col'])
                    source_str = chr(source_square[1] + ord('a')) + str(8 - source_square[0])
                    target_str = chr(target_square[1] + ord('a')) + str(8 - target_square[0])
                    move_squares.append(source_str + target_str)
            current_position = apply_move_to_position(move, current_position, current_player)
            positions_history.append(current_position.copy())
            current_player = 'b' if current_player == 'w' else 'w'
        except Exception as e:
            print(f"Error at move {i + 1} ({move}): {e}")
            break
    return positions_history, move_squares


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Windows')
    QFontDatabase.addApplicationFont('../resources/Avenir_Light.ttf')
    with open("./styles.qss", "r") as f:
        style = f.read()
        app.setStyleSheet(style)
    window = MainWindow()
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