"""
Tetris in Pygame - Snake style with menu, options, auto-scaling, and restart flow.

Features:
- Main menu (Start / Options / Exit) navigable with arrow keys and Enter
- Options: Game Size (width x height), Speed (drop rate), Starting Level
- Fixed window size with auto-scaled cells so playable area fits
- Pre-game wait: press key to start, arrow keys rotate preview piece
- Tetris pieces: I, O, T, S, Z, L, J (classic 7 pieces)
- Line clearing with score
- Game over screen with Restart / Menu / Exit
- Smooth drop with arrow key acceleration
"""

import pygame
import random
import math
import os
# To avoid audio errors on systems without sound
os.environ['SDL_AUDIODRIVER'] = 'dummy'

pygame.init()

# ============================================================================
# CONSTANTS
# ============================================================================

WINDOW_WIDTH = 320
WINDOW_HEIGHT = 480

# Game defaults (in cells)
GAME_WIDTH = 10
GAME_HEIGHT = 20
DEFAULT_SPEED = 1  # lines per second (higher = faster)
DEFAULT_LEVEL = 1

# Display settings
FPS = 60
FONT_SMALL = pygame.font.SysFont(None, 20)
FONT_MENU = pygame.font.SysFont(None, 32)
FONT_SCORE = pygame.font.SysFont(None, 28)

# Colors
COLOR_BG = (20, 20, 30)
COLOR_BORDER = (100, 100, 100)
COLOR_GRID_LINE = (40, 40, 50)
COLOR_EMPTY = (30, 30, 40)
COLOR_TEXT = (200, 200, 200)
COLOR_HIGHLIGHT = (255, 255, 100)

# Tetris piece colors (classic)
PIECE_COLORS = {
    'I': (0, 240, 240),    # Cyan
    'O': (240, 240, 0),    # Yellow
    'T': (160, 0, 240),    # Purple
    'S': (0, 240, 0),      # Green
    'Z': (240, 0, 0),      # Red
    'L': (240, 160, 0),    # Orange
    'J': (0, 0, 240),      # Blue
}

