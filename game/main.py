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
        self.game_node = self.game

    def export_fen(self):
        return self.board.fen()

    def get_legal(self):
        return [move.uci() for move in self.board.legal_moves]

    def check_legal(self, move):
        return self.board.is_legal(chess.Move.from_uci(move))
    
    def make_move(self, move_uci):
        if self.check_legal(move_uci):
            move = chess.Move.from_uci(move_uci)
            self.game_node = self.game_node.add_main_variation(move)
            self.board.push(move)
            status = self.check_status()
            if status:
                print(f"Game Over: {status}")
                self.game.headers["Result"] = self.board.result()
        else:
            raise ValueError(f"Illegal move: {move_uci}")

    def get_turn(self):
        if self.board.turn == chess.WHITE:
            return "White" 
        else:
            return "Black"

    def is_in_check(self):
        return self.board.is_check()

    def check_status(self):
        if self.board.is_checkmate():
            return "Checkmate"
        if self.board.is_stalemate():
            return "Stalemate"
        if self.board.is_insufficient_material():
            return "Insufficient Material"
        if self.board.is_fifty_moves():
            return "50-move Rule"
        if self.board.is_fivefold_repetition():
            return "Fivefold Repetition"
        return None

    def save_pgn(self):
        white = self.game.headers.get("White")
        black = self.game.headers.get("Black")
        today = date.today().strftime("%Y.%m.%d")
        self.game.headers["Date"] = today

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