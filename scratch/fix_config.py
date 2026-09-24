with open("src/madsnake.c", "r") as f:
    text = f.read()

# Remove the vars and function from where they are
vars_str = """static int cfg_speed_ms = 120;
static int cfg_max_length = 20;

static void load_config(void)
{
    const char *home = getenv("HOME");
    if (!home) return;
    
    char path[512];
    snprintf(path, sizeof(path), "%s/.config/madsnake/config", home);
    
    FILE *f = fopen(path, "r");
    if (!f) return;
    
    char line[256];
    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "speed_ms=", 9) == 0) {
            cfg_speed_ms = atoi(line + 9);
        } else if (strncmp(line, "max_length=", 11) == 0) {
            cfg_max_length = atoi(line + 11);
        }
    }
    fclose(f);
    
    if (cfg_speed_ms < 10) cfg_speed_ms = 10;
    if (cfg_max_length < 5) cfg_max_length = 5;
}
"""

text = text.replace(vars_str, "")

# Insert them right after the #includes
insert_idx = text.find("/* ── Grid globals")
if insert_idx == -1:
    insert_idx = text.find("/* ── Snake data")

text = text[:insert_idx] + vars_str + "\n" + text[insert_idx:]

with open("src/madsnake.c", "w") as f:
    f.write(text)