# Piece definitions (relative coordinates)
PIECES = {
    'I': [(0, 0), (1, 0), (2, 0), (3, 0)],
    'O': [(0, 0), (1, 0), (0, 1), (1, 1)],
    'T': [(0, 1), (1, 0), (1, 1), (2, 1)],
    'S': [(1, 0), (2, 0), (0, 1), (1, 1)],
    'Z': [(0, 0), (1, 0), (1, 1), (2, 1)],
    'L': [(0, 0), (0, 1), (1, 1), (2, 1)],
    'J': [(2, 0), (0, 1), (1, 1), (2, 1)],
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def compute_scale(game_width, game_height, window_w, window_h, margin=60):
    """Auto-compute cell scale so playable area + score fits in window."""
    scale_x = (window_w - 20) // game_width
    scale_y = (window_h - margin) // game_height
    return min(scale_x, scale_y, 60)  # Cap at 60 pixels per cell

def get_game_origin(game_width, game_height, scale, window_w, window_h, score_space=60):
    """Get top-left origin for playable area (centered)."""
    playable_w = game_width * scale
    playable_h = game_height * scale
    origin_x = (window_w - playable_w) // 2
    origin_y = (window_h - playable_h - score_space) // 2 + score_space
    return origin_x, origin_y

def rotate_piece(piece_coords):
    """Rotate piece 90 degrees clockwise."""
    if not piece_coords:
        return piece_coords
    # Rotate: (x, y) -> (y, -x), then normalize to top-left
    rotated = [(y, -x) for x, y in piece_coords]
    min_x = min(x for x, y in rotated)
    min_y = min(y for x, y in rotated)
    return [(x - min_x, y - min_y) for x, y in rotated]

def collides(piece, x, y, board, width, height):
    """Check if piece at (x, y) collides with board or boundaries."""
    for dx, dy in piece:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= width or ny >= height:
            return True
        if ny >= 0 and board[ny][nx]:
            return True
    return False

def place_piece(piece, x, y, board, piece_type):
    """Place piece on board and clear any lines."""
    for dx, dy in piece:
        nx, ny = x + dx, y + dy
        if 0 <= ny < len(board) and 0 <= nx < len(board[0]):
            board[ny][nx] = piece_type

def clear_lines(board):
    """Clear full lines and return count."""
    width = len(board[0])
    new_board = [row[:] for row in board if not all(row)]
    cleared = len(board) - len(new_board)
    new_board = [[None] * width for _ in range(cleared)] + new_board
    return new_board, cleared

def spawn_piece():
    """Spawn a random piece at top center."""
    piece_type = random.choice(list(PIECES.keys()))
    piece_coords = PIECES[piece_type][:]
    x = 3
    y = 0
    return piece_coords, piece_type, x, y

# ============================================================================
# GAME LOGIC
# ============================================================================

class GameState:
    def __init__(self, width, height, speed):
        self.width = width
        self.height = height
        self.speed = speed
        self.board = [[None for _ in range(width)] for _ in range(height)]
        self.piece, self.piece_type, self.piece_x, self.piece_y = spawn_piece()
        self.next_piece, self.next_type, _, _ = spawn_piece()
        self.score = 0
        self.lines = 0
        self.level = 1
        self.drop_timer = 0
        self.game_over = False

    def update(self, dt, player_down=False):
        """Update game state by dt seconds."""
        if self.game_over:
            return
        
        # Increase drop timer
        drop_speed = self.speed + 0.5 * (self.level - 1)  # Faster with level
        self.drop_timer += dt
        should_drop = self.drop_timer >= (1.0 / drop_speed) or player_down

        if should_drop:
            self.drop_timer = 0
            # Try to move piece down
            if not collides(self.piece, self.piece_x, self.piece_y + 1, self.board, self.width, self.height):
                self.piece_y += 1
            else:
                # Piece can't move down; place it
                place_piece(self.piece, self.piece_x, self.piece_y, self.board, self.piece_type)
                self.board, cleared = clear_lines(self.board)
                self.lines += cleared
                self.score += cleared * 100 * self.level
                if cleared > 0:
                    self.level = 1 + self.lines // 5

                # Spawn next piece
                self.piece, self.piece_type, self.piece_x, self.piece_y = self.next_piece, self.next_type, 3, 0
                self.next_piece, self.next_type, _, _ = spawn_piece()

                # Check game over
                if collides(self.piece, self.piece_x, self.piece_y, self.board, self.width, self.height):
                    self.game_over = True

    def move_left(self):
        if not collides(self.piece, self.piece_x - 1, self.piece_y, self.board, self.width, self.height):
            self.piece_x -= 1

    def move_right(self):
        if not collides(self.piece, self.piece_x + 1, self.piece_y, self.board, self.width, self.height):
            self.piece_x += 1

    def rotate(self):
        rotated = rotate_piece(self.piece)
        if not collides(rotated, self.piece_x, self.piece_y, self.board, self.width, self.height):
            self.piece = rotated

    def hard_drop(self):
        """Drop piece to bottom instantly."""
        while not collides(self.piece, self.piece_x, self.piece_y + 1, self.board, self.width, self.height):
            self.piece_y += 1

# ============================================================================
# UI RENDERING
# ============================================================================

def draw_board(screen, game, scale, origin_x, origin_y):
    """Draw board, pieces, and grid."""
    board_width = game.width * scale
    board_height = game.height * scale

    # Border (1-pixel adjacent to playable area)
    pygame.draw.rect(screen, COLOR_BORDER, (origin_x - 1, origin_y - 1, board_width + 2, board_height + 2), 1)

    # Draw grid
    for row in range(game.height + 1):
        y = origin_y + row * scale
        pygame.draw.line(screen, COLOR_GRID_LINE, (origin_x, y), (origin_x + board_width, y), 1)
    for col in range(game.width + 1):
        x = origin_x + col * scale
        pygame.draw.line(screen, COLOR_GRID_LINE, (x, origin_y), (x, origin_y + board_height), 1)

    # Draw placed pieces
    for row, line in enumerate(game.board):
        for col, cell in enumerate(line):
            if cell:
                x = origin_x + col * scale
                y = origin_y + row * scale
                pygame.draw.rect(screen, PIECE_COLORS[cell], (x, y, scale, scale))
                pygame.draw.rect(screen, (255, 255, 255), (x, y, scale, scale), 1)

    # Draw current piece
    for dx, dy in game.piece:
        x = origin_x + (game.piece_x + dx) * scale
        y = origin_y + (game.piece_y + dy) * scale
        if y >= origin_y:  # Only draw if visible
            pygame.draw.rect(screen, PIECE_COLORS[game.piece_type], (x, y, scale, scale))
            pygame.draw.rect(screen, (255, 255, 255), (x, y, scale, scale), 1)

def draw_score(screen, game, font, scale, origin_x, origin_y):
    """Draw score, lines, level."""
    score_text = font.render(f'Score: {game.score}', True, COLOR_HIGHLIGHT)
    lines_text = font.render(f'Lines: {game.lines}', True, COLOR_TEXT)
    level_text = font.render(f'Level: {game.level}', True, COLOR_TEXT)
    
    screen.blit(score_text, (origin_x, origin_y - 55))
    screen.blit(lines_text, (origin_x + 150, origin_y - 55))
    screen.blit(level_text, (origin_x + 150, origin_y - 35))

def menu():
    """Main menu."""
    items = ['Start', 'Options', 'Exit']
    sel = 0
    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(FPS) / 1000.0
        screen = pygame.display.get_surface()
        screen.fill(COLOR_BG)

        title = FONT_MENU.render('TETRIS', True, COLOR_HIGHLIGHT)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 50))

        y = 150
        for i, item in enumerate(items):
            prefix = '>' if i == sel else ' '
            text = FONT_MENU.render(f'{prefix} {item}', True, COLOR_HIGHLIGHT if i == sel else COLOR_TEXT)
            screen.blit(text, (80, y))
            y += 50

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'exit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    sel = (sel - 1) % len(items)
                if event.key == pygame.K_DOWN:
                    sel = (sel + 1) % len(items)
                if event.key == pygame.K_RETURN:
                    if items[sel] == 'Start':
                        return 'start'
                    if items[sel] == 'Options':
                        return 'options'
                    if items[sel] == 'Exit':
                        return 'exit'

