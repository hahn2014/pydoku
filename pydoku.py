import numpy as np
# Online Python - IDE, Editor, Compiler, Interpreter

def print_block_grid(grid):
    print('--GRID--')
    for block_row in range(3):
        for sub_row in range(3):
            row_parts = []
            for block_col in range(3):
                block_sub_row = ' '.join(map(str, grid[block_row, block_col, sub_row, :]))
                row_parts.append(block_sub_row)
                
            print('  '.join(row_parts))
            
        if block_row < 2:
            sample_row = '  '.join([' '.join(['9']*3)]*3)
            print(' ' * len(sample_row))
        print()

grid = np.random.randint(1,10, size=(9,9))
grid = grid.reshape(3,3,3,3)


print_block_grid(grid)
