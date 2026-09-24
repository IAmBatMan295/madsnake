with open("src/madsnake.c", "r") as f:
    text = f.read()

# Replace INIT_LEN definition
text = text.replace("#define INIT_LEN  5", "")

# Add cfg_default_length
text = text.replace(
    "static int cfg_speed_ms = 120;\nstatic int cfg_max_length = 20;",
    "static int cfg_speed_ms = 120;\nstatic int cfg_max_length = 20;\nstatic int cfg_default_length = 5;"
)

# Update load_config
old_load = """static void load_config(void)
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
}"""

new_load = """static void load_config(void)
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
        } else if (strncmp(line, "default_length=", 15) == 0) {
            cfg_default_length = atoi(line + 15);
        }
    }
    fclose(f);
    
    if (cfg_speed_ms < 10) cfg_speed_ms = 10;
    
    if (cfg_default_length < 1) {
        log_msg("Warning: default_length < 1. Clamping to 1.");
        cfg_default_length = 1;
    }
    if (cfg_max_length < cfg_default_length) {
        log_msg("Warning: max_length < default_length. Clamping max_length.");
        cfg_max_length = cfg_default_length;
    }
}"""

text = text.replace(old_load, new_load)

# Replace INIT_LEN usages
text = text.replace("slen = INIT_LEN;", "slen = cfg_default_length;")

with open("src/madsnake.c", "w") as f:
    f.write(text)
