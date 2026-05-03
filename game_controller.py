from Hnefatafl import reset_board, print_board, Role
from rules_engine import generate_valid_moves, is_valid_move, execute_captures, check_win_condition

 
game_state = {
    "board":        reset_board(11), 
    "current_turn": "ATTACKERS",  
    "selected":     None,          # (row, col) of selected piece
    "valid_moves":  [],            
    "game_over":    False,
    "winner":       None ,     
    "difficulty":   "medium"    
}

def belongs_to_current_turn(piece):
    if game_state["current_turn"] == "ATTACKERS":
        return piece.role == Role.ATTACKER
    else:
        return piece.role == Role.DEFENDER or piece.role == Role.KING
 
 
def switch_turn():
    if game_state["current_turn"] == "ATTACKERS":
        game_state["current_turn"] = "DEFENDERS"
    else:
        game_state["current_turn"] = "ATTACKERS"
 
 
def clear_selection():
    game_state["selected"] = None
    game_state["valid_moves"] = []
    

def select_piece(row, col):
    #Returns True if selection succeeded.
    board = game_state["board"]
    piece = board[row][col]
 
    # Empty cell 
    if piece == '_' or piece is None:
        clear_selection()
        return False
    
    # wrong turn
    if not belongs_to_current_turn(piece):
        clear_selection()
        return False
 
    # Valid selection
    game_state["selected"] = (row, col)
    game_state["valid_moves"] = generate_valid_moves(piece, board)
    return True


def try_move(to_row, to_col):
    #Try to move the selected piece to (to_row, to_col).
    if game_state["game_over"]:
        return False
 
    if game_state["selected"] is None:
        return False
 
    if (to_row, to_col) not in game_state["valid_moves"]:
        return False
 
    board = game_state["board"]
    from_row, from_col = game_state["selected"]
 
    # Move the piece
    piece = board[from_row][from_col]
    board[from_row][from_col] = '_'
    board[to_row][to_col] = piece
    piece.move(to_row, to_col)
 
    # Run capture logic 
    execute_captures(piece.role, to_row, to_col, board)
 
    # Check win condition 
    result = check_win_condition(board)
    if result is not None:
        game_state["game_over"] = True
        game_state["winner"] = result
 
    # Clear selection
    clear_selection()
 
    # Switch turn only if game still going
    if not game_state["game_over"]:
        switch_turn()
 
    return True
 

def handle_click(row, col):
    # Main entry point from the GUI.
    if game_state["game_over"]:
        return "game_over"
 
    # Nothing selected yet , try to select
    if game_state["selected"] is None:
        success = select_piece(row, col)
        return "selected" if success else "invalid"
 
    # Something already selected
    board = game_state["board"]
    piece = board[row][col]
 
    # Clicked the same cell , deselect
    if (row, col) == game_state["selected"]:
        clear_selection()
        return "invalid"
 
    # Clicked another piece of the same team , re-select
    if piece != '_' and piece is not None and belongs_to_current_turn(piece):
        game_state["selected"] = (row, col)
        game_state["valid_moves"] = generate_valid_moves(piece, board)
        return "selected"
 
    # Clicked a destination , try to move
    moved = try_move(row, col)
    return "moved" if moved else "invalid"
 
 
def get_turn_label():
    if game_state["current_turn"] == "ATTACKERS":
        return "Attackers' Turn (Black)"
    else:
        return "Defenders' Turn (White)"


def set_difficulty(level):
    # level = "easy", "medium", or "hard"
    game_state["difficulty"] = level
 
 
def get_depth():
    # Returns the alpha-beta depth based on difficulty
    if game_state["difficulty"] == "easy":
        return 1
    elif game_state["difficulty"] == "medium":
        return 3
    else:  # hard
        return 5

def reset_game():
    current_difficulty = game_state["difficulty"]
    game_state["board"]        = reset_board(11)
    game_state["current_turn"] = "ATTACKERS"
    game_state["selected"]     = None
    game_state["valid_moves"]  = []
    game_state["game_over"]    = False
    game_state["winner"]       = None
    game_state["difficulty"]   = current_difficulty