with open("src/madsnake.c", "rb") as f:
    code = f.read()

code = code.replace(b"L'\x00'", b"L'\\0'")

with open("src/madsnake.c", "wb") as f:
    f.write(code)