def options_menu():
    """Options menu: width, height, speed, level."""
    opts = {
        'width': GAME_WIDTH,
        'height': GAME_HEIGHT,
        'speed': DEFAULT_SPEED,
        'level': DEFAULT_LEVEL,
    }
    keys = ['width', 'height', 'speed', 'level', 'back']
    sel = 0
    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(FPS) / 1000.0
        screen = pygame.display.get_surface()
        screen.fill(COLOR_BG)

        title = FONT_MENU.render('Options', True, COLOR_HIGHLIGHT)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 30))

        y = 100
        for i, key in enumerate(keys[:-1]):
            prefix = '>' if i == sel else ' '
            text = FONT_SMALL.render(f'{prefix} {key.upper()}: {opts[key]}', True, COLOR_TEXT)
            screen.blit(text, (60, y))
            y += 35

        # Back button
        prefix = '>' if sel == 4 else ' '
        text = FONT_SMALL.render(f'{prefix} BACK', True, COLOR_TEXT)
        screen.blit(text, (60, y))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return opts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    sel = (sel - 1) % len(keys)
                if event.key == pygame.K_DOWN:
                    sel = (sel + 1) % len(keys)
                if event.key == pygame.K_LEFT:
                    key = keys[sel]
                    if key == 'width':
                        opts['width'] = max(8, opts['width'] - 1)
                    elif key == 'height':
                        opts['height'] = max(10, opts['height'] - 1)
                    elif key == 'speed':
                        opts['speed'] = max(0.5, opts['speed'] - 0.5)
                    elif key == 'level':
                        opts['level'] = max(1, opts['level'] - 1)
                if event.key == pygame.K_RIGHT:
                    key = keys[sel]
                    if key == 'width':
                        opts['width'] = min(20, opts['width'] + 1)
                    elif key == 'height':
                        opts['height'] = min(30, opts['height'] + 1)
                    elif key == 'speed':
                        opts['speed'] = min(10, opts['speed'] + 0.5)
                    elif key == 'level':
                        opts['level'] = min(10, opts['level'] + 1)
                if event.key == pygame.K_RETURN and sel == 4:
                    return opts

