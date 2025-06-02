from pathlib import Path

from PyQt6.QtCore import (Qt, QRectF)
from PyQt6.QtGui import (QPainter, QColor, QPainterPath)
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (QWidget, QLabel)

SQUARE_SIZE_DEFAULT = 38

class ChessBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = ThemeBase()
        self.svg_renderers = {}
        self.square_size = SQUARE_SIZE_DEFAULT
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


    def paintEvent(self, event):
        painter = QPainter(self)
        self.square_size = min(self.width(), self.height()) // 8
        self.board_size = self.square_size * 8
        start_x = (self.width() - self.board_size) // 2
        start_y = (self.height() - self.board_size) // 2

        path = QPainterPath()
        radius = self.square_size * 0.2
        rect = QRectF(start_x, start_y, self.board_size, self.board_size)
        path.addRoundedRect(rect, radius, radius)
        painter.setClipPath(path)

        self._draw_board_squares(painter, start_x, start_y)
        self._draw_pieces(painter, start_x, start_y)
        painter.end()


    def apply_theme(self, theme_cls):
        self.current_theme = theme_cls()
        self.update()


    def _draw_board_squares(self, painter, start_x, start_y):
        self.current_theme.square_size = self.square_size
        self.current_theme._draw_board_squares(painter, start_x, start_y)


    def _draw_pieces(self, painter, start_x, start_y):
        self.current_theme.square_size = self.square_size
        self.current_theme._draw_pieces(painter, start_x, start_y, self)


    def setup_starting_position(self):
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


    def parse_pgn(self, pgn_content):
        """Parses the supplied PGN file"""
        self.setup_starting_position()
        moves = extract_moves_list(pgn_content)
        positions = generate_positions_from_moves(moves, self.pieces.copy())
        self.positions_history = positions
        self.is_opened = True
        self.current_move_index = -1
        self.update()


    def _load_piece_images(self):
        """Load SVG renderers for chess piece images."""
        piece_types = ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]
        assets_dir = Path(__file__).parent.parent / "assets" / "classic-theme"
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


    def update_move_count_label(self, label_widget: QLabel):
        """Update the turn label to show the current move count and total moves."""
        current_move = self.current_move_index + 1
        total_moves = self.get_move_count()
        if label_widget:
            label_widget.setText(f"({current_move}/{total_moves})")


class ThemeBase:
    def _draw_board_squares(self, painter, start_x, start_y):
        for row in range(8):
            for col in range(8):
                x = start_x + col * self.square_size
                y = start_y + row * self.square_size
                color = QColor(240,217,181) if (row + col) % 2 == 0 else QColor(181,136,99)
                painter.fillRect(x, y, self.square_size, self.square_size, color)
    def _load_piece_images(self):
        piece_types = ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]
        self.assets_dir = Path(__file__).parent.parent / "assets" / "classic-theme"
        for piece_type in piece_types:
            path = self.assets_dir / f"{piece_type}.svg"
            if path.exists():
                board.svg_renderers[piece_type] = QSvgRenderer(str(path))
            else:
                print(f"Warning: Missing SVG for {piece_type} at {path}")
    def _draw_pieces(self, painter, start_x, start_y, board):
        self.display_position = board.get_current_position()
        for (row, col), piece_type in self.display_position.items():
            if piece_type in board.svg_renderers:
                self._render_piece(painter, row, col, piece_type, start_x, start_y, board)
    def _render_piece(self, painter, row, col, piece_type, start_x, start_y, board):
        x = start_x + col * self.square_size
        y = start_y + row * self.square_size
        renderer = board.svg_renderers[piece_type]
        size = self.square_size * 0.95
        offset = (self.square_size - size) / 2
        renderer.render(painter, QRectF(x + offset, y + offset, size, size))


