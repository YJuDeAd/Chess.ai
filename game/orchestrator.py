from core import Core
import random


class Orchestrator:
    def __init__(self):
        self.game = Core()
        self.white = None
        self.black = None

    def assign_player(self, player1, player2):
        self.white = random.choice([player1, player2])
        self.black = player2 if self.white == player1 else player1
        print(self.white)
        print(self.black)