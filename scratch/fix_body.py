import re

with open("src/madsnake.c", "r") as f:
    code = f.read()

# Replace fill_interior(sx, sy); in draw_body
# We will insert fill_block(sx, sy); right after int vert = ...
def repl1(m):
    return m.group(1) + "\n    /* Fill background first */\n    fill_block(sx, sy);\n\n    attron(COLOR_PAIR(PAIR_SNAKE));"

code = re.sub(r'(int vert  = \(from_dx == 0 && to_dx == 0\);)\n\n    attron\(COLOR_PAIR\(PAIR_SNAKE\)\);', repl1, code)

# Remove the fill_interior at the end of draw_body
code = re.sub(r'    attroff\(COLOR_PAIR\(PAIR_SNAKE\)\);\n\n    /\* Checker fill interior \*/\n    fill_interior\(sx, sy\);', r'    attroff(COLOR_PAIR(PAIR_SNAKE));', code)

# Replace ' ' with nothing (just skip drawing the border where we opened it? 
# NO! The border was ALREADY drawn, so if we open a side we just replace it with the solid fill color `\u2588`! Wait, if we use space, it draws black. If we draw nothing, it leaves the border!
# But if we draw the fill color, it requires setting the cchar_t.
# Wait, why did I draw a full box and then "open" it? That's terribly inefficient.
# Let's just redraw the corner code completely in the script!