class RetroTheme(ThemeBase):
    def __init__(self):
        super().__init__()
        self.svg_renderers = {}
        self.square_size = SQUARE_SIZE_DEFAULT
        self._load_piece_images()
    def _draw_board_squares(self, painter, start_x, start_y):
        for row in range(8):
            for col in range(8):
                x = start_x + col * self.square_size
                y = start_y + row * self.square_size
                color = QColor(78,231,0) if (row + col) % 2 == 0 else QColor(20,20,20)
                painter.fillRect(x, y, self.square_size, self.square_size, color)
    def _load_piece_images(self):
        self.svg_renderers = {}
        for color in ['w', 'b']:
            for piece in ['P', 'N', 'B', 'R', 'Q', 'K']:
                key = f"{color}{piece}"
                path = f"../assets/retro-theme/{key}.svg"
                self.svg_renderers[key] = QSvgRenderer(path)
    def _draw_pieces(self, painter, start_x, start_y, board):
        display_position = board.get_current_position()
        for (row, col), piece_type in display_position.items():
            if piece_type in self.svg_renderers:
                self._render_piece(painter, row, col, piece_type, start_x, start_y, board)
    def _render_piece(self, painter, row, col, piece_type, start_x, start_y, board):
        x = start_x + col * self.square_size
        y = start_y + row * self.square_size
        renderer = self.svg_renderers[piece_type]
        size = self.square_size * 0.95
        offset = (self.square_size - size) / 2
        renderer.render(painter, QRectF(x + offset, y + offset, size, size))


class CatpuccinTheme(ThemeBase):
    def __init__(self):
        super().__init__()
        self.svg_renderers = {}
        self.square_size = SQUARE_SIZE_DEFAULT
        self._load_piece_images()
    def _draw_board_squares(self, painter, start_x, start_y):
        for row in range(8):
            for col in range(8):
                x = start_x + col * self.square_size
                y = start_y + row * self.square_size
                color = QColor(138,66,69) if (row + col) % 2 == 0 else QColor(66,69,138)
                painter.fillRect(x, y, self.square_size, self.square_size, color)
    def _load_piece_images(self):
        self.svg_renderers = {}
        for color in ['w', 'b']:
            for piece in ['P', 'N', 'B', 'R', 'Q', 'K']:
                key = f"{color}{piece}"
                path = f"../assets/catpuccin-theme/{key}.svg"
                self.svg_renderers[key] = QSvgRenderer(path)
    def _draw_pieces(self, painter, start_x, start_y, board):
        display_position = board.get_current_position()
        for (row, col), piece_type in display_position.items():
            if piece_type in self.svg_renderers:
                self._render_piece(painter, row, col, piece_type, start_x, start_y, board)
    def _render_piece(self, painter, row, col, piece_type, start_x, start_y, board):
        x = start_x + col * self.square_size
        y = start_y + row * self.square_size
        renderer = self.svg_renderers[piece_type]
        size = self.square_size * 0.95
        offset = (self.square_size - size) / 2
        renderer.render(painter, QRectF(x + offset, y + offset, size, size))


class GruvboxTheme(ThemeBase):
    def __init__(self):
        super().__init__()
        self.svg_renderers = {}
        self.square_size = SQUARE_SIZE_DEFAULT
        self._load_piece_images()
    def _draw_board_squares(self, painter, start_x, start_y):
        for row in range(8):
            for col in range(8):
                x = start_x + col * self.square_size
                y = start_y + row * self.square_size
                color = QColor(249,243,185) if (row + col) % 2 == 0 else QColor(79,79,79)
                painter.fillRect(x, y, self.square_size, self.square_size, color)
    def _load_piece_images(self):
        self.svg_renderers = {}
        for color in ['w', 'b']:
            for piece in ['P', 'N', 'B', 'R', 'Q', 'K']:
                key = f"{color}{piece}"
                path = f"../assets/gruvbox-theme/{key}.svg"
                self.svg_renderers[key] = QSvgRenderer(path)
    def _draw_pieces(self, painter, start_x, start_y, board):
        display_position = board.get_current_position()
        for (row, col), piece_type in display_position.items():
            if piece_type in self.svg_renderers:
                self._render_piece(painter, row, col, piece_type, start_x, start_y, board)
    def _render_piece(self, painter, row, col, piece_type, start_x, start_y, board):
        x = start_x + col * self.square_size
        y = start_y + row * self.square_size
        renderer = self.svg_renderers[piece_type]
        size = self.square_size * 0.95
        offset = (self.square_size - size) / 2
        renderer.render(painter, QRectF(x + offset, y + offset, size, size))


