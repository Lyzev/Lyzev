import os
import sys
import chess
import importlib.util

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("chess_controller",
                                              os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                           "chess-controller.py"))
chess_controller = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chess_controller)


def test_load_stats_default(tmp_path, monkeypatch):
  monkeypatch.setattr(chess_controller, "DATA_DIR", str(tmp_path))
  stats = chess_controller.load_stats()
  assert stats["games_played"] == 0
  assert stats["white_wins"] == 0
  assert stats["black_wins"] == 0
  assert stats["draws"] == 0
  assert stats["total_moves"] == 0
  assert stats["current_game_moves"] == 0


def test_save_and_load_stats(tmp_path, monkeypatch):
  monkeypatch.setattr(chess_controller, "DATA_DIR", str(tmp_path))
  stats = {
    "games_played": 1,
    "white_wins": 1,
    "black_wins": 0,
    "draws": 0,
    "total_moves": 10,
    "current_game_moves": 10
  }
  chess_controller.save_stats(stats)
  loaded = chess_controller.load_stats()
  assert loaded == stats


def test_load_game_new(tmp_path, monkeypatch):
  monkeypatch.setattr(chess_controller, "DATA_DIR", str(tmp_path))
  game = chess_controller.load_game("test_board.pgn")
  board = game.end().board()
  assert board.fen() == chess.Board().fen()
