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
