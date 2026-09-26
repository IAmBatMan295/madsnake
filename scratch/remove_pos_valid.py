with open("src/madsnake.c", "r") as f:
    text = f.read()

start = text.find("static int pos_valid")
end = text.find("static void food_spawn")

if start != -1 and end != -1:
    text = text[:start] + text[end:]

with open("src/madsnake.c", "w") as f:
    f.write(text)
