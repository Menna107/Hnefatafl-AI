import tkinter as tk
from tkinter import messagebox
from Hnefatafl import reset_board, Role
from game_controller import handle_click, game_state, reset_game as controller_reset, get_turn_label, get_depth, set_difficulty
from ai import get_best_move, get_all_moves

import threading

class GameGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hnefatafl")

        self.n = 11
        self.board = reset_board(self.n)

        self.cell_size = 50
        self.selected = None
        self.valid_moves = []

        self.human_team = "DEFENDERS"
        self.ai_team = "ATTACKERS"
        self.is_ai_thinking = False

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

        # Turn label
        self.turn_label = tk.Label(self.frame, text=get_turn_label())
        self.turn_label.pack()

        self.show_start_menu()

    def show_start_menu(self):
        self.menu_window = tk.Toplevel(self.root)
        self.menu_window.title("Start Game")

        self.menu_window.transient(self.root)   
        self.menu_window.grab_set()             
        self.menu_window.focus_force()          

        tk.Label(self.menu_window, text="Choose Your Team").pack(pady=10)

        self.team_choice = tk.StringVar(value="DEFENDERS")

        tk.Radiobutton(self.menu_window, text="Defenders (White)", 
                    variable=self.team_choice, value="DEFENDERS").pack()

        tk.Radiobutton(self.menu_window, text="Attackers (Black)", 
                    variable=self.team_choice, value="ATTACKERS").pack()

        tk.Label(self.menu_window, text="Difficulty").pack(pady=10)

        self.diff_choice = tk.StringVar(value="medium")

        tk.Radiobutton(self.menu_window, text="Easy", variable=self.diff_choice, value="easy").pack()
        tk.Radiobutton(self.menu_window, text="Medium", variable=self.diff_choice, value="medium").pack()
        tk.Radiobutton(self.menu_window, text="Hard", variable=self.diff_choice, value="hard").pack()

        tk.Button(self.menu_window, text="Start Game", command=self.start_game).pack(pady=15)

    def start_game(self):
        team = self.team_choice.get()
        difficulty = self.diff_choice.get()

        # Set teams
        self.human_team = team
        self.ai_team = "ATTACKERS" if team == "DEFENDERS" else "DEFENDERS"

        # Set difficulty
        set_difficulty(difficulty)

        # Reset game
        controller_reset()
        self.board = game_state["board"]

        self.selected = None
        self.valid_moves = []

        self.turn_label.config(text=get_turn_label())
        self.redraw()

        # Close menu
        self.menu_window.destroy()

        # If AI starts → trigger it
        if game_state["current_turn"] == self.ai_team:
            self.root.after(300, self.ai_move)

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

                if piece is None:
                    continue

                x = j * self.cell_size
                y = i * self.cell_size
                padding = 8

                if piece.role == Role.ATTACKER:  # attacker (black)
                    color = "#1f1f1f"
                elif piece.role == Role.DEFENDER:  # defender (white)
                    color = "#d9d9d9"
                elif piece.role == Role.KING:  # king
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
                if piece.role == Role.KING:
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
        if self.is_ai_thinking:
            return

        if game_state["current_turn"] != self.human_team:
            return

        col = event.x // self.cell_size
        row = event.y // self.cell_size


        result = handle_click(row, col)

        self.board = game_state["board"]
        self.selected = game_state["selected"]
        self.valid_moves = game_state["valid_moves"]

        self.turn_label.config(text=get_turn_label())
        self.redraw()

        if game_state["game_over"]:
            self.show_winner(game_state["winner"])
            return

        if result == "moved":
            self.root.after(200, self.ai_move)

    def reset_game(self):
        controller_reset()
        self.board = game_state["board"]
        self.selected = None
        self.valid_moves = []
        self.turn_label.config(text=get_turn_label())

        self.redraw()

    def show_winner(self, winner):
        result = messagebox.askquestion("Game Over", f"{winner} wins!\nPlay again?")

        if result == "yes":
            self.show_start_menu()

    def ai_move(self):
        if game_state["game_over"]:
            return

        if game_state["current_turn"] != self.ai_team:
            return

        self.is_ai_thinking = True

        threading.Thread(target=self._compute_ai_move).start()

    def _compute_ai_move(self):
        board = game_state["board"]
        depth = get_depth()

        move = get_best_move(board, depth, self.ai_team)

        if move is None:
            self.root.after(0, lambda: setattr(self, "is_ai_thinking", False))
            return

        def apply_move():
            (r1, c1), (r2, c2) = move

            handle_click(r1, c1)
            handle_click(r2, c2)

            self.board = game_state["board"]
            self.selected = game_state["selected"]
            self.valid_moves = game_state["valid_moves"]

            self.turn_label.config(text=get_turn_label())
            self.redraw()

            self.is_ai_thinking = False

            if game_state["game_over"]:
                self.show_winner(game_state["winner"])

        # Send back to UI thread
        self.root.after(0, apply_move)

    def run(self):
        self.root.mainloop()


    