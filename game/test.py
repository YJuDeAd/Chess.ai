from orchestrator import Orchestrator, HumanPlayer

game = Orchestrator()

p1 = HumanPlayer("May")
p2 = HumanPlayer("Cody")

game.assign_players(p1, p2)

while not game.game.game_over:
    status = game.get_status()
    
    print("\n" + "="*20)
    print(f"TURN: {status['Turn']}")
    print(game.game.board)
    
    if status['Check']:
        print("!!! YOUR KING IS IN CHECK !!!")

    success = game.run_tick()
    
    if not success:
        print("Try again.")

print("\nGAME OVER")
print(f"Result: {game.game.game_result()}")
game.game.save_pgn()