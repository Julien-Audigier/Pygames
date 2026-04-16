import math
import os
import pygame
# To avoid audio errors on systems without sound
os.environ['SDL_AUDIODRIVER'] = 'dummy'
pygame.init()

# Set up the game window
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Parkor Game")


# Define colors
DARKGRAY = (64, 64, 64)
DARKRED = (139, 0, 0)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHTGRAY = (200, 200, 200)

# Functions

def drawText(text=str, color=list, x=float, y=float, font = pygame.font.Font, surface=screen):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(x, y))
    surface.blit(text_surf, text_rect)

def centerObjectsOnObject(objects: list[object], centerObject: object, spaceing: int):
    y = spaceing + (centerObject.height - (len(objects)+1) * spaceing) / len(objects) / 2
    for object in objects:
        object.change_size(object.width, (centerObject.height - (len(objects)+1) * spaceing) / len(objects))
        object.change_position(centerObject.rect.centerx, y)
        y += spaceing + (centerObject.height - (len(objects)+1) * spaceing) / len(objects)

# Classes

class Object:
    def __init__(self, x, y, width, height, color, text=None, textColor=None, font_size=30, showing=True):
        self.rect = pygame.Rect(x-width/2, y-height/2, width, height)
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.showing = showing
        self.font = pygame.font.Font(None, font_size)
        self.text_color = textColor  # White

    def display_text(self,x="~",y="~", surface=screen):
        if x == "~":
            x = self.rect.center[0]
        if y == "~":
            y = self.rect.center[1]
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=(x, y))
        surface.blit(text_surf, text_rect)

    def change_position(self, x, y):
        self.x = x
        self.y = y
        self.rect.center = (x, y)

    def change_size(self, width, height):
        self.width = width
        self.height = height
        self.rect.size = (width, height)
        self.rect.topleft = (self.x - width/2, self.y - height/2)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class Level:
    def __init__(self, level_number, size, layout):
        self.level_number = level_number
        self.size = size
        self.layout = layout
        # Cached surface for the level (render once, blit each frame)
        self.surface = pygame.Surface((screen_width, screen_height))
        self.dirty = True
        # Font used for special tiles (avoid creating per-tile)
        self.font = pygame.font.Font(None, max(30, self.size // 2))
    
    def generate_layout(self):
        self.layout = [['#' for _ in range(
            screen_width//self.size)] for _ in range(screen_height//self.size)]
        self.dirty = True

    def draw_square(self, x, y, type, surface=screen):
        rectSq = pygame.Rect(y * self.size, x * self.size, self.size, self.size)
        match type:
            case '#':  # Wall
                pygame.draw.rect(self.surface, DARKRED, rectSq)
            case ' ':  # Nothing
                pygame.draw.rect(self.surface, WHITE, rectSq)
            case '^':  # SpikesUp
                drawText("ඞ",BLACK, rectSq.center[0], rectSq.center[1]+10, self.font, self.surface)
            case '>':  # SpikesRight
                drawText(">",BLACK, rectSq.center[0]-4, rectSq.center[1], self.font, self.surface)
            case 'v':  # SpikesDown
                drawText("v",BLACK, rectSq.center[0], rectSq.center[1]-4, self.font, self.surface)
            case '<':  # SpikesLeft
                drawText("<",BLACK, rectSq.center[0]+5, rectSq.center[1], self.font, self.surface)         
            case '&':  # Player start position
                drawText("&", BLACK, rectSq.center[0], rectSq.center[1]+4, self.font, self.surface)
            case '()':  # Goal
                drawText("()",BLACK, rectSq.center[0], rectSq.center[1], self.font, self.surface)
    
    def load_level(self, surface=screen):
        # Only re-render the level onto the cached surface when something changed
        if self.dirty:
            print(self.layout)
            self.surface.fill(WHITE)
            for y in range(len(self.layout)):
                for x in range(len(self.layout[y])):
                    self.draw_square(y, x, Level1.layout[y][x], self.surface)
            # Draw grid lines on cached surface
            self.dirty = False

        # Blit the cached surface to the target surface
        surface.blit(self.surface, (0, 0))
    
    def draw_grid(self):
        for x in range(0, screen_width, self.size):
            pygame.draw.line(screen, BLACK, (x, 0), (x, screen_height))
        for y in range(0, screen_height, self.size):
            pygame.draw.line(screen, BLACK, (0, y), (screen_width, y))

class Image:
    def __init__(self, x, y, width, height, path, showing=False):
        self.image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(center=(x, y))

    def change_position(self, x, y):
        self.rect.center = (x, y)
    
    def change_size(self, width, height):
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect.size = (width, height)

    def draw(self, surface=screen):
        surface.blit(self.image, self.rect)

# Vars
mouseHeld = False
tilesPressed = []
modeIndex = 0
modes = ["#", " ", "^", "&", "()"]  # Wall, Nothing, Spikes, Player Start, Goal
spikeRotation = ["^",">","v","<"]
row, col = 0, 0
mouse_pos = 0, 0

#Images
pygame.mouse.set_visible(True)
pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

# Objects
Level1 = Level(1, 20, None)
Level1.generate_layout()

MenuOpen = Object(775, 25, 27, 27, BLACK, "Open", WHITE, 25)
Menu = Object(725, 300, 150, 600, DARKGRAY, font_size=25,showing=False)
MenuButtons = [
    Object(0, 0, 110, 50, BLACK, "Tile", WHITE, 25),
    Object(0, 0, 110, 50, BLACK, "Spikes", WHITE, 25),
    Object(0, 0, 110, 50, BLACK, "Player Start", WHITE, 25),
    Object(0, 0, 110, 50, BLACK, "Goal", WHITE, 25),
    Object(0, 0, 110, 50, BLACK, "Reset", WHITE, 25),
    Object(0, 0, 110, 50, BLACK, "Save Level", WHITE, 25),
    Object(0, 0, 110, 50, BLACK, "Load Level", WHITE, 25),
    Object(0, 0, 110, 50, BLACK, "To Menu", WHITE, 25),
]
centerObjectsOnObject(MenuButtons, Menu, 20)

# Main Loop
running = True
clock = pygame.Clock()
while running:
    screen.fill(WHITE)
    Level1.load_level()
    Level1.draw_grid()
    if mouse_pos != pygame.mouse.get_pos():
        if Level1.layout[row][col] != "#":
            Level1.draw_square(row, col, ' ')
        Level1.draw_square(row,col, Level1.layout[row][col])
    mouse_pos = pygame.mouse.get_pos()
    pygame.display.set_caption(f"Parkor Game - Mouse Position: {mouse_pos}")

    col = math.floor(mouse_pos[0] // Level1.size)
    row = math.floor(mouse_pos[1] // Level1.size)
    rectSq = pygame.Rect(col * Level1.size, row * Level1.size, Level1.size, Level1.size)
    pygame.draw.rect(screen, GRAY, rectSq, 3)  # Highlighted tile
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN or mouseHeld:
            if Menu.showing:
                if MenuButtons[0].is_clicked(mouse_pos): #Tile
                    modeIndex = 0
                    Menu.showing = False
                    continue
                elif MenuButtons[1].is_clicked(mouse_pos): #Spikes
                    modeIndex = 2
                    Menu.showing = False
                    continue
                elif MenuButtons[2].is_clicked(mouse_pos): #Player Start
                    modeIndex = 3
                    Menu.showing = False
                    continue
                elif MenuButtons[3].is_clicked(mouse_pos): #Goal
                    modeIndex = 4
                    Menu.showing = False
                    continue
                elif MenuButtons[4].is_clicked(mouse_pos): #Reset
                    Level1.generate_layout()
                    continue
                
            if MenuOpen.is_clicked(mouse_pos):
                Menu.showing = not Menu.showing

            else: #level clicked
                if ((col, row) not in tilesPressed) and not (Menu.showing and Menu.rect.collidepoint(mouse_pos)):
                    tilesPressed.append((col, row))# To avoid multiple placements on one click
                    if (mouseHeld == False) and (modeIndex == 0 or modeIndex == 1): #On and only on click
                        modeIndex = (modes.index(Level1.layout[row][col])+1) % 2 #Toggle between wall and nothing
                    if Level1.layout[row][col] != "#":
                        if modeIndex == 3:  # Ensure only one player start
                            for y in range(len(Level1.layout)):
                                for x in range(len(Level1.layout[y])):
                                    if (x, y) != (col, row) and Level1.layout[y][x] == '&':
                                        Level1.layout[y][x] = ' '
                        Level1.layout[row][col] = modes[modeIndex]
                    if modeIndex == 0 or modeIndex == 1:
                        Level1.layout[row][col] = modes[modeIndex]
                    Level1.dirty = True       
                mouseHeld = True

        if event.type == pygame.MOUSEBUTTONUP:
            tilesPressed = []
            mouseHeld = False

    keys = pygame.key.get_just_released()
    if keys[pygame.K_r] and modeIndex == 2: #Rotate spikes
        modes[2] = spikeRotation[(spikeRotation.index(modes[2]) + 1) % len(spikeRotation)]
        Level1.draw_square(row, col, Level1.layout[row][col])
    if keys[pygame.K_ESCAPE]:
        if Menu.showing:
            Menu.showing = False
        else:
            running = False
        # Limit frame rate to reduce CPU usage
        clock.tick(60)

    # Drawing
    #Pre-Click Square
    if modeIndex == 0 or modeIndex == 1:
        if Level1.layout[row][col] == ' ' and not mouseHeld:
            Level1.draw_square(row,col, "#")
        else:
            Level1.draw_square(row,col, ' ')
    else:
        if Level1.layout[row][col] != "#":
            Level1.draw_square(row, col, ' ')
        Level1.draw_square(row, col, modes[modeIndex])

    # Menu
    if Menu.showing:
        pygame.draw.rect(screen, Menu.color, Menu.rect)
        Menu.text_color = WHITE
        Menu.text = f"Selected {modes[modeIndex]}"
        Menu.display_text(Menu.rect.centerx, Menu.rect.top+10)
        for button in MenuButtons:
            button.color = BLACK
            if modeIndex == 0 or modeIndex == 1:
                MenuButtons[0].color = LIGHTGRAY
            else:
                MenuButtons[modeIndex-1].color = LIGHTGRAY
            pygame.draw.rect(screen, button.color, button.rect)
            if button.is_clicked(mouse_pos):
                pygame.draw.rect(screen, WHITE, button.rect, 3)
            button.display_text()
    else:
        pygame.draw.ellipse(screen, MenuOpen.color, MenuOpen.rect)
        MenuOpen.display_text()
    
    #Cursor.draw()
    pygame.display.flip()  # Update the display