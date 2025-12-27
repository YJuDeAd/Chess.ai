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

    def start_match(self):
        print(f"Match Started: {self.white} (White) vs {self.black} (Black)")

        while not self.game.game_over:
            self.display_board()
            success = self.run_tick()
            if not success:
                print("Invalid Move, Try again.")

        self.game_end()

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
        
    def display_board(self):
        status = self.get_status()
    
        print("\n" + "="*20)
        print(f"TURN: {status['Turn']}")
        print(self.game.board)
        
        if status['Check']:
            print("!!! YOUR KING IS IN CHECK !!!")

    def game_end(self):
        print("\nGAME OVER")
        print(f"Result: {self.game.game_result()}")
        self.game.save_pgn()
        
    def get_status(self):
        return {
            "Turn": self.game.get_turn(),
            "Fen": self.game.export_fen(),
            "Check": self.game.is_in_check(),
            "Game Over": self.game.game_over
        }