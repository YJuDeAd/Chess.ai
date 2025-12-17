from main import Core

game = Core()

while not game.check_status():
    print(f"{game.get_turn()}'s Turn")
    
    if game.is_in_check():
        print("YOUR KING IS IN CHECK!")

    print(game.board)

    user_move = input("Enter move (e.g., a2a4): ")
    
    try:
        game.make_move(user_move)
    except ValueError as e:
        print(e)

game.save_pgn()