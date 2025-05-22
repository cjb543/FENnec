from pathlib import Path
from PyQt6.QtCore import (Qt, QRectF)
from PyQt6.QtGui import (QPainter, QColor, QPen, QPainterPath, QMouseEvent)
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (QWidget, QLabel)
from themes import ClassicTheme, RetroTheme, CatpuccinTheme, GruvboxTheme, GrayscaleTheme, LetteringTheme, MinimalistTheme

# Chess square constants
LIGHT_SQUARE_COLOR = QColor(240, 217, 181)
DARK_SQUARE_COLOR = QColor(181, 136, 99)

class ChessBoard(QWidget):
    SQUARE_SIZE_DEFAULT = 38
    PIECE_SIZE_RATIO = 0.9
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = ClassicTheme()
        self.svg_renderers = {}
        self.square_size = self.SQUARE_SIZE_DEFAULT
        self.board_size = self.square_size * 8
        self.current_move_index = -1
        self.is_opened = False
        self.positions_history = []
        self.pieces = {}
        self.current_position = {}
        self.piece_images = {}
        self.board_unlocked = False
        self.selected_square = None
        self._initialize_board()


    def _initialize_board(self):
        """Initialize board properties and state."""
        self.setMinimumSize(320, 320)
        self.setup_starting_position()
        self._load_piece_images()


    def apply_theme(self, theme_cls):
        self.current_theme = theme_cls()
        self.update()


    def _draw_board_squares(self, painter, start_x, start_y):
        self.current_theme.square_size = self.square_size
        self.current_theme._draw-_board_squares(painter, start_x, start_y)


    def _draw_pieces(self, painter, start_x, start_y):
        self.current_theme.square_size = self.square_size
        self.current_theme._draw_pieces(painter, start_x, start_y)


    def mousePressEvent(self, event: QMouseEvent):
        """Handles user mouse input on the chess board."""
        pass


    def setup_starting_position(self):
        """Sets up the starting position for a new game."""
        self.pieces = {}
        for col in range(8):
            self.pieces[(1, col)] = "bP"
            self.pieces[(6, col)] = "wP"
        back_row_pieces = ["R", "N", "B", "Q", "K", "B", "N", "R"]
        for col in range(8):
            self.pieces[(0, col)] = "b" + back_row_pieces[col]
            self.pieces[(7, col)] = "w" + back_row_pieces[col]
        self.positions_history = []
        self.current_move_index = -1


    def _load_piece_images(self):
        """Load SVG renderers for chess piece images."""
        piece_types = ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]
        assets_dir = Path(__file__).parent.parent / "assets"

        for piece_type in piece_types:
            path = assets_dir / f"{piece_type}.svg"
            if path.exists():
                self.svg_renderers[piece_type] = QSvgRenderer(str(path))
            else:
                print(f"Warning: Missing SVG for {piece_type} at {path}")


    def get_current_position(self):
        """Get the current position of the pieces."""
        if self.current_move_index == -1:
            return self.pieces
        elif 0 <= self.current_move_index < len(self.positions_history):
            return self.positions_history[self.current_move_index]
        return self.pieces


    def next_move(self):
        """Moves the game forward 1 move"""
        if self.current_move_index < len(self.positions_history) - 1:
            self.current_move_index += 1
            self.update()
            return True
        return False


    def previous_move(self):
        """Moves the game back 1 move"""
        if self.current_move_index >= 0:
            self.current_move_index -= 1
            self.update()
            return True
        return False


    def last_move(self):
        """Moves the game to the last move"""
        self.current_move_index = len(self.positions_history) - 1
        self.update()
        return True


    def reset_to_start(self):
        """Resets the game back to the first move"""
        self.current_move_index = -1
        self.update()


    def get_move_count(self):
        """Getter for current # of moves"""
        return len(self.positions_history)


    def process_pgn(self, pgn_content):
        """Fills the game_info list with PGN content"""
        game_info = extract_game_info(pgn_content)
        self.parse_pgn(pgn_content)
        self.reset_to_start()
        return game_info


    def parse_pgn(self,pgn_content):
        """Parses the supplied PGN file"""
        self.setup_starting_position()
        moves_text = extract_moves_from_pgn(pgn_content)
        moves = extract_moves_list(moves_text)
        positions = generate_positions_from_moves(moves, self.pieces.copy())
        self.positions_history = positions
        self.is_opened = True
        self.current_move_index = -1
        self.update()


    def update_move_count_label(self, label_widget: QLabel):
        """Update the turn label to show the current move count and total moves."""
        current_move = self.current_move_index + 1
        total_moves = self.get_move_count()
        if label_widget:
            label_widget.setText(f"({current_move}/{total_moves})")


    def unlock_board(self):
        """Allows the user to edit the chess board"""
        self.board_unlocked = True
        self.selected_square = None
    pass
