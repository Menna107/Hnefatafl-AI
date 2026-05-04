from enum import Enum

# n = int(input("Enter board size (odd number >= 7): "))
#
# if n % 2 == 0 or n < 7:
#     print("Invalid size")
#     exit()

class Role(Enum):
    KING = 'K'
    DEFENDER = 'D'
    ATTACKER = 'A'

class Piece:
    def __init__(self, role, row, col):
        self.role = role
        self.position = (row, col)

    def move(self, new_row: int, new_col: int):
        self.position = (new_row, new_col)

n = 11
board = []
for i in range(n):
    row = []
    for j in range(n):
        row.append(None)
    board.append(row)


def setup_board(board, n):
    mid = n // 2

    board[mid][mid] = Piece(Role.KING, mid, mid)

    for i in range(1, 3):
        board[mid - i][mid] = Piece(Role.DEFENDER, mid - i, mid)
        board[mid + i][mid] = Piece(Role.DEFENDER, mid + i, mid)
        board[mid][mid - i] = Piece(Role.DEFENDER, mid, mid - i)
        board[mid][mid + i] = Piece(Role.DEFENDER, mid, mid + i)

    diagonals = [
        (mid - 1, mid - 1),
        (mid - 1, mid + 1),
        (mid + 1, mid - 1),
        (mid + 1, mid + 1)
    ]

    for r, c in diagonals:
        board[r][c] = Piece(Role.DEFENDER, r, c)

    board[0][mid] = Piece(Role.ATTACKER, 0, mid)
    board[n-1][mid] = Piece(Role.ATTACKER, n-1, mid)
    board[mid][0] = Piece(Role.ATTACKER, mid, 0)
    board[mid][n-1] = Piece(Role.ATTACKER, mid, n-1)

    for i in range(mid - 2, mid + 3):
        board[0][i] = Piece(Role.ATTACKER, 0, i)
        board[n-1][i] = Piece(Role.ATTACKER, n-1, i)
        board[i][0] = Piece(Role.ATTACKER, i, 0)
        board[i][n-1] = Piece(Role.ATTACKER, i, n-1)

    board[1][mid] = Piece(Role.ATTACKER, 1, mid)
    board[n-2][mid] = Piece(Role.ATTACKER, n-2, mid)
    board[mid][1] = Piece(Role.ATTACKER, mid, 1)
    board[mid][n-2] = Piece(Role.ATTACKER, mid, n-2)

def print_board(board):
    for row in board:
        formatted_row = []
        for cell in row:
            if cell is None:
                formatted_row.append('_')
            else:
                formatted_row.append(cell.role.value)
        print(' '.join(formatted_row))

def clone_board(board):
    new_board = []
    for row in board:
        new_row = []
        for cell in row:
            if cell is None:
                new_row.append(None)
            else:
                new_row.append(Piece(cell.role, cell.position[0], cell.position[1]))
        new_board.append(new_row)
    return new_board

def reset_board(n):
    board = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append(None)
        board.append(row)

    setup_board(board, n)
    return board
