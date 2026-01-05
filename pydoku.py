#!/usr/bin/env python3.13
import numpy as np
import random
import time
import math
import sys
import os
from datetime import datetime

# ANSI Color Codes
BLUE = "\033[94m"  # Bright blue for clues
RED = "\033[91m"   # Invalid player entries
BOLD = "\033[1m"
YELLOW_BG = "\033[103m"  # Bright yellow background for cursor
RESET = "\033[0m"

# Cross-platform single key press reading
def getch():
    if os.name == 'nt':
        import msvcrt
        return msvcrt.getch().decode('utf-8', errors='ignore')
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def print_menu():
    print("\033[2J\033[H", end="")
    print("Welcome to Pydoku! (CLI Mode)\n")
    print("---Menu Options---\n")
    print("quit/q/exit/e - Exit the game")
    print("menu/print/options/m/p/o - Print menu options")
    print("start easy/1 - Begin a game in easy mode")
    print("start hard/2 - Begin a game in hard mode")
    print("start expert/3 - Begin a game in expert mode")
    print("start torture/4 - Begin a game in torture mode")

def parse_input(prompt):
    prompt = prompt.strip().lower()
    if prompt in {'quit', 'exit', 'q', 'e'}:
        return -1
    elif prompt in {'print', 'menu', 'options', 'p', 'm', 'o'}:
        return 0
    elif prompt in {'start easy', '1'}:
        return 1
    elif prompt in {'start hard', '2'}:
        return 2
    elif prompt in {'start expert', '3'}:
        return 3
    elif prompt in {'start torture', '4'}:
        return 4
    else:
        return -2

