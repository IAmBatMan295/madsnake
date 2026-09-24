with open("src/madsnake.c", "r") as f:
    text = f.read()

import re

# Find the getch loop
old_code = """        while ((ch = getch()) != ERR) {
            if (ch == KEY_MOUSE) {
                MEVENT me;
                if (getmouse(&me) == OK &&
                    (me.bstate & (BUTTON1_PRESSED | BUTTON2_PRESSED |
                                  BUTTON3_PRESSED | BUTTON4_PRESSED |
                                  BUTTON5_PRESSED)))
                    quit = 1;
                quit = 1;
            }
        }"""

new_code = """        while ((ch = getch()) != ERR) {
            if (ch == KEY_MOUSE) {
                MEVENT me;
                if (getmouse(&me) == OK &&
                    (me.bstate & (BUTTON1_PRESSED | BUTTON2_PRESSED |
                                  BUTTON3_PRESSED | BUTTON4_PRESSED |
                                  BUTTON5_PRESSED)))
                    quit = 1;
            } else {
                /* Any other key, including KEY_RESIZE, terminates */
                quit = 1;
            }
        }"""

if old_code in text:
    text = text.replace(old_code, new_code)
else:
    print("Could not find old code block!")

with open("src/madsnake.c", "w") as f:
    f.write(text)
