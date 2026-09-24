import re

with open("src/madsnake.c", "r") as f:
    code = f.read()

# Change the logic in grid_init
code = re.sub(r'cell_w = COLS / 25;', 'cell_w = COLS / 40;', code)
code = re.sub(r'if \(cell_w < 12\) cell_w = 12;', 'if (cell_w < 6) cell_w = 6;', code)
code = re.sub(r'if \(cell_h < 6\) cell_h = 6;', 'if (cell_h < 3) cell_h = 3;', code)

with open("src/madsnake.c", "w") as f:
    f.write(code)
