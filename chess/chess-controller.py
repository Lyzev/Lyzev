import datetime
import chess
import os
import argparse
import json
from stockfish import Stockfish

script_dir = os.path.dirname(os.path.abspath(__file__))

stockfish = Stockfish(path=os.path.join(script_dir, "stockfish-ubuntu-x86-64-avx2"), depth=14, parameters={"Threads": 2, "Minimum Thinking Time": 3})

# ------------------ Stats functions ------------------

def load_stats():
    stats_file = os.path.join(script_dir, "stats.json")
    if os.path.exists(stats_file):
        with open(stats_file, "r") as f:
            stats = json.load(f)
    else:
        stats = {
            "games_played": 0,
            "white_wins": 0,
            "black_wins": 0,
            "draws": 0,
            "total_moves": 0,
            "current_game_moves": 0
        }
    return stats

def save_stats(stats):
    stats_file = os.path.join(script_dir, "stats.json")
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=4)

# ------------------ Board functions ------------------

def load_board(filename):
    filepath = os.path.join(script_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            board = chess.Board(file.read().strip())
    else:
        board = chess.Board()
    return board

def save_board(board, filename):
    filepath = os.path.join(script_dir, filename)
    with open(filepath, "w") as file:
        file.write(board.fen())

def board_to_markdown(board, legal_moves, stats):
    piece_svgs = {
        "P": "white/down/pawn.svg", "N": "white/down/horse.svg",
        "B": "white/down/bishop.svg",
        "R": "white/down/tower.svg", "Q": "white/down/queen.svg", "K": "white/down/king.svg",
        "p": "black/up/pawn.svg", "n": "black/up/horse.svg",
        "b": "black/up/bishop.svg",
        "r": "black/up/tower.svg", "q": "black/up/queen.svg", "k": "black/up/king.svg"
    }

    if board.turn:
        piece_svgs.update({
            "P": "white/up/pawn.svg", "N": "white/up/horse.svg",
            "B": "white/up/bishop.svg",
            "R": "white/up/tower.svg", "Q": "white/up/queen.svg",
            "K": "white/up/king.svg",
            "p": "black/down/pawn.svg", "n": "black/down/horse.svg",
            "b": "black/down/bishop.svg",
            "r": "black/down/tower.svg", "q": "black/down/queen.svg", "k": "black/down/king.svg"
        })

    board_md = "|   | a | b | c | d | e | f | g | h |\n"
    board_md += "|---|---|---|---|---|---|---|---|---|\n"
    ranks = range(8, 0, -1) if board.turn else range(1, 9)
    for rank in ranks:
        board_md += f"| {rank} "
        for file in range(8):
            # Determine the target square based on file and rank
            target_square = chess.square(file, rank - 1)

            # Check for unique legal move that ends on this square
            unique_moves = [m for m in legal_moves if m.to_square == target_square]
            if len(unique_moves) == 1:
                move_to_issue = unique_moves[0].uci()
                hyperlink_start = f"["
                hyperlink_end = f"](https://github.com/Lyzev/Lyzev/issues/new?title=chess%7C{move_to_issue}&body=Click+%27Create%27+to+submit+this+move.)"
            else:
                hyperlink_start = ""
                hyperlink_end = ""

            # Determine the image symbol based on whether there's a piece on the square and the square color
            piece = board.piece_at(target_square)
            if piece is not None:
                if (file + rank) % 2 == 0:
                    symbol = f"![{piece.symbol()}](chess/assets/img/light/{piece_svgs[piece.symbol()]})"
                else:
                    symbol = f"![{piece.symbol()}](chess/assets/img/dark/{piece_svgs[piece.symbol()]})"
            else:
                if (file + rank) % 2 == 0:
                    symbol = "![Square](chess/assets/img/light/square.svg)"
                else:
                    symbol = "![Square](chess/assets/img/dark/square.svg)"

            # Wrap the symbol with the hyperlink if applicable
            symbol = f"{hyperlink_start}{symbol}{hyperlink_end}"
            board_md += f"| {symbol} "
        board_md += "|\n"
    # --- Game Status Section ---
    board_md += "\n## Game Status\n\n"
    board_md += f"- **Next to move:** `{'White' if board.turn else 'Black'}`\n"
    if board.move_stack:
        last_move = board.peek()
        board_md += f"- **Last move:** `{last_move}` at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    # --- Evaluation Section ---
    evaluation = stockfish.get_evaluation()
    win_percentage = 50
    if evaluation["type"] == "cp":
        win_percentage = 100 / (1 + 10 ** (-evaluation["value"] / 400))
    elif evaluation["type"] == "mate":
        win_percentage = 100 if evaluation["value"] > 0 else 0
    win_percentage = max(0, min(100, win_percentage))
    white_percentage = win_percentage
    black_percentage = 100 - win_percentage

    bar_length = 20
    white_bar = int(bar_length * (white_percentage / 100))
    black_bar = bar_length - white_bar
    ascii_bar = f"{'█' * white_bar}{'░' * black_bar}\n\n`{white_percentage:.1f}% White` / `{black_percentage:.1f}% Black`"

    board_md += "\n## Evaluation (Stockfish)\n\n"
    board_md += f"{ascii_bar}\n"
    if evaluation["type"] == "mate":
        board_md += f"- **Mate in:** `{abs(evaluation['value'])}`\n"


    # --- Legal Moves Section ---
    board_md += "\n## Legal Moves\n\n"
    board_md += "| **Piece** | **Move** |\n"
    board_md += "|:---------:|:--------:|\n"

    moves_dict = {}
    for move in legal_moves:
        piece_position = chess.square_name(move.from_square)
        moves_dict.setdefault(piece_position, []).append(move.uci())

    for piece_position, moves in moves_dict.items():
        moves_links = [
            f"[`{move}`](https://github.com/Lyzev/Lyzev/issues/new?title=chess%7C{move}&body=Click+%27Create%27+to+submit+this+move.)"
            for move in moves
        ]
        board_md += f"| `{piece_position}` | {', '.join(moves_links)} |\n"

    # ------------------ Stats Section ------------------
    board_md += "\n## Game Statistics\n\n"
    board_md += f"- **Moves in current game:** {stats['current_game_moves']}\n"
    board_md += f"- **Total moves across all games:** {stats['total_moves']}\n"
    board_md += f"- **Games played:** {stats['games_played']}\n"
    board_md += f"- **White wins:** {stats['white_wins']}\n"
    board_md += f"- **Black wins:** {stats['black_wins']}\n"
    board_md += f"- **Draws:** {stats['draws']}\n\n"

    total_decisive = stats['white_wins'] + stats['black_wins']
    if total_decisive > 0:
        white_rate = stats['white_wins'] / total_decisive * 100
        black_rate = 100 - white_rate
    else:
        white_rate = 50
        black_rate = 50
    win_bar_length = 20
    white_win_bar = int(win_bar_length * white_rate / 100)
    black_win_bar = win_bar_length - white_win_bar
    win_rate_bar = f"{'█' * white_win_bar}{'░' * black_win_bar}\n\n"
    board_md += f"**Win Rate (Decisive games):**\n\n{win_rate_bar}White {white_rate:.1f}% / Black {black_rate:.1f}%\n"

    return board_md

def save_board_markdown(board, filename, legal_moves, stats):
    filepath = os.path.join(script_dir, filename)
    with open(filepath, "w") as file:
        file.write(board_to_markdown(board, legal_moves, stats))

def create_readme(template_path, board_path, output_path):
    template_filepath = os.path.join(script_dir, template_path)
    board_filepath = os.path.join(script_dir, board_path)
    output_filepath = os.path.join(script_dir, output_path)

    with open(template_filepath, "r") as template_file:
        template_content = template_file.read()

    with open(board_filepath, "r") as board_file:
        board_content = board_file.read()

    readme_content = template_content.replace("${CHESS}", board_content)

    with open(output_filepath, "w") as output_file:
        output_file.write(readme_content)

# ------------------ Main Function ------------------

def main():
    parser = argparse.ArgumentParser(description="Chess board controller.")
    parser.add_argument("move", type=str, help="The move to be made in UCI format")
    args = parser.parse_args()

    filename = "board.fen"
    board = load_board(filename)
    stats = load_stats()

    move = args.move

    try:
        chess_move = chess.Move.from_uci(move)
        legal_moves = list(board.legal_moves)
        if chess_move in legal_moves:
            board.push(chess_move)
            # Update move counters for every legal move made
            stats["total_moves"] += 1
            stats["current_game_moves"] += 1

            if board.is_checkmate():
                # In checkmate, the winner is the side that did not have the turn
                winner = "Black" if board.turn else "White"
                print(f"Checkmate! The game is over. {winner} wins.")
                stats["games_played"] += 1
                if winner == "White":
                    stats["white_wins"] += 1
                else:
                    stats["black_wins"] += 1
                stats["current_game_moves"] = 0
                board = chess.Board()
            elif board.is_stalemate():
                print("Stalemate! The game is a draw.")
                stats["games_played"] += 1
                stats["draws"] += 1
                stats["current_game_moves"] = 0
                board = chess.Board()
            elif board.is_insufficient_material():
                print("Draw due to insufficient material.")
                stats["games_played"] += 1
                stats["draws"] += 1
                stats["current_game_moves"] = 0
                board = chess.Board()

            save_board(board, filename)
            legal_moves = list(board.legal_moves)
            stockfish.set_fen_position(board.fen())
            save_board_markdown(board, "board.md", legal_moves, stats)
            create_readme("../README-TEMPLATE.md", "board.md", "../README.md")
            save_stats(stats)
            print("Move made successfully.")
        else:
            print("Invalid move.")
    except ValueError:
        print("Invalid move format.")

if __name__ == "__main__":
    main()