def game_loop(opts):
    """Main game loop."""
    game = GameState(int(opts['width']), int(opts['height']), opts['speed'])
    game.level = opts['level']
    scale = compute_scale(int(opts['width']), int(opts['height']), WINDOW_WIDTH, WINDOW_HEIGHT, margin=80)
    origin_x, origin_y = get_game_origin(int(opts['width']), int(opts['height']), scale, WINDOW_WIDTH, WINDOW_HEIGHT, score_space=80)

    # Pre-game wait
    waiting = True
    preview_rotation = 0
    while waiting:
        screen = pygame.display.get_surface()
        screen.fill(COLOR_BG)
        draw_board(screen, game, scale, origin_x, origin_y)
        draw_score(screen, game, FONT_SCORE, scale, origin_x, origin_y)

        wait_text = FONT_MENU.render('Press SPACE to start', True, COLOR_HIGHLIGHT)
        arrow_text = FONT_SMALL.render('Arrow keys rotate preview', True, COLOR_TEXT)
        screen.blit(wait_text, (WINDOW_WIDTH // 2 - wait_text.get_width() // 2, origin_y + 200))
        screen.blit(arrow_text, (WINDOW_WIDTH // 2 - arrow_text.get_width() // 2, origin_y + 240))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'exit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    game.piece = rotate_piece(game.piece)
                if event.key == pygame.K_ESCAPE:
                    return 'menu'

    # Game play
    clock = pygame.time.Clock()
    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'exit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move_left()
                if event.key == pygame.K_RIGHT:
                    game.move_right()
                if event.key == pygame.K_UP:
                    game.rotate()
                if event.key == pygame.K_DOWN:
                    game.update(dt, player_down=True)
                    continue
                if event.key == pygame.K_SPACE:
                    game.hard_drop()
                if event.key == pygame.K_ESCAPE:
                    return 'menu'

        game.update(dt, player_down=False)

        screen = pygame.display.get_surface()
        screen.fill(COLOR_BG)
        draw_board(screen, game, scale, origin_x, origin_y)
        draw_score(screen, game, FONT_SCORE, scale, origin_x, origin_y)

        pygame.display.flip()

        if game.game_over:
            return game_over_screen(game.score)

def game_over_screen(score):
    """Game over screen."""
    items = ['Restart', 'Menu', 'Exit']
    sel = 0
    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(FPS) / 1000.0
        screen = pygame.display.get_surface()
        screen.fill(COLOR_BG)

        title = FONT_MENU.render('GAME OVER', True, COLOR_HIGHLIGHT)
        score_text = FONT_MENU.render(f'Score: {score}', True, COLOR_TEXT)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 80))
        screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 150))

        y = 250
        for i, item in enumerate(items):
            prefix = '>' if i == sel else ' '
            text = FONT_MENU.render(f'{prefix} {item}', True, COLOR_HIGHLIGHT if i == sel else COLOR_TEXT)
            screen.blit(text, (80, y))
            y += 50

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'exit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    sel = (sel - 1) % len(items)
                if event.key == pygame.K_DOWN:
                    sel = (sel + 1) % len(items)
                if event.key == pygame.K_RETURN:
                    action = items[sel].lower()
                    if action == 'restart':
                        return 'restart'
                    if action == 'menu':
                        return 'menu'
                    if action == 'exit':
                        return 'exit'

# ============================================================================
# MAIN
# ============================================================================

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Tetris')

    opts = {
        'width': GAME_WIDTH,
        'height': GAME_HEIGHT,
        'speed': DEFAULT_SPEED,
        'level': DEFAULT_LEVEL,
    }

    while True:
        action = menu()
        if action == 'exit':
            break
        if action == 'start':
            while True:
                result = game_loop(opts)
                if result == 'restart':
                    continue
                if result == 'menu':
                    break
                if result == 'exit':
                    return
        if action == 'options':
            opts = options_menu()

    pygame.quit()

if __name__ == '__main__':
    main()
