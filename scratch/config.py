with open("src/madsnake.c", "r") as f:
    text = f.read()

# Add config global variables near the top
vars_str = """
static int cfg_speed_ms = 120;
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

# Insert before int main(void)
main_idx = text.find("int main(void)")
text = text[:main_idx] + vars_str + "\n" + text[main_idx:]

# Call load_config() inside main()
main_start = text.find("{", main_idx)
text = text[:main_start+1] + "\n    load_config();" + text[main_start+1:]

# Replace hardcoded speed_ms and max_length
text = text.replace("int speed_ms = 120;", "int speed_ms = cfg_speed_ms;")
text = text.replace("slen >= INIT_LEN * 4", "slen >= cfg_max_length")

with open("src/madsnake.c", "w") as f:
    f.write(text)
