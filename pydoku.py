import numpy as np
import random
import sys
import os

# ANSI Color Codes
BLUE = "\033[94m"      # Bright blue for clues
RED = "\033[91m"        # Invalid player entries
BOLD = "\033[1m"
YELLOW_BG = "\033[103m"  # Bright yellow background for cursor
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
    print("\033[2J\033[H", end="") # Clear screen and redraw
    print("Welcome to Pydoku!\n")
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
    
def cell_has_conflict(player_flat, row, col):
    """Return True if the number in this cell conflicts with any other cell."""
    num = player_flat[row, col]
    if num == 0:
        return False
    
    # Row conflict
    if np.count_nonzero(player_flat[row, :] == num) > 1:
        return True
    # Column conflict
    if np.count_nonzero(player_flat[:, col] == num) > 1:
        return True
    # Block conflict
    br, bc = 3 * (row // 3), 3 * (col // 3)
    if np.count_nonzero(player_flat[br:br+3, bc:bc+3] == num) > 1:
        return True
    return False

def print_block_grid(original_puzzle, player_grid, solution, cursor=None, difficulty_name="GRID"):
    puzzle_flat = original_puzzle.reshape(9, 9)
    player_flat = player_grid.reshape(9, 9)
    solution_flat = solution.reshape(9, 9)

    print(f"              --{difficulty_name.upper()}--               ")
    print("╔═══╤═══╤═══╦═══╤═══╤═══╦═══╤═══╤═══╗")

    for i in range(9):
        line = "║"
        for j in range(9):
            is_clue = puzzle_flat[i, j] != 0
            val = player_flat[i, j]
            content = "   " if val == 0 else f" {val} "
            is_cursor = cursor == (i, j)

            if is_cursor:
                # Cursor always gets strong yellow highlight
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
    
    solve()  # Fill complete solution
    solution = grid.copy()
    
    positions = [(r,c) for r in range(9) for c in range(9)]
    random.shuffle(positions)
    for r, c in positions[:remove_count]:
        grid[r, c] = 0
    
    return grid.reshape(3,3,3,3), solution.reshape(3,3,3,3)

def play_sudoku(settings):
    print(f"\nGenerating {settings['name'].capitalize()} puzzle...\n")
    original_puzzle, solution = generate_puzzle(remove_count=settings['remove_count'])
    player_grid = original_puzzle.copy()
    difficulty_name = settings['name'].capitalize()
    
    cursor_row, cursor_col = 0, 0
    raw_mode = sys.stdin.isatty()
    status = None  # For fallback mode messages
    
    # Initial instructions (shown once)
    print("\033[2J\033[H", end="")  # Clear screen
    if raw_mode:
        print("Arrow keys to move | 1-9 to place | 0 to clear | q to quit to menu")
    else:
        print("j/left k/down i/up l/right | 1-i9 place | 0 clear | q quit to menu")
    print("Invalid entries will appear in red.\n")
    input("Press Enter to start...")
    
    while True:
        print("\033[2J\033[H", end="")
        print_block_grid(original_puzzle, player_grid, solution,
                         cursor=(cursor_row, cursor_col), difficulty_name=difficulty_name)
        
        # Display status message if any (fallback mode only)
        if not raw_mode and status is not None:
            print(f"\n{status}")
        
        # Check for win
        if np.array_equal(player_grid.reshape(9,9), solution.reshape(9,9)):
            print("\n" + "="*40)
            print("       You have solved the puzzle!")
            print("="*40)
            choice = input("\nPress 'q' to quit the game or any other key to return to main menu: ").strip().lower()
            if choice == 'q':
                print("\nThanks for playing Pydoku!")
                sys.exit(0)
            else:
                return  # Back to main menu
        
        # Input handling
        if raw_mode:
            key = getch()
            if key == 'q':
                return
            elif key in '1234567890':
                num = 0 if key == '0' else int(key)
                if original_puzzle.reshape(9,9)[cursor_row, cursor_col] == 0:  # Editable cell
                    player_grid.reshape(9,9)[cursor_row, cursor_col] = num
            elif key == '\x1b' or key == '\033':  # Escape sequence (arrow keys)
                # Read the rest of the sequence
                try:
                    seq1 = getch()
                    seq2 = getch()
                    arrow = key + seq1 + seq2
                    if arrow == '\x1b[A' or arrow == '\033[A':
                        cursor_row = max(0, cursor_row - 1)
                    elif arrow == '\x1b[B' or arrow == '\033[B':
                        cursor_row = min(8, cursor_row + 1)
                    elif arrow == '\x1b[C' or arrow == '\033[C':
                        cursor_col = min(8, cursor_col + 1)
                    elif arrow == '\x1b[D' or arrow == '\033[D':
                        cursor_col = max(0, cursor_col - 1)
                except:
                    pass  # Incomplete sequence - ignore
        else:
            # Fallback mode with status messages
            try:
                cmd = input("\n> ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                return
            
            status = None  # Clear previous status
            
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
            elif cmd in '1234567890':
                num = 0 if cmd == '0' else int(cmd)
                if original_puzzle.reshape(9,9)[cursor_row, cursor_col] == 0:
                    player_grid.reshape(9,9)[cursor_row, cursor_col] = num
            else:
                status = f"\033[1;31mUnknown command: {cmd}\033[0m"

def main():
    difficulties = {
        1: {"name": "easy",   "remove_count": 35},
        2: {"name": "hard",   "remove_count": 50},
        3: {"name": "expert", "remove_count": 60}
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
                print("\nGoodbye!")
                return
            elif prompt == -2:
                print(f"Unknown command: {user_input!r}. Type 'menu' for options.")
                continue
            elif prompt in difficulties:
                play_sudoku(difficulties[prompt])
                # After returning from game, loop back to menu prompt
            
            if not user_input:
                print("Empty input - try again.")
                
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            return


if __name__ == "__main__":
    main()
