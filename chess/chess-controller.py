import datetime
import chess
import chess.pgn
import os
import argparse
import json
from stockfish import Stockfish

script_dir = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(script_dir, "data")


def get_stockfish():
  stockfish_path = os.environ.get("STOCKFISH_PATH", "stockfish")
  return Stockfish(path=stockfish_path, depth=2)


def load_stats():
  stats_file = os.path.join(DATA_DIR, "stats.json")
  if os.path.exists(stats_file):
    try:
      with open(stats_file, "r") as f:
        stats = json.load(f)
    except json.JSONDecodeError:
      print("Warning: stats.json is corrupted. Loading default stats.")
      stats = None
  else:
    stats = None
  if stats is None:
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
  stats_file = os.path.join(DATA_DIR, "stats.json")
  try:
    with open(stats_file, "w") as f:
      json.dump(stats, f, indent=4)
  except IOError as e:
    print(f"Error saving stats: {e}")


def load_game(filename):
  filepath = os.path.join(DATA_DIR, filename)
  if os.path.exists(filepath):
    try:
      with open(filepath, "r") as file:
        game = chess.pgn.read_game(file)
        if game is None:
          game = chess.pgn.Game()
    except IOError as e:
      print(f"Error loading game: {e}")
      game = chess.pgn.Game()
  else:
    game = chess.pgn.Game()
  return game


def save_game(game, filename):
  filepath = os.path.join(DATA_DIR, filename)
  try:
    with open(filepath, "w") as file:
      file.write(str(game))
  except IOError as e:
    print(f"Error saving game: {e}")


def board_to_markdown(board, legal_moves, stats):
  piece_svgs = {
    "P": "white/pawn.svg", "N": "white/horse.svg",
    "B": "white/bishop.svg",
    "R": "white/tower.svg", "Q": "white/queen.svg", "K": "white/king.svg",
    "p": "black/pawn.svg", "n": "black/horse.svg",
    "b": "black/bishop.svg",
    "r": "black/tower.svg", "q": "black/queen.svg", "k": "black/king.svg"
  }
  board_md = "|   | a | b | c | d | e | f | g | h |\n"
  board_md += "|---|---|---|---|---|---|---|---|---|\n"
  ranks = range(8, 0, -1) if board.turn else range(1, 9)
  for rank in ranks:
    board_md += f"| {rank} "
    for file in range(8):
      target_square = chess.square(file, rank - 1)
      unique_moves = [m for m in legal_moves if m.to_square == target_square]
      if len(unique_moves) == 1:
        move_to_issue = unique_moves[0].uci()
        hyperlink_start = f"["
        hyperlink_end = f"](https://github.com/Lyzev/Lyzev/issues/new?title=chess%7C{move_to_issue}&body=Click+%27Create%27+to+submit+this+move.)"
      else:
        hyperlink_start = ""
        hyperlink_end = ""
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
      symbol = f"{hyperlink_start}{symbol}{hyperlink_end}"
      board_md += f"| {symbol} "
    board_md += "|\n"
  board_md += "\n## Game Status\n\n"
  board_md += f"- **Next to move:** `{'White' if board.turn else 'Black'}`\n"
  if board.move_stack:
    last_move = board.peek()
    board_md += f"- **Last move:** `{last_move}` at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
  stockfish = get_stockfish()
  stockfish.set_fen_position(board.fen())
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


def main():
  parser = argparse.ArgumentParser(description="Chess board controller.")
  parser.add_argument("move", type=str, help="The move to be made in UCI format")
  args = parser.parse_args()
  filename = "board.pgn"
  game = load_game(filename)
  board = game.end().board()
  stats = load_stats()
  move = args.move
  try:
    chess_move = chess.Move.from_uci(move)
    legal_moves = list(board.legal_moves)
    if chess_move in legal_moves:
      game.end().add_variation(chess_move)
      board = game.end().board()
      stats["total_moves"] += 1
      stats["current_game_moves"] += 1
      is_game_over = False
      result = "*"
      if board.is_checkmate():
        winner = "Black" if board.turn else "White"
        print(f"Checkmate! The game is over. {winner} wins.")
        stats["games_played"] += 1
        if winner == "White":
          stats["white_wins"] += 1
          result = "1-0"
        else:
          stats["black_wins"] += 1
          result = "0-1"
        is_game_over = True
      elif board.is_stalemate():
        print("Stalemate! The game is a draw.")
        stats["games_played"] += 1
        stats["draws"] += 1
        result = "1/2-1/2"
        is_game_over = True
      elif board.is_insufficient_material():
        print("Draw due to insufficient material.")
        stats["games_played"] += 1
        stats["draws"] += 1
        result = "1/2-1/2"
        is_game_over = True
      if is_game_over:
        game.headers["Result"] = result
        stats["current_game_moves"] = 0
        history_dir = os.path.join(DATA_DIR, "history")
        os.makedirs(history_dir, exist_ok=True)
        history_filename = os.path.join(history_dir, f"game_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pgn")
        with open(history_filename, "w") as hf:
          hf.write(str(game))
        game = chess.pgn.Game()
        board = game.end().board()
      save_game(game, filename)
      legal_moves = list(board.legal_moves)
      save_board_markdown(board, "board.md", legal_moves, stats)
      readme_template_path = os.path.join(script_dir, "..", "README-TEMPLATE.md")
      readme_path = os.path.join(script_dir, "..", "README.md")
      create_readme(readme_template_path, "board.md", readme_path)
      save_stats(stats)
      print("Move made successfully.")
    else:
      print("Invalid move.")
      import sys
      sys.exit(1)
  except ValueError:
    print("Invalid move format.")
    import sys
    sys.exit(1)


if __name__ == "__main__":
  main()
