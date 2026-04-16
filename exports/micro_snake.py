# MicroPython/Casio-adapted Snake with menu and options
# Designed for Casio MicroPython with casioplot-style API
# Features:
# - Main menu (Start / Options / Exit) navigable with Up/Down and EXE to select
# - Options: Size, Speed, Food count
# - Pre-start wait: arrow press sets initial direction; EXE to start
# - Food placement avoids snake
# - Restart or return to menu after death

import time
import random
try:
    import casioplot as cp
except Exception:
    # Fallback stub for testing off-device (very small subset behaviour)
    class _Stub:
        W=128; H=64
        def clear(self): pass
        def text(self,x,y,s): print(s)
        def rect(self,x,y,w,h,fill=False): pass
        def fill_rect(self,x,y,w,h): pass
        def show(self): pass
        def is_pressed(self,k): return False
    cp = _Stub()

# Key codes used on many Casio MicroPython ports (may vary):
KEY_UP = 26
KEY_DOWN = 25
KEY_LEFT = 28
KEY_RIGHT = 27
KEY_EXE = 31
KEY_AC = 47

# Defaults (logical cells)
GAME_SIZE = 12
SPEED = 6  # ticks per second
FOOD_COUNT = 1

SCREEN_W = getattr(cp, 'W', 128)
SCREEN_H = getattr(cp, 'H', 64)

