from Hnefatafl import clone_board, Role
from rules_engine import generate_valid_moves, execute_captures, check_win_condition

# Utility Function
def evaluate_board(board):
    result = check_win_condition(board)

    if result == "DEFENDERS":
        return 10000
    elif result == "ATTACKERS":
        return -10000

    attackers = 0
    defenders = 0
    king_pos = None

    for r in range(11):
        for c in range(11):
            piece = board[r][c]

            if piece is None:
                continue

            if piece.role == Role.ATTACKER:
                attackers += 1
            elif piece.role == Role.DEFENDER:
                defenders += 1
            elif piece.role == Role.KING:
                king_pos = (r, c)

    score = 0

    score += defenders * 10
    score -= attackers * 5

    if king_pos:
        r, c = king_pos
        distance = min(
            abs(r-0)+abs(c-0),
            abs(r-0)+abs(c-10),
            abs(r-10)+abs(c-0),
            abs(r-10)+abs(c-10)
        )
        score += (20 - distance)

    return score

def get_all_moves(board, team):
    moves = []

    for r in range(11):
        for c in range(11):
            piece = board[r][c]

            if piece is None:
                continue

            if team == "ATTACKERS" and piece.role == Role.ATTACKER:
                valid = generate_valid_moves(piece, board)
                for move in valid:
                    moves.append(((r, c), move))

            elif team == "DEFENDERS" and piece.role in (Role.DEFENDER, Role.KING):
                valid = generate_valid_moves(piece, board)
                for move in valid:
                    moves.append(((r, c), move))

    return moves

def apply_move(board, move):
    new_board = clone_board(board)

    (r1, c1), (r2, c2) = move
    piece = new_board[r1][c1]

    new_board[r1][c1] = None
    new_board[r2][c2] = piece
    piece.move(r2, c2)

    execute_captures(piece.role, r2, c2, new_board)

    return new_board

def alpha_beta(board, depth, alpha, beta, maximizing_player):

    result = check_win_condition(board)

    if depth == 0 or result is not None:
        return evaluate_board(board)

    if maximizing_player:  # DEFENDERS (maximize)
        value = float('-inf')
        moves = get_all_moves(board, "DEFENDERS")

        for move in moves:
            new_board = apply_move(board, move)

            value = max(
                value,
                alpha_beta(new_board, depth - 1, alpha, beta, False)
            )

            alpha = max(alpha, value)

            if beta <= alpha:
                break

        return value

    else:  # ATTACKERS (minimize)
        value = float('inf')
        moves = get_all_moves(board, "ATTACKERS")

        for move in moves:
            new_board = apply_move(board, move)

            value = min(
                value,
                alpha_beta(new_board, depth - 1, alpha, beta, True)
            )

            beta = min(beta, value)

            if beta <= alpha:
                break

        return value

def get_best_move(board, depth, team):
    best_move = None

    if team == "DEFENDERS":
        best_value = float('-inf')
        moves = get_all_moves(board, "DEFENDERS")

        for move in moves:
            new_board = apply_move(board, move)

            value = alpha_beta(
                new_board,
                depth - 1,
                float('-inf'),
                float('inf'),
                False
            )

            if value > best_value:
                best_value = value
                best_move = move

    else:  # ATTACKERS
        best_value = float('inf')
        moves = get_all_moves(board, "ATTACKERS")

        for move in moves:
            new_board = apply_move(board, move)

            value = alpha_beta(
                new_board,
                depth - 1,
                float('-inf'),
                float('inf'),
                True
            )

            if value < best_value:
                best_value = value
                best_move = move

    return best_move