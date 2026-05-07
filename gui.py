import tkinter as tk
from tkinter import ttk
import threading
from Hnefatafl import reset_board, Role
from game_controller import handle_click, game_state, reset_game as controller_reset, get_turn_label, get_depth, \
    set_difficulty
from ai import get_best_move


class GameGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hnefatafl")
        self.root.withdraw()

        self.n = 11
        self.cell_size = 50
        self.selected = None
        self.valid_moves = []
        self.is_ai_thinking = False

        # --- Game UI Setup ---
        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack()

        self.header_frame = tk.Frame(self.game_frame, bg="#f4fbf7", pady=5)
        self.header_frame.pack(fill="x")

        self.back_btn = tk.Button(
            self.header_frame,
            text="  ❮  Back to Menu  ",
            command=self.return_to_menu,
            bg="#ffffff",
            fg="#2e8b57",
            font=("Arial", 10, "bold"),
            relief="flat",
            activebackground="#2e8b57",
            activeforeground="white",
            cursor="hand2",
            padx=10
        )
        self.back_btn.pack(side="left", padx=10)
        self.back_btn.bind("<Enter>", lambda e: self.back_btn.config(bg="#e8f5ed"))
        self.back_btn.bind("<Leave>", lambda e: self.back_btn.config(bg="#ffffff"))

        tk.Label(self.header_frame, text="HNEFATAFL", font=("Impact", 15),
                 bg="#f4fbf7", fg="#2e8b57").pack(side="right", padx=15)

        self.canvas = tk.Canvas(
            self.game_frame,
            width=self.n * self.cell_size,
            height=self.n * self.cell_size,
            bg="#a8d5ba"
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        self.turn_label = tk.Label(self.game_frame, text="", font=("Impact", 15), bg="#f4fbf7", fg="#2e8b57")
        self.turn_label.pack(pady=5)

        self.show_main_menu()

    def center_window(self, window, width, height):
        """Center any window on the screen"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def show_main_menu(self):
        """Build and show the main menu window"""
        self.menu_window = tk.Toplevel()
        self.menu_window.title("Hnefatafl - Strategy Game")

        menu_width = self.n * self.cell_size
        menu_height = 680
        self.center_window(self.menu_window, menu_width, menu_height)
        self.menu_window.configure(bg="#f4fbf7")
        self.menu_window.protocol("WM_DELETE_WINDOW", self.root.quit)

        main_container = tk.Frame(self.menu_window, bg="#f4fbf7")
        main_container.pack(expand=True, fill="both")

        content_frame = tk.Frame(main_container, bg="#f4fbf7")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        def update_styles():
            for val, btn in team_btns.items():
                if self.team_choice.get() == val:
                    btn.config(fg="white")
                else:
                    btn.config(fg="#2e8b57" if val == "DEFENDERS" else "white")
            for val, btn in diff_btns.items():
                if self.diff_choice.get() == val:
                    btn.config(fg="white")
                else:
                    btn.config(fg="#2e8b57")

        # --- Menu Header ---
        tk.Label(content_frame, text="Viking Chess", font=("Garamond", 18),
                 bg="#f4fbf7", fg="#555").pack(pady=(0, 0))
        tk.Label(content_frame, text="HNEFATAFL", font=("Impact", 45),
                 bg="#f4fbf7", fg="#2e8b57").pack(pady=(0, 20))

        # --- Team Selection ---
        tk.Label(content_frame, text="CHOOSE YOUR SIDE", font=("Arial", 10, "bold"),
                 bg="#f4fbf7", fg="#2e8b57").pack()

        team_frame = tk.Frame(content_frame, bg="#f4fbf7")
        team_frame.pack(pady=10)

        self.team_choice = tk.StringVar(value="DEFENDERS")
        team_btns = {}

        def_btn = tk.Radiobutton(team_frame, text="White Side\n(Defenders)", variable=self.team_choice,
                                 value="DEFENDERS", indicatoron=0, width=15, height=3,
                                 bg="white", fg="#2e8b57", selectcolor="#2e8b57",
                                 activebackground="#2e8b57", activeforeground="white",
                                 font=("Arial", 10, "bold"), relief="flat", command=update_styles)
        def_btn.pack(side="left", padx=10)
        team_btns["DEFENDERS"] = def_btn

        att_btn = tk.Radiobutton(team_frame, text="Black Side\n(Attackers)", variable=self.team_choice,
                                 value="ATTACKERS", indicatoron=0, width=15, height=3,
                                 bg="#333", fg="white", selectcolor="#2e8b57",
                                 activebackground="#2e8b57", activeforeground="white",
                                 font=("Arial", 10, "bold"), relief="flat", command=update_styles)
        att_btn.pack(side="left", padx=10)
        team_btns["ATTACKERS"] = att_btn

        # --- Difficulty Selection ---
        tk.Label(content_frame, text="AI DIFFICULTY", font=("Arial", 10, "bold"),
                 bg="#f4fbf7", fg="#2e8b57").pack(pady=(20, 5))

        diff_outer_frame = tk.Frame(content_frame, bg="#e8f5ed", padx=5, pady=5)
        diff_outer_frame.pack(pady=5)

        self.diff_choice = tk.StringVar(value="medium")
        diff_btns = {}
        for text, mode in [("EASY", "easy"), ("MEDIUM", "medium"), ("HARD", "hard")]:
            rb = tk.Radiobutton(diff_outer_frame, text=text, variable=self.diff_choice, value=mode,
                                indicatoron=0, width=10, pady=8, bg="#e8f5ed", fg="#2e8b57",
                                selectcolor="#2e8b57", activebackground="#2e8b57", activeforeground="white",
                                font=("Arial", 9, "bold"), relief="flat", command=update_styles)
            rb.pack(side="left", padx=1)
            diff_btns[mode] = rb

        update_styles()

        # --- Main Buttons ---
        start_btn = tk.Button(content_frame, text="START BATTLE", command=self.start_game,
                              font=("Arial", 13, "bold"), bg="#2e8b57", fg="white",
                              activebackground="#1e5e3a", relief="flat", width=22, pady=12, cursor="hand2")
        start_btn.pack(pady=(30, 10))

        tk.Button(content_frame, text="HOW TO PLAY", command=self.show_rules,
                  font=("Arial", 10, "bold"), bg="#f4fbf7", fg="#2e8b57",
                  relief="flat", cursor="hand2").pack()

        tk.Button(content_frame, text="EXIT GAME", command=self.root.quit,
                  font=("Arial", 10), bg="#f4fbf7", fg="#999",
                  activebackground="#f4fbf7", relief="flat", cursor="hand2").pack(pady=(5, 20))

        # --- Footer ---
        footer_frame = tk.Frame(self.menu_window, bg="#f4fbf7")
        footer_frame.pack(side="bottom", pady=15)
        tk.Label(footer_frame, text="DEVELOPED BY", font=("Arial", 8, "bold"),
                 bg="#f4fbf7", fg="#bccad6").pack()
        team_names = "Menna Hekal • Salma Mohamed • Hazem Ahmed • Malak Nour • Adam Mohamed"
        tk.Label(footer_frame, text=team_names, font=("Arial", 8),
                 bg="#f4fbf7", fg="#999").pack()

    def show_rules(self):
        """Display game rules in a scrollable Toplevel window"""
        rules_win = tk.Toplevel(self.menu_window)
        rules_win.title("How To Play")
        self.center_window(rules_win, 480, 580)
        rules_win.configure(bg="#f4fbf7")
        rules_win.resizable(False, False)

        tk.Label(rules_win, text="GAME RULES", font=("Impact", 25), bg="#f4fbf7", fg="#2e8b57").pack(pady=(15, 5))

        container = tk.Frame(rules_win, bg="white", highlightthickness=1, highlightbackground="#2e8b57")
        container.pack(padx=20, pady=10, fill="both", expand=True)

        canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white", padx=10)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=420)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        rules_content = [
            ("The Objective",
             "• Defenders: Move the King to any of the 4 corner squares.\n• Attackers: Capture the King to win."),
            ("Turn Order", "• Attackers always move first.\n• Players take turns moving one piece per turn."),
            ("Movement", "• All pieces move any number of squares horizontally or vertically."),
            ("Capturing Pieces", "• Sandwich an enemy piece between two of your pieces."),
            ("Capturing the KING",
             "• Surround him on all 4 sides.\n• Against a wall: Surround 3 sides.\n• Against a corner: Surround 2 sides."),
            ("Special Squares", "• Only the King can occupy the center and the 4 corner squares.")
        ]

        for title, content in rules_content:
            tk.Label(scrollable_frame, text=title, font=("Arial", 11, "bold"), bg="white", fg="#2e8b57").pack(
                anchor="w", pady=(10, 0))
            tk.Label(scrollable_frame, text=content, font=("Arial", 10), bg="white", fg="#444", justify="left",
                     wraplength=400).pack(anchor="w", pady=(0, 5))

        btn_close = tk.Button(rules_win, text="GOT IT", command=rules_win.destroy,
                              font=("Arial", 11, "bold"), bg="#2e8b57", fg="white", relief="flat", width=15, pady=8)
        btn_close.pack(pady=15)

    def start_game(self):
        """Initialize game state and switch from menu to game board"""
        set_difficulty(self.diff_choice.get())
        self.human_team = self.team_choice.get()
        self.ai_team = "ATTACKERS" if self.human_team == "DEFENDERS" else "DEFENDERS"
        controller_reset()
        self.board = game_state["board"]
        self.menu_window.withdraw()

        self.center_window(self.root, self.n * self.cell_size, (self.n * self.cell_size) + 80)
        self.root.deiconify()
        self.turn_label.config(text=get_turn_label())
        self.redraw()
        if game_state["current_turn"] == self.ai_team:
            self.root.after(300, self.ai_move)

    def show_winner(self, winner):
        """Display the victory window with the winner's name"""
        win_win = tk.Toplevel(self.root)
        win_win.title("🏆 Victory - Hnefatafl")
        self.center_window(win_win, 480, 450)
        win_win.configure(bg="#f4fbf7")
        win_win.grab_set()
        win_win.resizable(False, False)

        border_frame = tk.Frame(win_win, bg="#2e8b57", padx=1, pady=1)
        border_frame.pack(expand=True, fill="both", padx=15, pady=15)
        inner_border = tk.Frame(border_frame, bg="#f4fbf7", padx=2, pady=2)
        inner_border.pack(expand=True, fill="both")
        main_frame = tk.Frame(inner_border, bg="#f4fbf7", highlightthickness=1, highlightbackground="#d1e7dd")
        main_frame.pack(expand=True, fill="both")

        tk.Label(main_frame, text="👑", font=("Segoe UI Emoji", 45), bg="#f4fbf7").pack(pady=(25, 0))
        tk.Label(main_frame, text="VICTORY", font=("Impact", 45), bg="#f4fbf7", fg="#2e8b57").pack()
        tk.Label(main_frame, text="◦ ◦ ◦ ◦ ◦ ◦ ◦", font=("Arial", 12), bg="#f4fbf7", fg="#2e8b57").pack()

        winner_role = "THE DEFENDERS WIN" if "Defender" in winner else "THE ATTACKERS WIN"
        tk.Label(main_frame, text=winner_role, font=("Garamond", 24, "bold"), bg="#f4fbf7", fg="#1a1a1a").pack(
            pady=(30, 0))

        btn_frame = tk.Frame(main_frame, bg="#f4fbf7")
        btn_frame.pack(side="bottom", pady=(0, 40))

        def create_fancy_button(parent, text, cmd, primary=True):
            bg_color = "#2e8b57" if primary else "#f4fbf7"
            fg_color = "#ffffff" if primary else "#2e8b57"
            return tk.Button(
                parent, text=text, command=cmd, font=("Verdana", 9, "bold"), bg=bg_color, fg=fg_color,
                activebackground="#1e5e3a" if primary else "#e8f5ed", relief="flat", width=15, pady=10,
                cursor="hand2", highlightthickness=1, highlightbackground="#2e8b57"
            )

        menu_btn = create_fancy_button(btn_frame, "MAIN MENU",
                                       lambda: [win_win.destroy(), self.return_to_menu(ask=False)], primary=False)
        menu_btn.pack(side="left", padx=10)
        exit_btn = create_fancy_button(btn_frame, "EXIT GAME", self.root.quit, primary=True)
        exit_btn.pack(side="left", padx=10)

    def return_to_menu(self, ask=True):
        """Switch back from the game board to the main menu"""
        if ask:
            if self.show_custom_confirm("QUIT GAME", "Are you sure you want to return to main menu?"):
                self.root.withdraw()
                self.menu_window.deiconify()
        else:
            self.root.withdraw()
            self.menu_window.deiconify()

    def show_custom_confirm(self, title, message):
        """Custom styled confirmation dialog"""
        confirm_win = tk.Toplevel(self.root)
        confirm_win.title(title)
        self.center_window(confirm_win, 400, 200)
        confirm_win.configure(bg="#f4fbf7")
        confirm_win.grab_set()
        confirm_win.resizable(False, False)
        confirm_win.transient(self.root)

        tk.Label(confirm_win, text=title, font=("Impact", 18), bg="#f4fbf7", fg="#2e8b57").pack(pady=(20, 5))
        tk.Label(confirm_win, text=message, font=("Garamond", 12), bg="#f4fbf7", fg="#333").pack(pady=10)

        btn_frame = tk.Frame(confirm_win, bg="#f4fbf7")
        btn_frame.pack(pady=20)
        self.result = False

        def on_confirm():
            self.result = True
            confirm_win.destroy()

        tk.Button(btn_frame, text="YES, RETURN", command=on_confirm, font=("Verdana", 9, "bold"),
                  bg="#2e8b57", fg="white", width=12, pady=5, relief="flat", cursor="hand2").pack(side="left", padx=10)
        tk.Button(btn_frame, text="CANCEL", command=confirm_win.destroy, font=("Verdana", 9, "bold"),
                  bg="#ffffff", fg="#2e8b57", width=12, pady=5, relief="flat", cursor="hand2",
                  highlightthickness=1, highlightbackground="#2e8b57").pack(side="left", padx=10)

        self.root.wait_window(confirm_win)
        return self.result

    def draw_grid(self):
        """Draw the game board squares"""
        mid = self.n // 2
        for i in range(self.n):
            for j in range(self.n):
                x1, y1 = j * self.cell_size, i * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                fill_color = "#a8d5ba"
                if (i, j) == (mid, mid) or (i, j) in [(0, 0), (0, self.n - 1), (self.n - 1, 0),
                                                      (self.n - 1, self.n - 1)]:
                    fill_color = "#2e8b57"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="#2e8b57")
                if self.selected == (i, j):
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=3)
                elif (i, j) in self.valid_moves:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="blue", width=2)

    def draw_pieces(self):
        """Draw game pieces on the board"""
        self.canvas.delete("piece")
        for i in range(self.n):
            for j in range(self.n):
                piece = self.board[i][j]
                if piece is None: continue
                x, y = j * self.cell_size, i * self.cell_size
                padding = 8
                color = "#1f1f1f" if piece.role == Role.ATTACKER else "#d9d9d9"
                if piece.role == Role.KING: color = "#cfd8dc"
                self.canvas.create_oval(x + padding, y + padding, x + self.cell_size - padding,
                                        y + self.cell_size - padding, fill=color, outline="gray", tags="piece")
                if piece.role == Role.KING:
                    self.canvas.create_text(x + self.cell_size / 2, y + self.cell_size / 2, text="♛",
                                            font=("Arial", 16), tags="piece")

    def redraw(self):
        """Update the entire canvas"""
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_pieces()

    def on_click(self, event):
        """Handle human player clicks"""
        if self.is_ai_thinking or game_state["current_turn"] != self.human_team: return
        col, row = event.x // self.cell_size, event.y // self.cell_size
        res = handle_click(row, col)
        self.board, self.selected, self.valid_moves = game_state["board"], game_state["selected"], game_state[
            "valid_moves"]
        self.turn_label.config(text=get_turn_label())
        self.redraw()
        if game_state["game_over"]:
            self.show_winner(game_state["winner"])
        elif res == "moved":
            self.root.after(200, self.ai_move)

    def ai_move(self):
        """Start AI move in a separate thread"""
        if game_state["game_over"]: return
        self.is_ai_thinking = True
        threading.Thread(target=self._compute_ai_move).start()

    def _compute_ai_move(self):
        """AI move logic and UI update"""
        move = get_best_move(game_state["board"], get_depth(), self.ai_team)
        if move:
            def apply():
                handle_click(move[0][0], move[0][1])
                handle_click(move[1][0], move[1][1])
                self.board, self.selected, self.valid_moves = game_state["board"], game_state["selected"], game_state[
                    "valid_moves"]
                self.turn_label.config(text=get_turn_label())
                self.redraw()
                self.is_ai_thinking = False
                if game_state["game_over"]: self.show_winner(game_state["winner"])

            self.root.after(0, apply)
        else:
            self.is_ai_thinking = False

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    game = GameGUI()
    game.run()