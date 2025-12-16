from datetime import date
import chess.pgn as pgn
import chess
import os


class Core:
    def __init__(self, FEN=None):
        if FEN:
            self.board = chess.Board(FEN)
        else:
            self.board = chess.Board()
        self.game = pgn.Game.from_board(self.board)

    def export_fen(self):
        return self.board.fen()

    def get_legal(self):
        return [move.uci() for move in self.board.legal_moves]

    def check_legal(self, move):
        return self.board.is_legal(chess.Move.from_uci(move))
    
    def save_pgn(self):
        white = self.game.headers.get("White")
        black = self.game.headers.get("Black")
        today = date.today().strftime("%Y.%m.%d")

        if white == "?":
            sanitized_white = "White"
        else:
            sanitized_white = white.replace(" ", "_")
        if black == "?":
            sanitized_black = "Black"
        else:
            sanitized_black = black.replace(" ", "_")

        base_name = f"{today}_{sanitized_white}_vs_{sanitized_black}"
        filename = f"{base_name}.pgn"
        path = f"../pgns/{filename}"

        counter = 1
        while os.path.exists(path):
            filename = f"{base_name}_{counter}.pgn"
            path = f"../pgns/{filename}"
            counter += 1

        try:
            with open(path, "x", encoding="utf-8") as f:
                exporter = pgn.FileExporter(f)
                self.game.accept(exporter)
        except FileExistsError:
            raise FileExistsError

        print(f"Game Saved: {filename}")