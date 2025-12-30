import numpy as np
import random
# Online Python - IDE, Editor, Compiler, Interpreter

def print_menu():
    print("---Menu Options---\n")
    print("quit/q/exit        - Exit the game")
    print("menu/print/options - Print menu options")
    print("start easy   - Begin a game in easy mode")
    print("start hard   - Begin a game in hard mode")
    print("start expert - Begin a game in expert mode")

def parse_input(prompt):
    if prompt in {'quit', 'exit', 'q'}:
        return -1
    elif prompt in {'print'}:
        return 0
    elif prompt in {'start easy', 'start 1'}:
        return 1
    elif prompt in {'start hard', 'start 2'}:
        return 2
    elif prompt in {'start expert', 'start 3'}:
        return 3
    else: return -2

def print_block_grid(grid):
    if grid.shape == (3,3,3,3):
        flat_grid = grid.reshape(9,9)
    else:
        flat_grid = grid
    
    # Top border styling
    print("              --GRID--               ")
    print("╔═══╤═══╤═══╦═══╤═══╤═══╦═══╤═══╤═══╗")
    for block_row in range(3):
        for sub_row in range(3):
            row_idx = block_row * 3 + sub_row
            row_parts = []
            
            for block_col in range(3):
                col_start = block_col * 3
                cells = []
                for col_idx in range(col_start, col_start + 3):
                    val = flat_grid[row_idx, col_idx]
                    cells.append(" ")
                    cells.append("X" if val == 0 else str(val)) # Blank for 0
                    if col_idx == 2:
                        cells.append(" ║")
                    elif col_idx == 5:
                        cells.append(" ║")
                    elif col_idx == 8:
                        cells.append(" ")
                    else:
                        cells.append(" │")
                row_parts.append("".join(cells))
            
            # Vertical block separators
            if block_row == 0 and sub_row == 0:
                left = "║"
            else:
                left = "║" if sub_row == 0 else "║"
            separator = ""
            
            line = separator.join(row_parts)
            print("║" + line + "║")
            
            # Horizontal block separators
            if row_idx == 2 or row_idx == 5:
                print("╠═══╪═══╪═══╬═══╪═══╪═══╬═══╪═══╪═══╣")
            elif row_idx == 8:
                print("╚═══╧═══╧═══╩═══╧═══╧═══╩═══╧═══╧═══╝")
            else:
                print("╟───┼───┼───╫───┼───┼───╫───┼───┼───╢")
                    
            
        
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
    
    while True:
        try:
            user_input = input("> ").strip()
            prompt = parse_input(user_input)
            print(f"input: {user_input} -> prompt: {prompt}")

            if prompt == 0: # print menu options
                print_menu()
                continue
            elif prompt == 1: # start game in easy mode
                print("Now generating easy puzzle...")
                grid = generate_puzzle(remove_count=40, seed=None) #remove count is difficulty
                print("Easy Puzzle Generated! now starting game. type and enter 'q/quit/exit at any time to exit game.\n\n")
                break
            elif prompt == 2: # start game in hard mode
                print("Now generating hard puzzle...")
                grid = generate_puzzle(remove_count=60, seed=None) #remove count is difficulty
                print("Hard Puzzle Generated! now starting game. type and enter 'q/quit/exit at any time to exit game.\n\n")
                break
            elif prompt == 3: # start game in expert mode
                print("Now generating expert puzzle...")
                grid = generate_puzzle(remove_count=70, seed=None) #remove count is difficulty
                print("Expert Puzzle Generated! now starting game. type and enter 'q/quit/exit at any time to exit game.\n\n")
                break
            elif prompt == -2: # unknown command
                print (f"Unknown command {user_input}. Please try something else")
                
            if not user_input:
                print("Empty Input - Try Again.")
                continue
            
        except KeyboardInterrupt:
            print("\n\nInterupted! Goodbye.")
            break
        except EOFError:
            print("\n\nEnd of Input. Goodbye!")
            break


if __name__ == "__main__":
    main()
