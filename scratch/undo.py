with open("src/madsnake.c", "r") as f:
    lines = f.readlines()

# The file was duplicated from `static void erase_cell` onwards maybe?
for i, line in enumerate(lines):
    if "redefinition of" in line:
        pass # just to think

# Actually I can just look at the duplicate functions.
# Let's find the first instance of 'static void erase_cell'
first_erase = -1
second_erase = -1
for i, line in enumerate(lines):
    if line.startswith("static void erase_cell"):
        if first_erase == -1:
            first_erase = i
        else:
            second_erase = i

if second_erase != -1:
    print(f"First erase at {first_erase}, second at {second_erase}")
    # The duplication happened because my `code[:start_idx] + new_draw_food + code[end_idx:]`
    # wait! old_draw_food_end was "/* Erase a grid cell */".
    # BUT start_idx was static void draw_food(void)
    # The first draw_food was at 479, and second draw_food was at 704!
    pass
