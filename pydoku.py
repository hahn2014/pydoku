import numpy as np
import random
# Online Python - IDE, Editor, Compiler, Interpreter

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
    print("Now generating puzzle...")
    grid = generate_puzzle(remove_count=45, seed=None) #remove count is difficulty
    
    print("Puzzle Generated! now starting game. type and enter 'q/quit/exit at any time to exit game.\n\n")
    while True:
        try:
            user_input = input("> ").strip()
            
            if user_input.lower() in {'quit', 'exit', 'q'}:
                print("User called system exit. Goodbye!")
                break
            if not user_input:
                print("Empty Input - Try Again.")
                continue
            
            print(f"Echo: {user_input.upper()}")
            
        except KeyboardInterrupt:
            print("\n\nInterupted! Goodbye.")
            break
        except EOFError:
            print("\n\nEnd of Input. Goodbye!")
            break


if __name__ == "__main__":
    main()
