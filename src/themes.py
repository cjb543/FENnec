class ThemeBase:
    def _draw_board_squares(self, painter, start_x, start_y):
        """Draw the chessboard squares."""
        for row in range(8):
            for col in range(8):
                x = start_x + col * self.square_size
                y = start_y + row * self.square_size
                color = QColor(240,217,181) if (row + col) % 2 == 0 else QColor(181,136,99)
                painter.fillRect(x, y, self.square_size, self.square_size, color)


    def _draw_pieces(self, painter, start_x, start_y):
        """Draw the pieces on the board."""
        display_position = self.get_current_position()
        for (row, col), piece_type in display_position.items():
            if piece_type in self.svg_renderers:
                self._render_piece(painter, row, col, piece_type, start_x, start_y)


    def _render_piece(self, painter, row, col, piece_type, start_x, start_y):
        """Renders a single chess piece on the board."""
        x = start_x + col * self.square_size
        y = start_y + row * self.square_size
        renderer = self.svg_renderers[piece_type]
        size = self.square_size * 0.95
        offset = (self.square_size - size) / 2
        renderer.render(painter, QRectF(x + offset, y + offset, size, size))


class RetroTheme(ThemeBase):
    def _draw_board_squares(self, painter, start_x, start_y):
        """Draw the chessboard squares."""
        for row in range(8):
            for col in range(8):
                x = start_x + col * self.square_size
                y = start_y + row * self.square_size
                color = QColor(78,231,0) if (row + col) % 2 == 0 else QColor(20,20,20)
                painter.fillRect(x, y, self.square_size, self.square_size, color)


    def _draw_pieces(self, painter, start_x, start_y):
        """Draw the pieces on the board."""
        display_position = self.get_current_position()
        for (row, col), piece_type in display_position.items():
            if piece_type in self.svg_renderers:
                self._render_piece(painter, row, col, piece_type, start_x, start_y)


    def _render_piece(self, painter, row, col, piece_type, start_x, start_y):
        """Renders a single chess piece on the board."""
        x = start_x + col * self.square_size
        y = start_y + row * self.square_size
        renderer = self.svg_renderers[piece_type]
        size = self.square_size * 0.95
        offset = (self.square_size - size) / 2
        renderer.render(painter, QRectF(x + offset, y + offset, size, size))


class CatpuccinTheme(ThemeBase):
    def _draw_board_squares(self, painter, start_x, start_y):
        """Draw the chessboard squares."""
        for row in range(8):
            for col in range(8):
                x = start_x + col * self.square_size
                y = start_y + row * self.square_size
                color = QColor(138,66,69) if (row + col) % 2 == 0 else QColor(66,69,138)
                painter.fillRect(x, y, self.square_size, self.square_size, color)


    def _draw_pieces(self, painter, start_x, start_y):
        """Draw the pieces on the board."""
        display_position = self.get_current_position()
        for (row, col), piece_type in display_position.items():
            if piece_type in self.svg_renderers:
                self._render_piece(painter, row, col, piece_type, start_x, start_y)


    def _render_piece(self, painter, row, col, piece_type, start_x, start_y):
        """Renders a single chess piece on the board."""
        x = start_x + col * self.square_size
        y = start_y + row * self.square_size
        renderer = self.svg_renderers[piece_type]
        size = self.square_size * 0.95
        offset = (self.square_size - size) / 2
        renderer.render(painter, QRectF(x + offset, y + offset, size, size))


