import re

with open("src/madsnake.c", "r") as f:
    code = f.read()

# Replace assignments of sx and sy
code = re.sub(r'int sx = p\.x \* cell_w;', r'int sx = p.x * cell_w + offset_x;', code)
code = re.sub(r'int sy = p\.y \* cell_h;', r'int sy = p.y * cell_h + offset_y;', code)

code = re.sub(r'int sx = gx \* cell_w;', r'int sx = gx * cell_w + offset_x;', code)
code = re.sub(r'int sy = gy \* cell_h;', r'int sy = gy * cell_h + offset_y;', code)

code = re.sub(r'int sx = food\.x \* cell_w;', r'int sx = food.x * cell_w + offset_x;', code)
code = re.sub(r'int sy = food\.y \* cell_h;', r'int sy = food.y * cell_h + offset_y;', code)

# Also fix the log prints for food screen coordinates
code = re.sub(r'food\.x \* cell_w\)', r'food.x * cell_w + offset_x)', code)
code = re.sub(r'food\.y \* cell_h\)', r'food.y * cell_h + offset_y)', code)

with open("src/madsnake.c", "w") as f:
    f.write(code)
