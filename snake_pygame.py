import pygame
import random
import sys
import os
import time

# To avoid audio errors on systems without sound
os.environ['SDL_AUDIODRIVER'] = 'dummy'

# Default settings
DEFAULT_WIDTH = 896
DEFAULT_HEIGHT = 448
DEFAULT_SPEED = 5
DEFAULT_FOOD = 50
SCALE = 39

# Game settings (can be changed in options)
WIDTH = DEFAULT_WIDTH
HEIGHT = DEFAULT_HEIGHT
SPEED = DEFAULT_SPEED
FOOD_COUNT = DEFAULT_FOOD
WINDOW_WIDTH = WIDTH
WINDOW_HEIGHT = HEIGHT

# Playable area: use a square size (number of cells) independent of window size
GAME_SIZE = 8  # default playable area is GAME_SIZE x GAME_SIZE cells
# Window stays fixed for visibility; SCALE is the pixel size per cell
WINDOW_WIDTH = WIDTH
WINDOW_HEIGHT = HEIGHT
# Game area origin (in cell coordinates), centered inside the window
GAME_X = (WINDOW_WIDTH // SCALE - GAME_SIZE) // 2
GAME_Y = (WINDOW_HEIGHT // SCALE - GAME_SIZE) // 2
# Border is 1 cell larger on each side
BORDER_SIZE = GAME_SIZE + 2
BORDER_X = GAME_X - 1
BORDER_Y = GAME_Y - 1

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake Game (Casio Style)")
font = pygame.font.SysFont(None, 24)
score_font = pygame.font.SysFont(None, 32)
clock = pygame.time.Clock()

def draw_menu(selected):
    screen.fill(BLACK)
    title = font.render("Snake Game", True, WHITE)
    screen.blit(title, (WINDOW_WIDTH//2 - 40, WINDOW_HEIGHT//2 - 80))
    options = ["Start Game", "Options", "Exit"]
    for i, option in enumerate(options):
        color = GREEN if i == selected else WHITE
        text = font.render(option, True, color)
        screen.blit(text, (WINDOW_WIDTH//2 - 40, WINDOW_HEIGHT//2 - 20 + i*40))
    pygame.display.flip()

def menu():
    selected = 0
    while True:
        draw_menu(selected)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % 3
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % 3
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        return 'start'
                    elif selected == 1:
                        return 'options'
                    else:
                        pygame.quit()
                        sys.exit()
        clock.tick(15)

def draw_options(selected, game_size, speed, food_count):
    screen.fill(BLACK)
    title = font.render("Options", True, WHITE)
    screen.blit(title, (WINDOW_WIDTH//2 - 40, WINDOW_HEIGHT//2 - 100))
    opts = [f"Size: {game_size}x{game_size}", f"Speed: {speed}", f"Food: {food_count}", "Back"]
    for i, opt in enumerate(opts):
        color = GREEN if i == selected else WHITE
        text = font.render(opt, True, color)
        screen.blit(text, (WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 - 40 + i*40))
    pygame.display.flip()

def options_menu():
    global GAME_SIZE, SPEED, FOOD_COUNT, GAME_X, GAME_Y, BORDER_SIZE, BORDER_X, BORDER_Y, SCALE
    selected = 0
    game_size = GAME_SIZE
    speed = SPEED
    food_count = FOOD_COUNT
    # max playable size in cells (leave room for border)
    max_size = min(WIDTH, HEIGHT) - 2
    while True:
        draw_options(selected, game_size, speed, food_count)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % 4
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % 4
                elif event.key == pygame.K_LEFT:
                    if selected == 0:
                        game_size = max(8, game_size - 4)
                    elif selected == 1:
                        speed = max(2, speed - 1)
                    elif selected == 2:
                        food_count = max(1, food_count - 1)
                elif event.key == pygame.K_RIGHT:
                    if selected == 0:
                        game_size = min(max_size, game_size + 4)
                    elif selected == 1:
                        speed = min(60, speed + 1)
                    elif selected == 2:
                        food_count = min(60, food_count + 1)
                elif event.key == pygame.K_RETURN:
                    if selected == 3:
                        # Apply changes: compute SCALE automatically so the playable area fits inside the fixed window
                        GAME_SIZE = game_size
                        BORDER_SIZE = GAME_SIZE + 2
                        # compute maximum integer scale (pixels per cell) so border fits with small margins
                        margin_px = 20
                        score_margin = 30
                        max_scale_x = (WINDOW_WIDTH - margin_px) // BORDER_SIZE
                        max_scale_y = (WINDOW_HEIGHT - score_margin - margin_px) // BORDER_SIZE
                        SCALE = max(1, min(max_scale_x, max_scale_y))
                        print(f"Options set: GAME_SIZE={GAME_SIZE}, SCALE={SCALE}, SPEED={speed}, FOOD_COUNT={food_count}")
                        # Recompute origin in cell coordinates (we keep logical coords 0..GAME_SIZE-1)
                        GAME_X = (WIDTH - GAME_SIZE) // 2
                        GAME_Y = (HEIGHT - GAME_SIZE) // 2
                        BORDER_X = GAME_X - 1
                        BORDER_Y = GAME_Y - 1
                        SPEED = speed
                        FOOD_COUNT = food_count
                        return
        clock.tick(15)

def place_food_not_on_snake(snake, existing_foods, game_size):
    # Return a random (x,y) not currently occupied by the snake or existing foods
    attempts = 0
    while True:
        x = random.randint(0, game_size - 1)
        y = random.randint(0, game_size - 1)
        if (x, y) not in snake and (x, y) not in existing_foods:
            return (x, y)
        attempts += 1
        if attempts > 1000:
            for ix in range(game_size):
                for iy in range(game_size):
                    if (ix, iy) not in snake and (ix, iy) not in existing_foods:
                        return (ix, iy)
            if existing_foods.count([-100,0]) == len(existing_foods):
                return "win"
            else:
                return [-100, 0]  # error case
                    
def draw_game(snake, foods, score):
    screen.fill(BLACK)
    # Draw game area border (1 cell larger than playable area)
    # Compute pixel origin for playable area so it is centered in the fixed window
    play_w_px = GAME_SIZE * SCALE
    play_h_px = GAME_SIZE * SCALE
    origin_x = (WINDOW_WIDTH - play_w_px) // 2
    origin_y = (WINDOW_HEIGHT - play_h_px) // 2
    # Border rectangle: 1-pixel border immediately outside the playable cells (no overlap)
    border_rect = pygame.Rect(origin_x - 1, origin_y - 1, GAME_SIZE * SCALE + 2, GAME_SIZE * SCALE + 2)
    pygame.draw.rect(screen, WHITE, border_rect, 1)
    # Draw score centered above the playable area border
    score_text = score_font.render(f"Score: {score}", True, WHITE)
    score_x = border_rect.x + border_rect.width // 2 - score_text.get_width() // 2
    score_y = max(border_rect.y - 34, 5)
    screen.blit(score_text, (score_x, score_y))
    # Draw snake (logical coordinates 0..GAME_SIZE-1)
    startColor = 200
    endColor = 255
    step = (endColor - startColor) // max(len(snake),1)
    i = startColor
    for segment in snake:
        sx = origin_x + segment[0] * SCALE
        sy = origin_y + segment[1] * SCALE
        pygame.draw.rect(screen, (0,i,0), (sx, sy, SCALE, SCALE))
        i+=step
    # Draw food
    for f in foods:
        fx = origin_x + f[0] * SCALE
        fy = origin_y + f[1] * SCALE
        pygame.draw.rect(screen, RED, (fx, fy, SCALE, SCALE))
    pygame.display.flip()

def handle_input(direction):
    next_direction = direction
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and direction != (-1, 0):
                next_direction = (1, 0)
            elif event.key == pygame.K_LEFT and direction != (1, 0):
                next_direction = (-1, 0)
            elif event.key == pygame.K_UP and direction != (0, 1):
                next_direction = (0, -1)
            elif event.key == pygame.K_DOWN and direction != (0, -1):
                next_direction = (0, 1)
            elif event.key == pygame.K_ESCAPE:
                return 'menu', next_direction
    return 'game', next_direction

def game_loop():
    global GAME_SIZE, SPEED, FOOD_COUNT, GAME_X, GAME_Y
    snake = [(GAME_SIZE//2, GAME_SIZE//2), (GAME_SIZE//2-1, GAME_SIZE//2), (GAME_SIZE//2-2, GAME_SIZE//2)]
    direction = (1, 0)
    score = 0
    foods = []
    for _ in range(FOOD_COUNT):
        result = place_food_not_on_snake(snake, foods, GAME_SIZE)
        if result == "win":
            return win(score)
        foods.append(result)
    game_over = False
    # Wait for player to press a key to start
    waiting = True
    origin_x = (WINDOW_WIDTH - GAME_SIZE * SCALE) // 2
    origin_y = (WINDOW_HEIGHT - GAME_SIZE * SCALE) // 2
    # draw initial frame
    draw_game(snake, foods, score)
    while waiting:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                # If an arrow key is pressed at start, set initial direction accordingly.
                if ev.key == pygame.K_RIGHT and direction != (-1, 0):
                    direction = (1, 0)
                elif ev.key == pygame.K_LEFT and direction != (1, 0):
                    direction = (-1, 0)
                elif ev.key == pygame.K_UP and direction != (0, 1):
                    direction = (0, -1)
                elif ev.key == pygame.K_DOWN and direction != (0, -1):
                    direction = (0, 1)
                # Any key starts the game; arrow keys also set the starting direction
                waiting = False
        clock.tick(30)
    while not game_over:
        state, next_direction = handle_input(direction)
        if state == 'menu':
            return 'menu'
        direction = next_direction
        head_x, head_y = snake[0]
        new_head = (head_x + direction[0], head_y + direction[1])
        if new_head[0] < 0 or new_head[0] >= GAME_SIZE or new_head[1] < 0 or new_head[1] >= GAME_SIZE:
            game_over = True
            break
        if new_head in snake:
            game_over = True
            break
        snake.insert(0, new_head)
        ate_food = False
        for i, food in enumerate(foods):
            if new_head == food:
                score += 10
                # replace eaten food ensuring it doesn't spawn on the snake
                other_foods = [f for j, f in enumerate(foods) if j != i]
                result = place_food_not_on_snake(snake, other_foods, GAME_SIZE)
                if result == "win":
                    return win(score)
                foods[i] = result
                ate_food = True
                break
        if not ate_food:
            snake.pop()
        draw_game(snake, foods, score)
        clock.tick(SPEED)
    return game_over_screen(score)

def game_over_screen(score):
    selected = 0
    while True:
        screen.fill(BLACK)
        over_text = font.render("GAME OVER", True, WHITE)
        score_text = font.render(f"Final Score: {score}", True, WHITE)
        options = ["Restart", "Menu", "Exit"]
        for i, opt in enumerate(options):
            color = GREEN if i == selected else WHITE
            text = font.render(opt, True, color)
            screen.blit(text, (WINDOW_WIDTH//2 - 40, WINDOW_HEIGHT//2 - 20 + i*40))
        screen.blit(over_text, (WINDOW_WIDTH//2 - 40, WINDOW_HEIGHT//2 - 80))
        screen.blit(score_text, (WINDOW_WIDTH//2 - 50, WINDOW_HEIGHT//2 - 50))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % 3
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % 3
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        return 'restart'
                    elif selected == 1:
                        return 'menu'
                    else:
                        pygame.quit()
                        sys.exit()
        clock.tick(15)

def win(score):
    time.sleep(0.5)  # brief pause before showing win screen
    selected = 0
    while True:
        screen.fill(BLACK)
        over_text = font.render("  Win!", True, WHITE)
        score_text = font.render(f"Food eaten: {int(score/10)}", True, WHITE)
        options = ["Restart", "Menu", "Exit"]
        for i, opt in enumerate(options):
            color = GREEN if i == selected else WHITE
            text = font.render(opt, True, color)
            screen.blit(text, (WINDOW_WIDTH//2 - 40, WINDOW_HEIGHT//2 - 20 + i*40))
        screen.blit(over_text, (WINDOW_WIDTH//2 - 40, WINDOW_HEIGHT//2 - 80))
        screen.blit(score_text, (WINDOW_WIDTH//2 - 50, WINDOW_HEIGHT//2 - 50))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % 3
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % 3
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        return 'restart'
                    elif selected == 1:
                        return 'menu'
                    else:
                        pygame.quit()
                        sys.exit()
        clock.tick(15)

def main():
    while True:
        choice = menu()
        if choice == 'start':
            # Start games repeatedly until the player returns to menu or exits
            while True:
                result = game_loop()
                if result == 'restart':
                    # Start a new game immediately
                    continue
                elif result == 'menu':
                    # Go back to main menu
                    break
                else:
                    # Any other result - exit
                    return
        elif choice == 'options':
            options_menu()
        else:
            break

if __name__ == "__main__":
    main()
