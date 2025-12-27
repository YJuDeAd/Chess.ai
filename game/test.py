from orchestrator import Orchestrator, HumanPlayer

game = Orchestrator()

p1 = HumanPlayer("May")
p2 = HumanPlayer("Cody")

game.assign_players(p1, p2)
game.start_match()