def cell_has_conflict(player_flat, row, col):
    num = player_flat[row, col]
    if num == 0:
        return False
    if np.count_nonzero(player_flat[row, :] == num) > 1:
        return True
    if np.count_nonzero(player_flat[:, col] == num) > 1:
        return True
    br, bc = 3 * (row // 3), 3 * (col // 3)
    if np.count_nonzero(player_flat[br:br+3, bc:bc+3] == num) > 1:
        return True
    return False

def get_candidates(board, r, c):
    """Return set of possible numbers for empty cell (r,c) on current board."""
    if board[r, c] != 0:
        return set()
    possible = set(range(1, 10))
    possible -= set(board[r, :])
    possible -= set(board[:, c])
    br, bc = 3 * (r // 3), 3 * (c // 3)
    possible -= set(board[br:br+3, bc:bc+3].flatten())
    return possible

def print_block_grid(original_puzzle, player_grid, solution, cursor=None, difficulty_name="GRID"):
    puzzle_flat = original_puzzle.reshape(9, 9)
    player_flat = player_grid.reshape(9, 9)
    print(f" --{difficulty_name.upper()}-- ")
    print("╔═══╤═══╤═══╦═══╤═══╤═══╦═══╤═══╤═══╗")
    for i in range(9):
        line = "║"
        for j in range(9):
            is_clue = puzzle_flat[i, j] != 0
            val = player_flat[i, j]
            content = "   " if val == 0 else f" {val} "
            is_cursor = cursor == (i, j)
            if is_cursor:
                cell = f"{YELLOW_BG}{BOLD}{content}{RESET}"
            elif is_clue:
                cell = f"{BLUE}{content}{RESET}"
            elif val != 0 and cell_has_conflict(player_flat, i, j):
                cell = f"{RED}{content}{RESET}"
            else:
                cell = content
            line += cell
            line += "║" if j % 3 == 2 else "│"
        print(line)
        if i in (2, 5):
            print("╠═══╪═══╪═══╬═══╪═══╪═══╬═══╪═══╪═══╣")
        elif i == 8:
            print("╚═══╧═══╧═══╩═══╧═══╧═══╩═══╧═══╧═══╝")
        else:
            print("╟───┼───┼───╫───┼───┼───╫───┼───┼───╢")

def generate_puzzle(remove_count=45, seed=None):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    grid = np.zeros((9,9), dtype=int)

    def is_valid(num, row, col):
        if num in grid[row, :]: return False
        if num in grid[:, col]: return False
        br, bc = 3*(row//3), 3*(col//3)
        if num in grid[br:br+3, bc:bc+3]: return False
        return True

    def solve(pos=0):
        if pos == 81: return True
        row, col = divmod(pos, 9)
        nums = list(range(1,10))
        random.shuffle(nums)
        for num in nums:
            if is_valid(num, row, col):
                grid[row, col] = num
                if solve(pos+1): return True
                grid[row, col] = 0
        return False

    solve()
    solution = grid.copy()

    positions = [(r,c) for r in range(9) for c in range(9)]
    random.shuffle(positions)
    for r, c in positions[:remove_count]:
        grid[r, c] = 0

    return grid.reshape(3,3,3,3), solution.reshape(3,3,3,3)

def play_sudoku_cli(settings):
    print(f"\nGenerating {settings['name'].capitalize()} puzzle...\n")
    original_puzzle, solution = generate_puzzle(remove_count=settings['remove_count'])
    player_grid = original_puzzle.copy()
    difficulty_name = settings['name'].capitalize()

    cursor_row, cursor_col = 0, 0
    raw_mode = sys.stdin.isatty()
    status = None

    print("\033[2J\033[H", end="")
    if raw_mode:
        print("Arrow keys to move | 1-9 to place | 0 to clear | q to quit to menu")
    else:
        print("j = left | l = right | i = up | k = down")
        print("1-9 to place | 0 to clear | q to quit to menu")
    print("Invalid entries will appear in red.\n")
    input("Press Enter to start...")

    while True:
        print("\033[2J\033[H", end="")
        print_block_grid(original_puzzle, player_grid, solution,
                         cursor=(cursor_row, cursor_col), difficulty_name=difficulty_name)

        if not raw_mode and status is not None:
            print(f"\n{status}")

        if np.array_equal(player_grid.reshape(9,9), solution.reshape(9,9)):
            print("\n" + "="*40)
            print("       🎉 CONGRATULATIONS! 🎉")
            print("       You have solved the puzzle!")
            print("="*40)
            choice = input("\nPress 'q' to quit the game or any other key to return to main menu: ").strip().lower()
            if choice == 'q':
                print("\nThanks for playing Pydoku!")
                sys.exit(0)
            else:
                return

        if raw_mode:
            key = getch()
            if not key:
                continue
            if key == 'q':
                return
            elif key in '0123456789':
                num = int(key)
                if original_puzzle.reshape(9,9)[cursor_row, cursor_col] == 0:
                    player_grid.reshape(9,9)[cursor_row, cursor_col] = num
            elif key in {'\x1b', '\033'}:
                try:
                    seq1 = getch()
                    seq2 = getch()
                    arrow = key + seq1 + seq2
                    if arrow in {'\x1b[A', '\033[A'}:
                        cursor_row = max(0, cursor_row - 1)
                    elif arrow in {'\x1b[B', '\033[B'}:
                        cursor_row = min(8, cursor_row + 1)
                    elif arrow in {'\x1b[C', '\033[C'}:
                        cursor_col = min(8, cursor_col + 1)
                    elif arrow in {'\x1b[D', '\033[D'}:
                        cursor_col = max(0, cursor_col - 1)
                except:
                    pass
        else:
            try:
                cmd = input("\n> ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                return

            status = None
            if not cmd:
                status = "\033[1;33mEmpty input - please enter a command.\033[0m"
                continue
            if cmd == 'q':
                return
            elif cmd == 'j':
                cursor_col = max(0, cursor_col - 1)
            elif cmd == 'l':
                cursor_col = min(8, cursor_col + 1)
            elif cmd == 'i':
                cursor_row = max(0, cursor_row - 1)
            elif cmd == 'k':
                cursor_row = min(8, cursor_row + 1)
            elif cmd in '0123456789':
                num = int(cmd)
                if original_puzzle.reshape(9,9)[cursor_row, cursor_col] == 0:
                    player_grid.reshape(9,9)[cursor_row, cursor_col] = num
            else:
                status = f"\033[1;31mUnknown command: {cmd}\033[0m"

def cli_main():
    difficulties = {
        1: {"name": "easy", "remove_count": 25},
        2: {"name": "hard", "remove_count": 40},
        3: {"name": "expert", "remove_count": 50},
        4: {"name": "torture", "remove_count": 65}
    }

    while True:
        print_menu()
        try:
            user_input = input("> ").strip().lower()
            prompt = parse_input(user_input)
            if prompt == 0:
                print_menu()
                continue
            elif prompt == -1:
                print("\nNow returning to main menu. Goodbye!")
                return
            elif prompt == -2:
                print(f"Unknown command: {user_input!r}. Type 'menu' for options.")
                continue
            elif prompt in difficulties:
                play_sudoku_cli(difficulties[prompt])

            if not user_input:
                print("Empty input - try again.")

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            return

def launch_gui():
    try:
        import tkinter as tk
        from tkinter import messagebox, simpledialog, Toplevel, Text
    except ImportError:
        print("\n" + "="*60)
        print("Tkinter is not available in this environment.")
        print("Automatically falling back to CLI mode...")
        print("="*60 + "\n")
        cli_main()
        return

    class SudokuGUI(tk.Tk):
        DARK_BG = "#000000"  # Furthest background
        MID_BG = "#1e1e1e"  # Mid-ground
        CANVAS_BG = "#121212"  # Grid background
        GRID_THIN = "#404040"  # Thin grid lines
        GRID_THICK = "#606060"  # Thick grid lines
        CLUE_COLOR = "#a9a9a9"  # Lightish dark gray for clues
        CORRECT_COLOR = "#ffffff"  # White for correct user
        INCORRECT_COLOR = "#ff0000"  # Bright red
        HIGHLIGHT_CURSOR = "#606060" # Cursor cell highlight
        HIGHLIGHT_ANSWER = "#e67e22"  # Darker orange for answer mode
        HIGHLIGHT_NOTES = "#4a90e2"  # Blue for notes mode
        HIGHLIGHT_ALIGN = "#4c9c61" # Blue for alignment rows/columns/blocks
        PENCIL_COLOR = "#808080"  # Lighter gray for notes
        REMAINING_COLOR = "#1b3de3" # Darker blue for the remaining numbers
        BUTTON_BG = "#333333"  # Dark gray buttons
        BUTTON_FG = "#878787"  # Lighter text
        TEXT_GRAY = "#d3d3d3"  # Bright gray for labels

        def __init__(self):
            super().__init__()
            self.title("Pydoku - GUI Mode")
            self.resizable(False, False)

            self.difficulties = ["Easy", "Hard", "Expert", "Torture"]
            self.remove_counts = {"Easy": 25, "Hard": 40, "Expert": 50, "Torture": 65}
            self.multipliers = {"Easy": 1, "Hard": 2, "Expert": 3, "Torture": 4}

            # Menu frame (initial screen)
            self.menu_frame = tk.Frame(self, bg=self.DARK_BG)
            self.menu_frame.pack(expand=True, fill="both")

            tk.Label(self.menu_frame, text="PYDOKU", font=("Arial", 82, "bold"), bg=self.DARK_BG, fg=self.HIGHLIGHT_NOTES).pack(pady=50)
            tk.Label(self.menu_frame, text="Select Difficulty", font=("Arial", 24), bg=self.DARK_BG, fg=self.TEXT_GRAY).pack(pady=20)

            for diff in self.difficulties:
                btn = tk.Button(self.menu_frame, text=diff, font=("Arial", 18), width=15, height=2, bg=self.MID_BG,
                                fg=self.BUTTON_FG, command=lambda d=diff: self.start_game(d))
                btn.pack(pady=10)

            tk.Button(self.menu_frame, text="View Leaderboards", font=("Arial", 16), width=20, bg=self.MID_BG,
                      fg=self.BUTTON_FG, command=self.show_leaderboard).pack(pady=30)

            tk.Button(self.menu_frame, text="Return to CLI", font=("Arial", 16), width=20, bg=self.MID_BG, fg=self.BUTTON_FG,
                      command=self.stop_ui).pack(pady=30)

            # Game frame (hidden initially)
            self.game_frame = tk.Frame(self, bg=self.DARK_BG)
            self.build_game_ui()

        def stop_ui(self):
            self.menu_frame.destroy()
            self.destroy()
            mode_selection()

        def build_game_ui(self):
            main_frame = tk.Frame(self.game_frame, bg=self.DARK_BG)
            main_frame.pack(padx=20, pady=20)

            # Left sidebar
            left_frame = tk.Frame(main_frame, bg=self.DARK_BG)
            left_frame.pack(side="left", padx=(0, 40))

            tk.Label(left_frame, text="Remaining", font=("Arial", 14, "bold"), bg=self.DARK_BG, fg=self.TEXT_GRAY).pack(pady=(0, 10))
            self.number_labels = {}
            for num in range(1, 10):
                lbl = tk.Label(left_frame, text=str(num), font=("Arial", 48, "bold"),
                               fg=self.REMAINING_COLOR, width=2, bg=self.DARK_BG)
                lbl.pack(pady=6)
                self.number_labels[num] = lbl

            # Right side
            right_frame = tk.Frame(main_frame, bg=self.DARK_BG)
            right_frame.pack(side="left")

            # Top controls
            control_frame = tk.Frame(right_frame, bg=self.DARK_BG)
            control_frame.pack(pady=(0, 15))

            self.timer_label = tk.Label(control_frame, text="Time: 00:00", font=("Arial", 14), bg=self.DARK_BG, fg="#ffffff")
            self.timer_label.pack(side="right", padx=20)

            self.hint_button = tk.Button(control_frame, text="Hint", font=("Arial", 12, "bold"), bg=self.BUTTON_BG,
                                         fg=self.BUTTON_FG, command=self.give_hint)
            self.hint_button.pack(side="right", padx=10)

            self.pause_button = tk.Button(control_frame, text="Pause", font=("Arial", 12, "bold"), bg=self.BUTTON_BG,
                                         fg=self.BUTTON_FG, command=self.toggle_pause)
            self.pause_button.pack(side="right", padx=10)

            self.notes_button = tk.Button(control_frame, text="Answer Mode (N)", font=("Arial", 12, "bold"), bg=self.BUTTON_BG,
                                         fg=self.BUTTON_FG, command=self.toggle_notes)
            self.notes_button.pack(side="right", padx=10)

            tk.Button(control_frame, text="Leaderboards", font=("Arial", 12, "bold"), bg=self.BUTTON_BG, fg=self.BUTTON_FG,
                      command=self.show_leaderboard).pack(side="right", padx=10)

            tk.Button(control_frame, text="Main Menu", font=("Arial", 12, "bold"), bg=self.BUTTON_BG, fg=self.BUTTON_FG,
                      command=self.back_to_menu).pack(side="right", padx=10)

            # Canvas
            self.cell_size = 60
            canvas_frame = tk.Frame(right_frame)
            canvas_frame.pack()
            self.canvas = tk.Canvas(canvas_frame, width=9*self.cell_size, height=9*self.cell_size,
                                    bg=self.CANVAS_BG, highlightthickness=0)
            self.canvas.pack()

            # Paused label (hidden initially)
            self.paused_label = tk.Label(canvas_frame, text="PAUSED", font=("Arial", 48, "bold"),
                                         fg=self.INCORRECT_COLOR, bg=self.MID_BG)

            # Bottom status
            bottom_frame = tk.Frame(right_frame)
            bottom_frame.pack(pady=15)
            self.score_label = tk.Label(bottom_frame, text="Score: 0", font=("Arial", 16, "bold"))
            self.score_label.pack(side="left", padx=30)
            self.mistakes_label = tk.Label(bottom_frame, text="Mistakes: 0", font=("Arial", 16))
            self.mistakes_label.pack(side="left", padx=30)

            self.canvas.bind("<Button-1>", self.on_cell_click)
            self.bind_all("<Key>", self.on_key_press)

        def start_game(self, diff_name):
            self.current_diff = diff_name
            self.menu_frame.pack_forget()
            self.game_frame.pack(expand=True, fill="both")
            self.new_game(diff_name)

        def back_to_menu(self):
            self.game_frame.pack_forget()
            self.menu_frame.pack(expand=True, fill="both")

        def toggle_pause(self):
            self.paused = not self.paused
            text = "Resume" if self.paused else "Pause"
            self.pause_button.config(text=text)
            if self.paused:
                self.canvas.pack_forget()
                self.paused_label.pack(expand=True, fill="both")
            else:
                self.paused_label.pack_forget()
                self.canvas.pack()

        def toggle_notes(self):
            self.notes_mode = not self.notes_mode
            if self.notes_mode:
                self.notes_button.config(text="NOTES MODE (N)", bg=self.HIGHLIGHT_ALIGN, font=("Arial", 14, "bold"))
            else:
                self.notes_button.config(text="Answer Mode (N)", bg=self.BUTTON_BG, font=("Arial", 12))

        def update_timer(self):
            if hasattr(self, 'timer_running') and self.timer_running and not self.paused:
                elapsed = int(time.time() - self.start_time)
                m, s = divmod(elapsed, 60)
                self.timer_label.config(text=f"Time: {m:02d}:{s:02d}")
            self.after(1000, self.update_timer)

        def update_remaining(self):
            for num in range(1, 10):
                placed_correct = sum(1 for r in range(9) for c in range(9)
                                     if self.player[r, c] == num and self.solution[r, c] == num)
                color = "gray" if placed_correct == 9 else self.REMAINING_COLOR
                self.number_labels[num].config(fg=color)

        def draw_grid(self):
            self.canvas.delete("grid")
            for i in range(10):
                width = 5 if i % 3 == 0 else 1
                fill_color = self.GRID_THICK if i % 3 == 0 else self.GRID_THIN
                self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size, 9 * self.cell_size, fill=fill_color,
                                        width=width, tags="grid")
                self.canvas.create_line(0, i * self.cell_size, 9 * self.cell_size, i * self.cell_size, fill=fill_color,
                                        width=width, tags="grid")

        def draw_numbers(self):
            self.canvas.delete("numbers")
            for r in range(9):
                for c in range(9):
                    val = self.player[r, c]
                    if val != 0:
                        color = self.CLUE_COLOR if self.original[r, c] != 0 else \
                            (self.INCORRECT_COLOR if cell_has_conflict(self.player, r, c) else self.CORRECT_COLOR)
                        x = c * self.cell_size + self.cell_size // 2
                        y = r * self.cell_size + self.cell_size // 2
                        self.canvas.create_text(x, y, text=str(val), tags="numbers",
                                                fill=color, font=("Arial", 32, "bold"))
                    # Pencil marks (only on empty cells)
                    if val == 0 and self.notes[r][c]:
                        for note in sorted(self.notes[r][c]):
                            mini_r = (note - 1) // 3
                            mini_c = (note - 1) % 3
                            offset_x = 12 + mini_c * 16
                            offset_y = 16 + mini_r * 16
                            x = c * self.cell_size + offset_x
                            y = r * self.cell_size + offset_y
                            self.canvas.create_text(x, y, text=str(note), tags="numbers",
                                                    fill=self.PENCIL_COLOR, font=("Arial", 12))

        def highlight_selected(self):
            self.canvas.delete("highlight")
            r, c = self.selected
            outline_color = self.HIGHLIGHT_ANSWER if not self.notes_mode else self.HIGHLIGHT_NOTES
            self.canvas.create_rectangle(
                c * self.cell_size + 4, r * self.cell_size + 4,
                (c + 1) * self.cell_size - 4, (r + 1) * self.cell_size - 4,
                outline=outline_color, width=4, tags="highlight"
            )
            self.highlight_directionals()

        def highlight_directionals(self):
            self.canvas.delete("highlight_directionals")
            r, c = self.selected
            block_y = math.floor((r/9)*3)
            block_x = math.floor((c/9)*3)
            block_top = 0 + (block_y * (self.cell_size * 3))
            block_bottom = block_top + (self.cell_size * 3)
            block_left = 0 + (block_x * (self.cell_size * 3))
            block_right = block_left + (self.cell_size * 3)

            # Horizontal Line
            self.canvas.create_rectangle(
                0, r * self.cell_size + 4,
                9 * self.cell_size, (r + 1) * self.cell_size - 4,
                fill=self.HIGHLIGHT_ALIGN, width=4, tags="highlight_directionals"
            )
            # Vertical Line
            self.canvas.create_rectangle(
                c * self.cell_size + 4, 0,
                (c + 1) * self.cell_size - 4, 9 * self.cell_size,
                fill=self.HIGHLIGHT_ALIGN, width=4, tags="highlight_directionals"
            )
            # Block
            self.canvas.create_rectangle(
                block_left, block_top, block_right, block_bottom,
                fill=self.HIGHLIGHT_ALIGN, width=4, tags="highlight_directionals"
            )
            self.canvas.tag_lower("highlight_directionals")


        def new_game(self, diff_name):
            remove_count = self.remove_counts[diff_name]
            orig_flat, sol_flat = generate_puzzle(remove_count=remove_count)
            self.original = orig_flat.reshape(9, 9)
            self.solution = sol_flat.reshape(9, 9)
            self.player = self.original.copy()

            self.start_time = time.time()
            self.timer_running = True
            self.paused = False
            self.pause_button.config(text="Pause")
            if hasattr(self, 'paused_label'):
                self.paused_label.pack_forget()
            self.canvas.pack()

            self.score = 0
            self.score_label.config(text="Score: 0")
            self.mistakes = 0
            self.mistakes_label.config(text="Mistakes: 0")
            self.hinted = set()
            self.notes_mode = False
            self.toggle_notes()  # Force update button to Answer Mode
            self.toggle_notes()  # Back to off (ensures correct style)
            self.notes = [[set() for _ in range(9)] for _ in range(9)]

            self.selected = (0, 0)
            self.draw_grid()
            self.highlight_selected()
            self.highlight_directionals()
            self.draw_numbers()
            self.update_remaining()

        def give_hint(self):
            empties = [(r, c) for r in range(9) for c in range(9) if self.player[r, c] == 0]
            if not empties:
                messagebox.showinfo("Hint", "No empty cells left!")
                return
            r, c = random.choice(empties)
            correct = self.solution[r, c]
            self.player[r, c] = correct
            self.hinted.add((r, c))
            self.draw_numbers()
            self.update_remaining()
            self.check_win()

        def on_cell_click(self, event):
            if self.paused:
                return
            c = event.x // self.cell_size
            r = event.y // self.cell_size
            if 0 <= r < 9 and 0 <= c < 9:
                self.selected = (r, c)
                self.highlight_selected()

        def on_key_press(self, event):
            if self.paused:
                return

            if event.char.lower() == 'n':
                self.toggle_notes()
                return

            r, c = self.selected
            changed = False

            if event.keysym in {"Left", "Right", "Up", "Down"}:
                if event.keysym == "Left":
                    c = max(0, c - 1)
                elif event.keysym == "Right":
                    c = min(8, c + 1)
                elif event.keysym == "Up":
                    r = max(0, r - 1)
                elif event.keysym == "Down":
                    r = min(8, r + 1)
            else:
                if event.char in "123456789":
                    num = int(event.char)
                    if not self.notes_mode:
                        if self.original[r, c] == 0:
                            old_conflict = cell_has_conflict(self.player, r, c)
                            candidates = len(get_candidates(self.player, r, c))
                            is_correct = num == self.solution[r, c]
                            self.player[r, c] = num
                            new_conflict = cell_has_conflict(self.player, r, c)
                            if new_conflict and not old_conflict:
                                self.mistakes += 1
                                self.mistakes_label.config(text=f"Mistakes: {self.mistakes}")
                            if is_correct and (r, c) not in self.hinted:
                                points = 100 * (9 - candidates + 1) * self.multipliers[self.current_diff]
                                self.score += points
                                self.score_label.config(text=f"Score: {self.score}")
                            changed = True
                    else:
                        if self.player[r, c] == 0:
                            if num in self.notes[r][c]:
                                self.notes[r][c].remove(num)
                            else:
                                self.notes[r][c].add(num)
                            changed = True
                elif event.keysym in {"Delete", "BackSpace", "0"}:
                    if not self.notes_mode:
                        if self.original[r, c] == 0:
                            old_conflict = cell_has_conflict(self.player, r, c)
                            self.player[r, c] = 0
                            if old_conflict and not cell_has_conflict(self.player, r, c):
                                self.mistakes = max(0, self.mistakes - 1)
                                self.mistakes_label.config(text=f"Mistakes: {self.mistakes}")
                            changed = True
                    else:
                        if self.player[r, c] == 0:
                            self.notes[r][c].clear()
                            changed = True

            self.selected = (r, c)
            self.highlight_selected()
            self.highlight_directionals()
            if changed:
                self.draw_numbers()
                self.update_remaining()
                self.check_win()

        def check_win(self):
            if np.array_equal(self.player, self.solution):
                self.timer_running = False
                elapsed = int(time.time() - self.start_time)
                m, s = divmod(elapsed, 60)
                timestr = f"{m:02d}:{s:02d}"
                messagebox.showinfo("🎉 Congratulations!",
                                    f"You solved the puzzle in {timestr}!\nFinal Score: {self.score}")

                nickname = simpledialog.askstring("Leaderboard", "Enter nickname (max 8 chars):",
                                                  parent=self)
                if nickname:
                    nickname = nickname[:8]
                    date = datetime.now().strftime("%Y-%m-%d %H:%M")
                    line = f"{nickname}|{self.score}|{timestr}|{date}|{self.current_diff}\n"
                    with open("leaderboards.txt", "a") as f:
                        f.write(line)

        def show_leaderboard(self):
            top = Toplevel(self)
            top.title("Leaderboards")
            top.resizable(False, False)

            text = Text(top, font=("Courier", 12), width=70, height=20)
            text.pack(padx=10, pady=10)

            entries = []
            if os.path.exists("leaderboards.txt"):
                with open("leaderboards.txt") as f:
                    for line in f:
                        parts = line.strip().split("|")
                        if len(parts) == 5:
                            nick, score, t, date, diff = parts
                            entries.append((int(score), nick, t, date, diff))

            if not entries:
                text.insert("end", "No entries yet!")
            else:
                entries.sort(reverse=True)
                header = f"{'Rank':<6}{'Score':<10}{'Nickname':<12}{'Time':<10}{'Date':<18}{'Difficulty'}\n"
                header += "-" * 70 + "\n"
                text.insert("end", header)
                for rank, (score, nick, t, date, diff) in enumerate(entries, 1):
                    line = f"{rank:<6}{score:<10}{nick:<12}{t:<10}{date:<18}{diff}\n"
                    text.insert("end", line)

            text.config(state="disabled")

    app = SudokuGUI()
    app.update_timer()
    app.mainloop()

def mode_selection():
    while True:
        print("\033[2J\033[H", end="")
        print("="*55)
        print("               Welcome to Pydoku!")
        print("="*55)
        print()
        print("1 - CLI Mode      (Terminal - works everywhere)")
        print("2 - GUI Mode      (Graphical - requires local run)")
        print("q - Quit")
        print()

        choice = input("> ").strip().lower()

        if choice in {'1', 'cli'}:
            cli_main()
        elif choice in {'2', 'gui'}:
            launch_gui()
        elif choice in {'q', 'quit', 'exit'}:
            print("\nThanks for playing! Goodbye!\n")
            return
        else:
            print("\nInvalid choice.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    args = sys.argv[1:]
    args_counted = False

    if args and not args_counted:
        if '-g' in args or '--gui' in args:
            launch_gui()
            args_counted = True
        elif '-c' in args or '--cli' in args:
            cli_main()
            args_counted = True
        else:
            print("Usage: python pydoku.py [-c | --cli | -g | --gui]")
            sys.exit(1)
    else:
        mode_selection()