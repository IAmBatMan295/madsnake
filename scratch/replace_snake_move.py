import re

with open("src/madsnake.c", "r") as f:
    text = f.read()

start_idx = text.find("static void snake_move(void)")
end_idx = text.find("/* ── Drawing", start_idx)

if start_idx == -1 or end_idx == -1:
    print("Could not find blocks")
    exit(1)

new_move = """static void snake_move(void)
{
    Pt head = snake_at(slen - 1);
    
    int best_dir = -1;
    int min_food_dist = MAX_GRID;
    int max_tail_dist = -1;
    
    for (int i = 0; i < 4; i++) {
        /* Evaluate directions in order: forward, right, left, back relative to current sdir
           to avoid erratic zigzagging when multiple paths have same distance */
        int d = (sdir + ((i == 0) ? 0 : (i == 1) ? 1 : (i == 2) ? 3 : 2)) % 4;
        
        int nx = head.x + DX[d];
        int ny = head.y + DY[d];
        
        int ate_food = (nx == food.x && ny == food.y);
        /* If we eat food, length increases, so tail stays at index 0. 
           If we don't, tail moves out, so index 0 becomes empty. */
        int ignore_tail = ate_food ? 0 : 1; 

        if (is_body(nx, ny, ignore_tail)) continue;
        
        Pt next = {nx, ny};
        int d_food = bfs_dist(next, food, ignore_tail);
        
        Pt next_tail = ate_food ? snake_at(0) : snake_at(1);
        int d_tail = bfs_dist(next, next_tail, ignore_tail); 
        
        int safe = (d_tail < MAX_GRID) || (nx == next_tail.x && ny == next_tail.y);
        
        if (safe) {
            if (d_food < min_food_dist) {
                min_food_dist = d_food;
                best_dir = d;
            }
        } else {
            /* If not safe, and we haven't found a safe move yet, stall by maximizing tail dist */
            if (best_dir == -1 && d_tail > max_tail_dist) {
                max_tail_dist = d_tail < MAX_GRID ? d_tail : 0;
                best_dir = d;
            }
        }
    }
    
    /* Fallback if totally trapped */
    if (best_dir == -1) {
        for (int d = 0; d < 4; d++) {
            int nx = head.x + DX[d];
            int ny = head.y + DY[d];
            if (!is_body(nx, ny, 1)) {
                best_dir = d;
                break;
            }
        }
    }
    
    if (best_dir == -1) return; /* Game over / stuck */
    
    sdir = best_dir;
    int nx = head.x + DX[sdir];
    int ny = head.y + DY[sdir];
    int ate = (nx == food.x && ny == food.y);
    
    if (!ate) {
        Pt old_tail = snake_at(0);
        erase_cell(old_tail.x, old_tail.y);
    }
    
    shead = (shead + 1) % SNAKE_MAX;
    sbuf[shead].x = nx;
    sbuf[shead].y = ny;
    
    if (ate) {
        if (slen < SNAKE_MAX) slen++;
        food_spawn();
        draw_food();
    }
    
    if (slen >= cfg_max_length) {
        clear();
        pick_color();
        snake_init();
        food_spawn();
        draw_food();
    }
}

"""

text = text[:start_idx] + new_move + text[end_idx:]

with open("src/madsnake.c", "w") as f:
    f.write(text)
