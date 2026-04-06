import os
import chess.pgn
from stockfish import Stockfish

script_dir = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(script_dir, "data")


def main():
  stockfish_path = os.environ.get("STOCKFISH_PATH", "stockfish")
  stockfish = Stockfish(path=stockfish_path, depth=2)
  filepath = os.path.join(DATA_DIR, "board.pgn")
  if os.path.exists(filepath):
    try:
      with open(filepath, "r") as file:
        game = chess.pgn.read_game(file)
        if game is not None:
          board = game.end().board()
          stockfish.set_fen_position(board.fen())
          print(stockfish.get_top_moves(1)[0]["Move"])
          exit(0)
    except IOError as e:
      print(f"Error reading game: {e}")
  print("No board.pgn file found")
  exit(1)


if __name__ == "__main__":
  main()
