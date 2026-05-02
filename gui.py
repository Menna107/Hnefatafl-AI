import tkinter as tk
from Hnefatafl import reset_board

class GameGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hnefatafl")

        self.n = 11
        self.board = reset_board(self.n)

        self.cell_size = 50
        self.selected = None
        self.valid_moves = []

        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.canvas = tk.Canvas(
            self.frame,
            width=self.n * self.cell_size,
            height=self.n * self.cell_size,
            bg="#a8d5ba"
        )
        self.canvas.pack()

        # Bind clicks
        self.canvas.bind("<Button-1>", self.on_click)

        # Draw board
        self.redraw()

        # Reset button
        reset_btn = tk.Button(self.frame, text="Reset", command=self.reset_game)
        reset_btn.pack()

    def draw_grid(self):
        mid = self.n // 2

        for i in range(self.n):
            for j in range(self.n):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                # Default cell color
                fill_color = "#a8d5ba"

                # Throne (center)
                if (i, j) == (mid, mid):
                    fill_color = "#2e8b57"

                # Corners
                elif (i, j) in [(0,0), (0,self.n-1), (self.n-1,0), (self.n-1,self.n-1)]:
                    fill_color = "#2e8b57"

                # Draw cell
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=fill_color,
                    outline="#2e8b57"
                )

                # Highlight selected cell
                if self.selected == (i, j):
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        outline="yellow",
                        width=3
                    )
                
                # Highlight valid moves
                elif (i, j) in self.valid_moves:
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        outline="blue",
                        width=2
                    )

    def draw_pieces(self):
        self.canvas.delete("piece")

        for i in range(self.n):
            for j in range(self.n):
                piece = self.board[i][j]

                if piece == '_':
                    continue

                x = j * self.cell_size
                y = i * self.cell_size
                padding = 8

                if piece == 'A':  # attacker (black)
                    color = "#1f1f1f"
                elif piece == 'D':  # defender (white)
                    color = "#d9d9d9"
                elif piece == 'K':  # king
                    color = "#cfd8dc"

                self.canvas.create_oval(
                    x + padding, y + padding,
                    x + self.cell_size - padding,
                    y + self.cell_size - padding,
                    fill=color,
                    outline="gray",
                    tags="piece"
                )

                # Draw crown for king
                if piece == 'K':
                    self.canvas.create_text(
                        x + self.cell_size/2,
                        y + self.cell_size/2,
                        text="♛",
                        font=("Arial", 16),
                        tags="piece"
                    )

    def redraw(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_pieces()

    def on_click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size

        if self.selected is None:
            if self.board[row][col] != '_':
                self.selected = (row, col)

                # TEMP: fake valid moves (for testing UI)
                self.valid_moves = [(row, col+1), (row, col-1)]
                
        else:
            self.make_move(self.selected, (row, col))
            self.selected = None
            self.valid_moves = []
        
        self.redraw()

    #temp move until the logic is implemented
    def make_move(self, from_pos, to_pos):
        r1, c1 = from_pos
        r2, c2 = to_pos

        piece = self.board[r1][c1]
        self.board[r1][c1] = '_'
        self.board[r2][c2] = piece

    def reset_game(self):
        self.board = reset_board(self.n)
        self.redraw()

    def run(self):
        self.root.mainloop()


    