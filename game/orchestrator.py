from core import Core
import random
import time


class HumanPlayer:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def get_move(self, fen):
        return input(f"[{self.name}] Enter move (e.g., a2a4): ")


class Orchestrator:
    def __init__(self, max_retries=3, time_per_player=600):
        self.game = Core()
        self.white = None
        self.black = None
        self.player_map = {}
        self.max_retries = max_retries
        self.strikes = {"White": 0, "Black": 0}
        self.time_limit = time_per_player
        self.clock = {"White": float(time_per_player), "Black": float(time_per_player)}

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
        print(f"Time: {self.time_limit}s per player")

        while not self.game.game_over:
            self.display_board()
            result = self.run_tick()
            
            if result["status"] == "timeout":
                print(f"TIMEOUT {result["player"]} ran out of time")
                break
            
            if result["status"] == "invalid_move":
                print(f"{result['reason']} (Strike {result['strikes']}/{self.max_retries})")
                if result["forfeit"]:
                    print("MAX RETRIES EXCEEDED. Game Over.")
                    break

            elif result["status"] == "failed":
                print(f"CRITICAL FAILURE: {result['reason']}")
                break

        self.game_end()

    def run_tick(self):
        if self.game.game_over:
            return {"status": "finished", "message": "The game has already ended."}

        current_turn = self.game.get_turn()
        current_player = self.player_map[current_turn]

        start_time = time.time()

        try:
            move = current_player.get_move(self.game.export_fen())
        except Exception as e:
            return {"status": "player_error", "message": f"Player crashed: {e}", "forfeit": True}


        elapsed = time.time() - start_time
        self.clock[current_turn] -= elapsed

        if self.clock[current_turn] <= 0:
            return {"status": "timeout", "player": current_turn}

        move_result = self.play_move(move)

        if move_result["success"]:
            self.strikes[current_turn] = 0
            if self.game.game_over:
                return {"status": "game_over", "result": self.game.game_result()}
            return {"status": "success"}
        else:
            self.strikes[current_turn] += 1
            is_forfeit = self.strikes[current_turn] >= self.max_retries
            return {
                "status": "invalid_move", 
                "reason": move_result["reason"],
                "strikes": self.strikes[current_turn],
                "forfeit": is_forfeit
            }
    
    def play_move(self, user_move: str):
        try:
            self.game.make_move(user_move)
            return {"success": True}
        except ValueError as e:
            return {"success": False, "reason": str(e)}
        
    def display_board(self):
        status = self.get_status()
    
        print("\n" + "="*20)
        print(f"TURN: {status['Turn']} | WHITE: {self.clocks['White']:.1f}s | BLACK: {self.clocks['Black']:.1f}s")
        print(self.game.board)
        
        if status['Check']:
            print("!!! YOUR KING IS IN CHECK !!!")

    def game_end(self):
        print("\n" + "═"*20)
        print("GAME OVER")

        if self.clocks["White"] <= 0:
            print(f"Result: Black wins on time.")
            return
        if self.clocks["Black"] <= 0:
            print(f"Result: White wins on time.")
            return
        
        for side, count in self.strikes.items():
            if count >= self.max_retries:
                winner = "Black" if side == "White" else "White"
                print(f"Result: {winner} wins by forfeit ({side} exceeded max retries)")
                return

        print(f"Result: {self.game.game_result()}")
        self.game.save_pgn()
        
    def get_status(self):
        return {
            "Turn": self.game.get_turn(),
            "Fen": self.game.export_fen(),
            "Check": self.game.is_in_check(),
            "Game Over": self.game.game_over
        }