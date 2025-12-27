from core import Core
import random


class HumanPlayer:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def get_move(self, fen):
        return input(f"[{self.name}] Enter move (e.g., a2a4): ")


class Orchestrator:
    def __init__(self):
        self.game = Core()
        self.white = None
        self.black = None
        self.player_map = {}

    def assign_players(self, p1, p2):
        players = [p1, p2]
        random.shuffle(players)

        self.white, self.black = players

        self.game.game.headers["White"] = self.white
        self.game.game.headers["Black"] = self.black

        self.player_map = {
            "White": self.white,
            "Black": self.black
        }

    def run_tick(self):
        if self.game.game_over:
            return "Game Over"

        current_turn = self.game.get_turn()
        current_player = self.player_map[current_turn]

        move = current_player.get_move(self.game.export_fen())
        
        return self.play_move(move)
    
    def play_move(self, user_move: str):
        try:
            self.game.make_move(user_move)
            return True
        except ValueError as e:
            print(e)
            return False
        
    def get_status(self):
        return {
            "Turn": self.game.get_turn(),
            "Fen": self.game.export_fen(),
            "Check": self.game.is_in_check(),
            "Game Over": self.game.game_over
        }