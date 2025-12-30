import numpy as np
import random
# Online Python - IDE, Editor, Compiler, Interpreter

def print_block_grid(grid):
    print('--GRID--\n')
    for block_row in range(3):
        for sub_row in range(3):
            row_parts = []
            for block_col in range(3):
                block_sub_row = ' '.join(map(str, grid[block_row, block_col, sub_row, :]))
                row_parts.append(block_sub_row)
                
            print('    '.join(row_parts))
            
        if block_row < 2:
            sample_row = '    '.join([' '.join(['9']*3)]*3)
            print(' ' * len(sample_row))
        print()
        
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

# Generate puzzle
grid = generate_puzzle(remove_count=45, seed=None)

# Print grid to screen
print_block_grid(grid)
