from Hnefatafl import Role

CORNERS = {(0, 0), (0, 10), (10, 0), (10, 10)}
THRONE = (5, 5)



def is_suicide(r, c, piece_role, board):
    if piece_role == Role.KING:
        return False 

    left_piece  = board[r][c-1] if c - 1 >= 0 else None
    right_piece = board[r][c+1] if c + 1 <= 10 else None
    up_piece    = board[r-1][c] if r - 1 >= 0 else None
    down_piece  = board[r+1][c] if r + 1 <= 10 else None

    restricted = {(0, 0), (0, 10), (10, 0), (10, 10), (5, 5)}
    left_is_restricted  = (r, c-1) in restricted
    right_is_restricted = (r, c+1) in restricted
    up_is_restricted    = (r-1, c) in restricted
    down_is_restricted  = (r+1, c) in restricted

    if piece_role == Role.ATTACKER:
        left_is_enemy  = (left_piece is not None and left_piece.role == Role.DEFENDER)
        right_is_enemy = (right_piece is not None and right_piece.role == Role.DEFENDER)
        up_is_enemy    = (up_piece is not None and up_piece.role == Role.DEFENDER)
        down_is_enemy  = (down_piece is not None and down_piece.role == Role.DEFENDER)

        if (left_is_enemy or left_is_restricted) and (right_is_enemy or right_is_restricted):
            return True
        
        if (up_is_enemy or up_is_restricted) and (down_is_enemy or down_is_restricted):
            return True

    elif piece_role == Role.DEFENDER:
        left_is_enemy  = (left_piece is not None and left_piece.role == Role.ATTACKER)
        right_is_enemy = (right_piece is not None and right_piece.role == Role.ATTACKER)
        up_is_enemy    = (up_piece is not None and up_piece.role == Role.ATTACKER)
        down_is_enemy  = (down_piece is not None and down_piece.role == Role.ATTACKER)

        if (left_is_enemy or left_is_restricted) and (right_is_enemy or right_is_restricted):
            return True
        
        if (up_is_enemy or up_is_restricted) and (down_is_enemy or down_is_restricted):
            return True

    return False

def process_square(target_row, target_col, piece, board, valid_moves):

    if target_row < 0 or target_row > 10 or target_col < 0 or target_col > 10:
        return False

    if board[target_row][target_col] is not None:
        return False

    if (target_row, target_col) in CORNERS.union({THRONE}):
        if piece.role == Role.KING:
            valid_moves.append((target_row, target_col))
            return True 
        else:
            return False

    if(is_suicide(target_row, target_col, piece.role, board)):
        return True
    
    valid_moves.append((target_row, target_col))
    return True


def generate_valid_moves(piece, board):
    valid_moves = []
    start_row, start_col = piece.position

    # Scan UP
    for r in range(start_row - 1, -1, -1):
        if not process_square(r, start_col, piece, board, valid_moves): 
            break
            
    # Scan DOWN
    for r in range(start_row + 1, 11):
        if not process_square(r, start_col, piece, board, valid_moves): 
            break
            
    # Scan LEFT
    for c in range(start_col - 1, -1, -1):
        if not process_square(start_row, c, piece, board, valid_moves): 
            break
            
    # Scan RIGHT
    for c in range(start_col + 1, 11):
        if not process_square(start_row, c, piece, board, valid_moves): 
            break

    return valid_moves


#########################
#########################
#########################
#########################
#########################


def is_valid_move(piece, target_row, target_col, board):
    valid_moves = generate_valid_moves(piece, board)
    return (target_row, target_col) in valid_moves



#########################
#########################
#########################
#########################
#########################


