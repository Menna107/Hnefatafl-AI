# n = int(input("Enter board size (odd number >= 7): "))
#
# if n % 2 == 0 or n < 7:
#     print("Invalid size")
#     exit()

n = 11
board = []
for i in range(n):
    row = []
    for j in range(n):
        row.append('_')
    board.append(row)

King = 'K'
Defender = 'D'
Attacker = 'A'

def setup_board(board, n):
    mid = n // 2

    board[mid][mid] = King

    for i in range(1, 3):
        board[mid - i][mid] = Defender
        board[mid + i][mid] = Defender
        board[mid][mid - i] = Defender
        board[mid][mid + i] = Defender

    diagonals = [
        (mid - 1, mid - 1),
        (mid - 1, mid + 1),
        (mid + 1, mid - 1),
        (mid + 1, mid + 1)
    ]

    for r, c in diagonals:
        board[r][c] = Defender

    board[0][mid] = Attacker
    board[n-1][mid] = Attacker
    board[mid][0] = Attacker
    board[mid][n-1] = Attacker

    for i in range(mid - 2, mid + 3):
        board[0][i] = Attacker
        board[n-1][i] = Attacker
        board[i][0] = Attacker
        board[i][n-1] = Attacker

    board[1][mid] = Attacker
    board[n-2][mid] = Attacker
    board[mid][1] = Attacker
    board[mid][n-2] = Attacker

def print_board(board):
    for row in board:
        print(' '.join(row))

def clone_board(board):
    new_board = []
    for row in board:
        new_row = []
        for cell in row:
            new_row.append(cell)
        new_board.append(new_row)
    return new_board

def reset_board(n):
    board = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append('_')
        board.append(row)

    setup_board(board, n)
    return board
