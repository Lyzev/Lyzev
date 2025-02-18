import os
from stockfish import Stockfish
import random

script_dir = os.path.dirname(os.path.abspath(__file__))

stockfish = Stockfish(path=script_dir + "/stockfish-ubuntu-x86-64-avx2", depth=12, parameters={"Threads": 2, "Minimum Thinking Time": 3})
stockfish.set_elo_rating(1150)

if __name__ == "__main__":
    filepath = os.path.join(script_dir, "board.fen")
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            stockfish.set_fen_position(file.read().strip())
            print(random.choice(stockfish.get_top_moves(5))["Move"])
            exit(0)
    print("No board.fen file found")
    exit(1)