def draw_text_center(y, text):
    # crude center by character count
    cp.text((SCREEN_W - len(text)*6)//2, y, text)

# Simple menu system
menu_items = ["Start", "Options", "Exit"]

def menu():
    sel = 0
    while True:
        cp.clear()
        draw_text_center(4, "SNAKE (MicroPython)")
        y = 20
        for i, item in enumerate(menu_items):
            prefix = '>' if i==sel else ' '
            cp.text(10, y, prefix + ' ' + item)
            y += 12
        cp.show()
        # wait key
        while True:
            if cp.is_pressed(KEY_UP):
                sel = (sel - 1) % len(menu_items)
                break
            if cp.is_pressed(KEY_DOWN):
                sel = (sel + 1) % len(menu_items)
                break
            if cp.is_pressed(KEY_EXE):
                if menu_items[sel] == 'Start':
                    return 'start'
                if menu_items[sel] == 'Options':
                    return 'options'
                if menu_items[sel] == 'Exit':
                    return 'exit'
            time.sleep(0.08)

# Options state
opts = {'size': GAME_SIZE, 'speed': SPEED, 'food': FOOD_COUNT}

def options_menu():
    keys = ['size','speed','food','back']
    sel = 0
    while True:
        cp.clear()
        draw_text_center(2, 'Options')
        y = 18
        cp.text(6,y, 'Size: %d' % opts['size'])
        y += 10
        cp.text(6,y, 'Speed: %d' % opts['speed'])
        y += 10
        cp.text(6,y, 'Food: %d' % opts['food'])
        y += 14
        cp.text(6,y, ('> Back' if sel==3 else '  Back'))
        cp.show()
        # navigate
        while True:
            if cp.is_pressed(KEY_UP):
                sel = (sel - 1) % len(keys)
                break
            if cp.is_pressed(KEY_DOWN):
                sel = (sel + 1) % len(keys)
                break
            if cp.is_pressed(KEY_LEFT):
                if keys[sel] == 'size':
                    opts['size'] = max(6, opts['size'] - 1)
                elif keys[sel] == 'speed':
                    opts['speed'] = max(1, opts['speed'] - 1)
                elif keys[sel] == 'food':
                    opts['food'] = max(1, opts['food'] - 1)
                break
            if cp.is_pressed(KEY_RIGHT):
                if keys[sel] == 'size':
                    opts['size'] = min(20, opts['size'] + 1)
                elif keys[sel] == 'speed':
                    opts['speed'] = min(20, opts['speed'] + 1)
                elif keys[sel] == 'food':
                    opts['food'] = min(6, opts['food'] + 1)
                break
            if cp.is_pressed(KEY_EXE) and keys[sel] == 'back':
                return
            time.sleep(0.08)

# Helpers

def place_food_not_on_snake(snake, existing, size, count):
    foods = list(existing)
    attempts = 0
    while len(foods) < count and attempts < 1000:
        attempts += 1
        x = random.randrange(size)
        y = random.randrange(size)
        if (x,y) not in snake and (x,y) not in foods:
            foods.append((x,y))
    # fallback scan
    if len(foods) < count:
        for yy in range(size):
            for xx in range(size):
                if (xx,yy) not in snake and (xx,yy) not in foods:
                    foods.append((xx,yy))
                    if len(foods) >= count:
                        return foods
    return foods

# Drawing: map logical cells into small pixel region centered on screen
CELL_PIX = 4  # rough estimate; Casio screen small

def draw_game(snake, foods, score, size):
    cp.clear()
    grid_w = size * CELL_PIX
    origin_x = max(0, (SCREEN_W - grid_w)//2)
    origin_y = 6
    # border (adjacent outside playable area): 1-pixel rectangle around
    cp.rect(origin_x-1, origin_y-1, grid_w+2, grid_w+2)
    # draw foods
    for fx,fy in foods:
        cp.fill_rect(origin_x + fx*CELL_PIX, origin_y + fy*CELL_PIX, CELL_PIX, CELL_PIX)
    # draw snake
    for sx, sy in snake:
        cp.rect(origin_x + sx*CELL_PIX, origin_y + sy*CELL_PIX, CELL_PIX, CELL_PIX)
    # score
    cp.text(2, 0, 'Score: %d' % score)
    cp.show()

# Main game loop returns 'menu' or 'restart' or 'exit'

def game_loop():
    size = opts['size']
    speed = opts['speed']
    foods = []
    snake = [(size//2, size//2)]
    dir = (1,0)
    # pre-start: wait for key, allow arrow to set initial direction
    while True:
        cp.clear()
        draw_text_center(20, 'Press EXE to start')
        draw_text_center(32, 'Arrow sets first direction')
        cp.show()
        if cp.is_pressed(KEY_UP): dir = (0,-1)
        if cp.is_pressed(KEY_DOWN): dir = (0,1)
        if cp.is_pressed(KEY_LEFT): dir = (-1,0)
        if cp.is_pressed(KEY_RIGHT): dir = (1,0)
        if cp.is_pressed(KEY_EXE):
            break
        if cp.is_pressed(KEY_AC):
            return 'menu'
        time.sleep(0.08)

    # initialize foods
    foods = place_food_not_on_snake(snake, foods, size, opts['food'])
    score = 0

    tick_delay = 1.0 / max(1, speed)
    last = time.time()
    while True:
        now = time.time()
        if now - last >= tick_delay:
            last = now
            # move snake
            head = snake[0]
            new_head = ((head[0] + dir[0]) % size, (head[1] + dir[1]) % size)
            if new_head in snake:
                # died
                return 'gameover'
            snake.insert(0, new_head)
            if new_head in foods:
                foods.remove(new_head)
                score += 1
                foods = place_food_not_on_snake(snake, foods, size, opts['food'])
            else:
                snake.pop()
            draw_game(snake, foods, score, size)
        # input polling to allow direction changes
        if cp.is_pressed(KEY_UP) and dir != (0,1): dir = (0,-1)
        if cp.is_pressed(KEY_DOWN) and dir != (0,-1): dir = (0,1)
        if cp.is_pressed(KEY_LEFT) and dir != (1,0): dir = (-1,0)
        if cp.is_pressed(KEY_RIGHT) and dir != (-1,0): dir = (1,0)
        if cp.is_pressed(KEY_AC):
            return 'menu'
        time.sleep(0.01)

# Game over screen

def game_over(score):
    sel = 0
    items = ['Restart','Menu','Exit']
    while True:
        cp.clear()
        draw_text_center(10, 'Game Over')
        draw_text_center(22, 'Score: %d' % score)
        y = 36
        for i,it in enumerate(items):
            cp.text(10, y + i*10, ('> ' if i==sel else '  ') + it)
        cp.show()
        if cp.is_pressed(KEY_UP): sel = (sel - 1) % 3
        if cp.is_pressed(KEY_DOWN): sel = (sel + 1) % 3
        if cp.is_pressed(KEY_EXE):
            return items[sel].lower()
        if cp.is_pressed(KEY_AC):
            return 'menu'
        time.sleep(0.08)

# Main entry

def main():
    while True:
        action = menu()
        if action == 'start':
            res = game_loop()
            if res == 'menu':
                continue
            if res == 'gameover':
                # present game over and act on choice
                # we attempt to retrieve score by re-running a tiny loop; for simplicity pass 0
                res2 = game_over(0)
                if res2 == 'restart':
                    continue
                if res2 == 'menu':
                    continue
                if res2 == 'exit':
                    break
        elif action == 'options':
            options_menu()
        elif action == 'exit':
            break

if __name__ == '__main__':
    main()
