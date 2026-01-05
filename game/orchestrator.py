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
    def __init__(self, config=None):
        self.game = Core()
        
        self.config = {
            "max_retries": 3,
            "time_per_player": 600,
            "verbosity": True,
            "auto_save": True
        }

        if config:
            self.config.update(config)
        
        self.white = None
        self.black = None
        self.player_map = {}
        
        self.strikes = {"White": 0, "Black": 0}
        self.clock = {
            "White": float(self.config["time_per_player"]), 
            "Black": float(self.config["time_per_player"])
        }
        
        self.move_history = []

    def assign_players(self, p1, p2):
        players = [p1, p2]
        random.shuffle(players)

        self.white, self.black = players

        self.game.game.headers["White"] = str(self.white)
        self.game.game.headers["Black"] = str(self.black)

        self.player_map = {
            "White": self.white,
            "Black": self.black
        }

    def log(self, message):
        if self.config["verbosity"]:
            print(message)

    def start_match(self):
        self.log(f"Match Started: {self.white} (White) vs {self.black} (Black)")
        self.log(f"Time Control: {self.config['time_per_player']}s | Retries: {self.config['max_retries']}")

        forced_winner = None

        while not self.game.game_over:
            self.display_board()
            result = self.run_tick()
            
            if result["status"] == "timeout":
                self.log(f"TIMEOUT {result['player']} ran out of time")
                forced_winner = "Black" if result['player'] == "White" else "White"
                break
            
            if result["status"] == "player_error":
                current_turn = self.game.get_turn()
                forced_winner = "Black" if result['player'] == "White" else "White"
                self.log(f"PLAYER CRASH: {result['message']}")
                self.log(f"CRITICAL PLAYER ERROR: {result['message']}")
                self.log(f"RESULT: {current_turn} forfeits due to code crash.")
                break
            
            if result["status"] == "invalid_move":
                self.log(f"{result['reason']} (Strike {result['strikes']}/{self.config['max_retries']})")
                if result["forfeit"]:
                    current_turn = self.game.get_turn()
                    forced_winner = "Black" if current_turn == "White" else "White"
                    self.log(f"MAX RETRIES EXCEEDED: {current_turn} forfeits.")
                    break

        self.game_end(winner_override=forced_winner)

    def run_tick(self):
        if self.game.game_over:
            return {"status": "finished", "message": "The game has already ended."}

        current_turn = self.game.get_turn()
        current_player = self.player_map[current_turn]
        fen_before = self.game.export_fen()

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

        log_entry = {
            "turn": current_turn,
            "player": str(current_player),
            "move": move,
            "elapsed": round(elapsed, 3),
            "remaining": round(self.clock[current_turn], 3),
            "success": move_result["success"],
            "fen": fen_before
        }
        self.move_history.append(log_entry)

        if move_result["success"]:
            self.strikes[current_turn] = 0
            if self.game.game_over:
                return {"status": "game_over", "result": self.game.game_result()}
            return {"status": "success"}
        else:
            self.strikes[current_turn] += 1
            is_forfeit = self.strikes[current_turn] >= self.config["max_retries"]
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
        print(f"TURN: {status['Turn']} | WHITE: {self.clock['White']:.1f}s | BLACK: {self.clock['Black']:.1f}s")
        print(self.game.board)
        
        if status['Check']:
            print("!!! YOUR KING IS IN CHECK !!!")

    def game_end(self, winner_override=None):
        self.log("\n" + "═"*20)
        self.log("GAME OVER")

        if winner_override:
            self.log(f"Final Result: {winner_override} wins by technicality/forfeit.")
            self.game.game.headers["Result"] = "1-0" if winner_override == "White" else "0-1"
        else:
            res = self.game.game_result()
            self.log(f"Final Result: {res}")
        
        if self.config["auto_save"]:
            self.game.save_pgn()
            self.log("PGN Saved.")
        
    def get_status(self):
        return {
            "Turn": self.game.get_turn(),
            "Fen": self.game.export_fen(),
            "Check": self.game.is_in_check(),
            "Game Over": self.game.game_over
        }