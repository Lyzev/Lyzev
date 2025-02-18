import datetime
import chess
import os
import argparse
from stockfish import Stockfish

script_dir = os.path.dirname(os.path.abspath(__file__))

stockfish = Stockfish(path=script_dir + "/stockfish-ubuntu-x86-64-avx2", depth=8, parameters={"Threads": 1, "Minimum Thinking Time": 1})
stockfish.set_elo_rating(800)

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

def board_to_markdown(board, legal_moves):
    piece_svgs = {
        "P": "chess/assets/img/white/down/pawn.svg", "N": "chess/assets/img/white/down/horse.svg",
        "B": "chess/assets/img/white/down/bishop.svg",
        "R": "chess/assets/img/white/down/tower.svg", "Q": "chess/assets/img/white/down/queen.svg", "K": "chess/assets/img/white/down/king.svg",
        "p": "chess/assets/img/black/up/pawn.svg", "n": "chess/assets/img/black/up/horse.svg",
        "b": "chess/assets/img/black/up/bishop.svg",
        "r": "chess/assets/img/black/up/tower.svg", "q": "chess/assets/img/black/up/queen.svg", "k": "chess/assets/img/black/up/king.svg"
    }

    if board.turn:
        piece_svgs.update({
            "P": "chess/assets/img/white/up/pawn.svg", "N": "chess/assets/img/white/up/horse.svg",
            "B": "chess/assets/img/white/up/bishop.svg",
            "R": "chess/assets/img/white/up/tower.svg", "Q": "chess/assets/img/white/up/queen.svg",
            "K": "chess/assets/img/white/up/king.svg",
            "p": "chess/assets/img/black/down/pawn.svg", "n": "chess/assets/img/black/down/horse.svg",
            "b": "chess/assets/img/black/down/bishop.svg",
            "r": "chess/assets/img/black/down/tower.svg", "q": "chess/assets/img/black/down/queen.svg",
            "k": "chess/assets/img/black/down/king.svg"
        })

    board_md = "|   | a | b | c | d | e | f | g | h |\n"
    board_md += "|---|---|---|---|---|---|---|---|---|\n"
    ranks = range(8, 0, -1) if board.turn else range(1, 9)
    for rank in ranks:
        board_md += f"| {rank} "
        for file in range(8):
            piece = board.piece_at(chess.square(file, rank - 1))
            symbol = " "
            if piece is not None:
                symbol = f"![{piece.symbol()}]({piece_svgs[piece.symbol()]})"
            else:
                symbol = "![Empty](chess/assets/img/empty.svg)"
            board_md += f"| {symbol} "
        board_md += "|\n"
    board_md += f"\n**Next move:** {"White" if board.turn else "Black"}\n"

    if len(board.move_stack) > 0:
        last_move = board.peek()
        board_md += f"\n**Last move:** {last_move} - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    wdl = stockfish.get_wdl_stats()
    win_percentage = (wdl[0] + wdl[1] / 2) / sum(wdl) * 100
    if not board.turn:
        win_percentage = 100 - win_percentage
    win_percentage = max(0, min(100, win_percentage))
    white_percentage = win_percentage
    black_percentage = 100 - win_percentage

    bar_length = 20
    white_bar = int(bar_length * (white_percentage / 100))
    black_bar = bar_length - white_bar
    ascii_bar = f"{"█" * white_bar}{"░" * black_bar}\n\n {white_percentage:.2f}% White / {black_percentage:.2f}% Black\n"

    board_md += f"\n**Win Percentage:**\n\n{ascii_bar}\n"

    board_md += "\n**Legal moves:**\n\n"
    board_md += "| Piece | Move |\n"
    board_md += "|-------|------|\n"

    moves_dict = {}
    for move in legal_moves:
        piece_position = chess.square_name(move.from_square)
        if piece_position not in moves_dict:
            moves_dict[piece_position] = []
        moves_dict[piece_position].append(move.uci())

    for piece_position, moves in moves_dict.items():
        moves_links = [
            f"[{move}](https://github.com/Lyzev/Lyzev/issues/new?title=chess%7C{move}&body=Click+%27Create%27+to+submit+this+move.)"
            for move in moves]
        board_md += f"| {piece_position} | {", ".join(moves_links)} |\n"

    return board_md


def save_board_markdown(board, filename, legal_moves):
    filepath = os.path.join(script_dir, filename)
    with open(filepath, "w") as file:
        file.write(board_to_markdown(board, legal_moves))

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

def main():
    parser = argparse.ArgumentParser(description="Chess board controller.")
    parser.add_argument("move", type=str, help="The move to be made in UCI format")
    args = parser.parse_args()

    filename = "board.fen"
    board = load_board(filename)

    move = args.move

    try:
        chess_move = chess.Move.from_uci(move)
        legal_moves = list(board.legal_moves)
        if chess_move in legal_moves:
            board.push(chess_move)
            if board.is_checkmate():
                print(f"Checkmate! The game is over. {"Black" if board.turn else "White"} wins.")
                board = chess.Board()
            elif board.is_stalemate():
                print("Stalemate! The game is a draw.")
                board = chess.Board()
            elif board.is_insufficient_material():
                print("Draw due to insufficient material.")
                board = chess.Board()
            save_board(board, filename)
            legal_moves = list(board.legal_moves)
            stockfish.set_fen_position(board.fen())
            save_board_markdown(board, "board.md", legal_moves)
            create_readme("../README-TEMPLATE.md", "board.md", "../README.md")
            print("Move made successfully.")
        else:
            print("Invalid move.")
    except ValueError:
        print("Invalid move format.")


if __name__ == "__main__":
    main()