class GruvboxTheme(ThemeBase):
    def _draw_board_squares(self, painter, start_x, start_y):
        """Draw the chessboard squares."""
        for row in range(8):
            for col in range(8):
                x = start_x + col * self.square_size
                y = start_y + row * self.square_size
                color = QColor(240,217,181) if (row + col) % 2 == 0 else QColor(181,136,99)
                painter.fillRect(x, y, self.square_size, self.square_size, color)


    def _draw_pieces(self, painter, start_x, start_y):
        """Draw the pieces on the board."""
        display_position = self.get_current_position()
        for (row, col), piece_type in display_position.items():
            if piece_type in self.svg_renderers:
                self._render_piece(painter, row, col, piece_type, start_x, start_y)


    def _render_piece(self, painter, row, col, piece_type, start_x, start_y):
        """Renders a single chess piece on the board."""
        x = start_x + col * self.square_size
        y = start_y + row * self.square_size
        renderer = self.svg_renderers[piece_type]
        size = self.square_size * 0.95
        offset = (self.square_size - size) / 2
        renderer.render(painter, QRectF(x + offset, y + offset, size, size))


class GrayscaleTheme(ThemeBase):
    def _draw_board_squares(self, painter, start_x, start_y):
        """Draw the chessboard squares."""
        for row in range(8):
            for col in range(8):
                x = start_x + col * self.square_size
                y = start_y + row * self.square_size
                color = QColor(240,217,181) if (row + col) % 2 == 0 else QColor(181,136,99)
                painter.fillRect(x, y, self.square_size, self.square_size, color)


    def _draw_pieces(self, painter, start_x, start_y):
        """Draw the pieces on the board."""
        display_position = self.get_current_position()
        for (row, col), piece_type in display_position.items():
            if piece_type in self.svg_renderers:
                self._render_piece(painter, row, col, piece_type, start_x, start_y)


    def _render_piece(self, painter, row, col, piece_type, start_x, start_y):
        """Renders a single chess piece on the board."""
        x = start_x + col * self.square_size
        y = start_y + row * self.square_size
        renderer = self.svg_renderers[piece_type]
        size = self.square_size * 0.95
        offset = (self.square_size - size) / 2
        renderer.render(painter, QRectF(x + offset, y + offset, size, size))


class LetteringTheme(ThemeBase):
    def _draw_board_squares(self, painter, start_x, start_y):
        """Draw the chessboard squares."""
        for row in range(8):
            for col in range(8):
                x = start_x + col * self.square_size
                y = start_y + row * self.square_size
                color = QColor(240,217,181) if (row + col) % 2 == 0 else QColor(181,136,99)
                painter.fillRect(x, y, self.square_size, self.square_size, color)


    def _draw_pieces(self, painter, start_x, start_y):
        """Draw the pieces on the board."""
        display_position = self.get_current_position()
        for (row, col), piece_type in display_position.items():
            if piece_type in self.svg_renderers:
                self._render_piece(painter, row, col, piece_type, start_x, start_y)


    def _render_piece(self, painter, row, col, piece_type, start_x, start_y):
        """Renders a single chess piece on the board."""
        x = start_x + col * self.square_size
        y = start_y + row * self.square_size
        renderer = self.svg_renderers[piece_type]
        size = self.square_size * 0.95
        offset = (self.square_size - size) / 2
        renderer.render(painter, QRectF(x + offset, y + offset, size, size))


class MinimalistTheme(ThemeBase):
    def _draw_board_squares(self, painter, start_x, start_y):
        """Draw the chessboard squares."""
        for row in range(8):
            for col in range(8):
                x = start_x + col * self.square_size
                y = start_y + row * self.square_size
                color = QColor(240,217,181) if (row + col) % 2 == 0 else QColor(181,136,99)
                painter.fillRect(x, y, self.square_size, self.square_size, color)


    def _draw_pieces(self, painter, start_x, start_y):
        """Draw the pieces on the board."""
        display_position = self.get_current_position()
        for (row, col), piece_type in display_position.items():
            if piece_type in self.svg_renderers:
                self._render_piece(painter, row, col, piece_type, start_x, start_y)


    def _render_piece(self, painter, row, col, piece_type, start_x, start_y):
        """Renders a single chess piece on the board."""
        x = start_x + col * self.square_size
        y = start_y + row * self.square_size
        renderer = self.svg_renderers[piece_type]
        size = self.square_size * 0.95
        offset = (self.square_size - size) / 2
        renderer.render(painter, QRectF(x + offset, y + offset, size, size))
