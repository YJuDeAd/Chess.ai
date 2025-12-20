from datetime import date
import chess.pgn as pgn
import chess
import os


class Core:
    def __init__(self, FEN=None):
        self.game_over = False
        self.draw_reason = None
        
        if FEN:
            self.board = chess.Board(FEN)
            self.fen_check()
        else:
            self.board = chess.Board()
        
        self.game = pgn.Game.from_board(self.board)
        self.game_node = self.game

    def export_fen(self):
        return self.board.fen()

    def fen_check(self):
        status = self.check_status()
        if status:
            print(f"Game Over: {status}")
            self.game_over = True
        return

    def get_legal(self):
        return [move.uci() for move in self.board.legal_moves]

    def check_legal(self, move):
        return self.board.is_legal(chess.Move.from_uci(move))
    
    def make_move(self, move_uci):
        if self.game_over:
            raise ValueError("Game is already over.")
        else:
            if self.check_legal(move_uci):
                move = chess.Move.from_uci(move_uci)
                self.game_node = self.game_node.add_main_variation(move)
                self.board.push(move)
                status = self.check_status()
                if status:
                    print(f"Game Over: {status}")
                    self.game_over = True
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
            self.draw_reason = "Stalemate"
            return self.draw_reason
        if self.board.is_insufficient_material():
            self.draw_reason = "Insufficient Material"
            return self.draw_reason
        if self.board.is_fifty_moves():
            self.draw_reason = "50-move Rule"
            return self.draw_reason
        if self.board.is_repetition():
            self.draw_reason = "Threefold Repetition"
            return self.draw_reason
        return None

    def game_result(self):
        result = self.board.result()
        if result == "1-0":
            return "White wins"
        elif result == "0-1":
            return "Black wins"
        elif result == "*":
            return "Game is still in progress"
        else:
            return f"Draw: {self.draw_reason}"

    def save_pgn(self):
        white = self.game.headers.get("White")
        black = self.game.headers.get("Black")
        today = date.today().strftime("%Y.%m.%d")
        self.game.headers["Date"] = today
        self.game.headers["Result"] = self.board.result()

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