class GrayscaleTheme(ThemeBase):
    def __init__(self):
        super().__init__()
        self.svg_renderers = {}
        self.square_size = SQUARE_SIZE_DEFAULT
        self._load_piece_images()
    def _draw_board_squares(self, painter, start_x, start_y):
        for row in range(8):
            for col in range(8):
                x = start_x + col * self.square_size
                y = start_y + row * self.square_size
                color = QColor(60,60,60) if (row + col) % 2 == 0 else QColor(230,230,230)
                painter.fillRect(x, y, self.square_size, self.square_size, color)
    def _load_piece_images(self):
        self.svg_renderers = {}
        for color in ['w', 'b']:
            for piece in ['P', 'N', 'B', 'R', 'Q', 'K']:
                key = f"{color}{piece}"
                path = f"../assets/grayscale-theme/{key}.svg"
                self.svg_renderers[key] = QSvgRenderer(path)
    def _draw_pieces(self, painter, start_x, start_y, board):
        display_position = board.get_current_position()
        for (row, col), piece_type in display_position.items():
            if piece_type in self.svg_renderers:
                self._render_piece(painter, row, col, piece_type, start_x, start_y, board)
    def _render_piece(self, painter, row, col, piece_type, start_x, start_y, board):
        x = start_x + col * self.square_size
        y = start_y + row * self.square_size
        renderer = self.svg_renderers[piece_type]
        size = self.square_size * 0.95
        offset = (self.square_size - size) / 2
        renderer.render(painter, QRectF(x + offset, y + offset, size, size))


class LetteringTheme(ThemeBase):
    def __init__(self):
        super().__init__()
        self.square_size = SQUARE_SIZE_DEFAULT
    def _draw_pieces(self, painter, start_x, start_y, board):
        display_position = board.get_current_position()
        for (row, col), piece_type in display_position.items():
            self._render_piece(painter, row, col, piece_type, start_x, start_y, board)
    def _render_piece(self, painter, row, col, piece_type, start_x, start_y, board):
        x = start_x + col * self.square_size
        y = start_y + row * self.square_size
        font = painter.font()
        font.setPointSize(int(self.square_size * 0.6))
        painter.setFont(font)

        if piece_type[0] == 'w':
            painter.setPen(QColor(255, 255, 255))
        else:
            painter.setPen(QColor(0, 0, 0))

        painter.drawText(
            QRectF(x, y, self.square_size, self.square_size),
            Qt.AlignmentFlag.AlignCenter,
            piece_type[1]
        )


class MinimalistTheme(ThemeBase):
    def __init__(self):
        super().__init__()
        self.svg_renderers = {}
        self.square_size = SQUARE_SIZE_DEFAULT
        self._load_piece_images()
    def _draw_board_squares(self, painter, start_x, start_y):
        for row in range(8):
            for col in range(8):
                x = start_x + col * self.square_size
                y = start_y + row * self.square_size
                color = QColor(60, 60, 60) if (row + col) % 2 == 0 else QColor(230, 230, 230)
                painter.fillRect(x, y, self.square_size, self.square_size, color)
    def _load_piece_images(self):
        self.svg_renderers = {}
        for color in ['w', 'b']:
            for piece in ['P', 'N', 'B', 'R', 'Q', 'K']:
                key = f"{color}{piece}"
                path = f"../assets/minimalist-theme/{key}.svg"
                self.svg_renderers[key] = QSvgRenderer(path)
    def _draw_pieces(self, painter, start_x, start_y, board):
        display_position = board.get_current_position()
        for (row, col), piece_type in display_position.items():
            if piece_type in self.svg_renderers:
                self._render_piece(painter, row, col, piece_type, start_x, start_y, board)
    def _render_piece(self, painter, row, col, piece_type, start_x, start_y, board):
        x = start_x + col * self.square_size
        y = start_y + row * self.square_size
        renderer = self.svg_renderers[piece_type]
        size = self.square_size * 0.95
        offset = (self.square_size - size) / 2
        renderer.render(painter, QRectF(x + offset, y + offset, size, size))
    def process_pgn(self, pgn_content):
        game_info = self.extract_game_info(pgn_content)
        self.parse_pgn(pgn_content)
        self.reset_to_start()
        return game_info