def execute_captures(piece_role, r, c, board):
    if piece_role == Role.KING:
        return

    restricted = {(0, 0), (0, 10), (10, 0), (10, 10), (5, 5)}
    captured_pieces = []

    # --- Check RIGHT ---
    if c + 2 <= 10:
        possible_enemy = board[r][c+1]
        possible_ally = board[r][c+2]
        possible_ally_pos = (r, c+2)
        
        # Is there an enemy? (And it's NOT the King)
        if possible_enemy is not None and possible_enemy.role != piece_role and possible_enemy.role != Role.KING:
            # Is the other side an ally, or a restricted square?
            if (possible_ally is not None and possible_ally.role == piece_role) or (possible_ally_pos in restricted):
                captured_pieces.append((r, c+1))

    # --- Check LEFT ---
    if c - 2 >= 0:
        possible_enemy = board[r][c-1]
        possible_ally = board[r][c-2]
        possible_ally_pos = (r, c-2)
        
        if possible_enemy is not None and possible_enemy.role != piece_role and possible_enemy.role != Role.KING:
            if (possible_ally is not None and possible_ally.role == piece_role) or (possible_ally_pos in restricted):
                captured_pieces.append((r, c-1))

    # --- Check DOWN ---
    if r + 2 <= 10:
        possible_enemy = board[r+1][c]
        possible_ally = board[r+2][c]
        possible_ally_pos = (r+2, c)
        
        if possible_enemy is not None and possible_enemy.role != piece_role and possible_enemy.role != Role.KING:
            if (possible_ally is not None and possible_ally.role == piece_role) or (possible_ally_pos in restricted):
                captured_pieces.append((r+1, c))

    # --- Check UP ---
    if r - 2 >= 0:
        possible_enemy = board[r-1][c]
        possible_ally = board[r-2][c]
        possible_ally_pos = (r-2, c)
        
        if possible_enemy is not None and possible_enemy.role != piece_role and possible_enemy.role != Role.KING:
            if (possible_ally is not None and possible_ally.role == piece_role) or (possible_ally_pos in restricted):
                captured_pieces.append((r-1, c))

    # Remove all captured pieces from the board
    for row, col in captured_pieces:
        board[row][col] = None




def is_king_captured_or_escaped(board):
   
    kr, kc = -1, -1
    
    # Find the King
    for r in range(11):
        for c in range(11):
            piece = board[r][c]
            if piece is not None and piece.role == Role.KING:
                kr, kc = r, c
                break
        if kr != -1:
            break
        
    if kr == -1:
        return "ATTACKERS" # Edge case: King was somehow removed
    
    # Check if Defenders won (King reached a corner)
    if (kr, kc) in CORNERS:
        return "DEFENDERS"

    # Check if Attackers won (King is surrounded on 4 hostile sides)
    hostile_sides = 0
    restricted = CORNERS.union({THRONE})

    # UP
    if kr - 1 < 0: 
        hostile_sides += 1
    elif board[kr-1][kc] is not None and board[kr-1][kc].role == Role.ATTACKER: 
        hostile_sides += 1
    elif (kr-1, kc) in restricted:
        hostile_sides += 1

    # DOWN
    if kr + 1 > 10:
        hostile_sides += 1
    elif board[kr+1][kc] is not None and board[kr+1][kc].role == Role.ATTACKER: 
        hostile_sides += 1
    elif (kr+1, kc) in restricted:
        hostile_sides += 1

    # LEFT
    if kc - 1 < 0: 
        hostile_sides += 1
    elif board[kr][kc-1] is not None and board[kr][kc-1].role == Role.ATTACKER: 
        hostile_sides += 1
    elif (kr, kc-1) in restricted: 
        hostile_sides += 1

    # RIGHT
    if kc + 1 > 10: 
        hostile_sides += 1
    elif board[kr][kc+1] is not None and board[kr][kc+1].role == Role.ATTACKER: 
        hostile_sides += 1
    elif (kr, kc+1) in restricted: 
        hostile_sides += 1

    if hostile_sides == 4:
        return "ATTACKERS"

    return None


def has_legal_moves(team, board):
    for r in range(11):
        for c in range(11):
            piece = board[r][c]
            
            if piece is not None:
                # If checking ATTACKERS, look only at Attacker pieces
                if team == "ATTACKERS" and piece.role == Role.ATTACKER:
                    moves = generate_valid_moves(piece, board)
                    if len(moves) > 0:
                        return True
                        
                # If checking DEFENDERS, look at both Defender and King pieces
                elif team == "DEFENDERS" and piece.role in (Role.DEFENDER, Role.KING):
                    moves = generate_valid_moves(piece, board)
                    if len(moves) > 0:
                        return True
                        
    # If we scanned the whole board and found 0 moves for this team
    return False


def check_win_condition(board):
    
    # 1. Did the King escape or get captured?
    king_status = is_king_captured_or_escaped(board)
    if king_status is not None:
        return king_status

    # 2. Are the Attackers completely blocked with zero moves?
    if not has_legal_moves("ATTACKERS", board):
        return "DEFENDERS"

    # 3. Are the Defenders completely blocked with zero moves?
    if not has_legal_moves("DEFENDERS", board):
        return "ATTACKERS"

    # If no conditions are met, the game keeps going!
    return None