import numpy as np
import random
import sys
import os

# ANSI Color Codes
BLUE = "\033[94m"      # Bright blue for clues
BOLD = "\033[1m"
YELLOW_BG = "\033[103m"  # Bright yellow background for cursor on empty
RESET = "\033[0m"

# Cross-platform single key press reading
def getch():
    """Get a single character from stdin without echo, cross-platform."""
    if os.name == 'nt':  # Windows
        import msvcrt
        return msvcrt.getch().decode('utf-8', errors='ignore')
    else:  # Unix (Linux/macOS)
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
    print("---Menu Options---\n")
    print("quit/q/exit/e            - Exit the game")
    print("menu/print/options/m/p/o - Print menu options")
    print("start easy/1       - Begin a game in easy mode")
    print("start hard/2       - Begin a game in hard mode")
    print("start expert/3     - Begin a game in expert mode")

def parse_input(prompt):
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
    else: return -2

def print_block_grid(puzzle, solution=None, cursor=None):
    """
    puzzle: the initial puzzle (with 0s as empty)
    solution: current player grid (modified)
    cursor: (row, col) or None
    """
    if puzzle.shape == (3,3,3,3):
        puzzle_flat = puzzle.reshape(9,9)
        solution_flat = solution.reshape(9,9) if solution is not None else puzzle_flat
    else:
        puzzle_flat = puzzle
        solution_flat = solution if solution is not None else puzzle

    print("              --GRID--               ")
    print("╔═══╤═══╤═══╦═══╤═══╤═══╦═══╤═══╤═══╗")

    for i in range(9):
        line = "║"
        for j in range(9):
            is_clue = puzzle_flat[i, j] != 0
            val = solution_flat[i, j]
            display_char = "X" if val == 0 else str(val)
            is_cursor = cursor == (i, j)

            if is_cursor:
                if val == 0:
                    cell = f"{YELLOW_BG}{BOLD} {display_char} {RESET}"
                else:
                    cell = f"{BOLD} {display_char} {RESET}"
            elif is_clue:
                cell = f"{BLUE} {display_char} {RESET}"
            else:
                cell = f" {display_char} "

            line += cell

            if j in (2, 5):
                line += "║"
            elif j == 8:
                line += "║"
            else:
                line += "│"
        print(line)

        if i in (2, 5):
            print("╠═══╪═══╪═══╬═══╪═══╪═══╬═══╪═══╪═══╣")
        elif i == 8:
            print("╚═══╧═══╧═══╩═══╧═══╧═══╩═══╧═══╧═══╝")
        else:
            print("╟───┼───┼───╫───┼───┼───╫───┼───┼───╢")

    if cursor:
        print(f"[DEBUG] Cursor at: ({cursor[0]}, {cursor[1]})")
                    

def generate_puzzle(remove_count=45, seed=None):
    #puzzle logic to fill in blank grid
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
        
    grid = np.zeros((9,9), dtype=int)
    
    def is_valid(num, row, col):
        if num in grid[row, :]:
            return False
        if num in grid[:, col]:
            return False
        block_row, block_col = 3 * (row // 3), 3 * (col // 3)
        if num in grid[block_row:block_row+3, block_col:block_col+3]:
            return False
        return True
        
    def solve(pos=0):
        if pos == 81:
            return True
        row, col = divmod(pos, 9)
        
        nums = list(range(1, 10))
        random.shuffle(nums)
        
        for num in nums:
            if is_valid(num, row, col):
                grid[row, col] = num
                if solve(pos+1):
                    return True
                grid[row, col] = 0
        return False
    
    solve() # fill a complete valid grid
    positions = [(r, c) for r in range(9) for c in range(9)] # remove cells to create the puzzle
    random.shuffle(positions)
    for i in range(remove_count):
        r, c = positions[i]
        grid[r, c] = 0
    
    # reshape int 3x3 blocks of 3x3 integers
    puzzle = grid.reshape(3,3,3,3)
    return puzzle


def main():
    print("Welcome to Pydoku!\n")
    print_menu()
    grid = None
    # Map difficulty level (returned by parse_input) to settings
    difficulties = {
        1: {"name": "easy",   "remove_count": 35},
        2: {"name": "hard",   "remove_count": 50},
        3: {"name": "expert", "remove_count": 60}
    }
    
    while True:
        try:
            user_input = input("> ").strip().lower()
            prompt = parse_input(user_input)
            

            if prompt == 0: # print menu options
                print_menu()
                continue
            elif prompt == -1: # quit command
                print("Goodbye!")
                break
            elif prompt == -2: # unknown command
                print (f"Unknown command {user_input}. Please try something else")
                continue
            elif prompt in difficulties:  # valid difficulty: 1, 2, or 3
                settings = difficulties[int(prompt)]
                print(f"\nGenerating {settings['name'].capitalize()} puzzle...\n")
                original_puzzle = generate_puzzle(remove_count=settings['remove_count'])
                player_grid = original_puzzle.copy()
                
                cursor = [0, 0]  # mutable list
                
                print("Controls:")
                print("  j - left    l - right")
                print("  i - up      k - down")
                print("  1–9 - place number")
                print("  q - quit game\n")
                
                while True:
                    # Clear screen (works in most terminals)
                    print("\033[2J\033[H", end="")
                    
                    print_block_grid(original_puzzle, player_grid, tuple(cursor))
                    
                    print("\n> Move: j/l/i/k | Place: 1-9 | q: quit <")
                    cmd = input("> ").strip().lower()
                    
                    r, c = cursor
                    
                    if cmd == 'q':
                        print("\nThanks for playing!")
                        return
                    elif cmd == 'j':
                        cursor[1] = max(0, c - 1)
                    elif cmd == 'l':
                        cursor[1] = min(8, c + 1)
                    elif cmd == 'i':
                        cursor[0] = max(0, r - 1)
                    elif cmd == 'k':
                        cursor[0] = min(8, r + 1)
                    elif cmd in '123456789':
                        if original_puzzle.reshape(9,9)[r, c] == 0:  # Not a clue
                            player_grid.reshape(9,9)[r, c] = int(cmd)
                            print(f"Placed {cmd} at ({r},{c})")
                        else:
                            print("Cannot overwrite original clue!")
                    else:
                        print("Unknown command.")
                
                input("Press Enter to exit...")
            
            if not user_input:
                print("Empty Input - Try Again.")
                continue
            
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            return


if __name__ == "__main__":
    main()
