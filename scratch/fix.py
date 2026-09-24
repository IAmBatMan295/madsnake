with open("src/madsnake.c", "r") as f:
    text = f.read()

# First, find where the duplication starts.
# The string "static void draw_food(void)" appears twice.
first_draw_food = text.find("static void draw_food(void)")
second_draw_food = text.find("static void draw_food(void)", first_draw_food + 1)

print(f"First: {first_draw_food}, Second: {second_draw_food}")

if second_draw_food != -1:
    # the second draw_food is the old one. We need to find where it ends.
    end_of_old_draw_food = text.find("static void main_loop(void)", second_draw_food)
    
    # We want to keep everything up to first_draw_food, plus the new draw_food which is currently
    # between first_draw_food and "/* Erase a grid cell */" (the second occurrence?)
    
    # Actually, it's easier to just find the new draw_food, save it, and reconstruct the file.
    
