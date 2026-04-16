import os
import pygame
os.environ['SDL_AUDIODRIVER'] = 'dummy'  # To avoid audio errors on systems without sound
pygame.init()

# Set up the game window
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Testing")

# Define colors
DARKRED = (139, 0, 0)
DARKGRAY = (64, 64, 64)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

#Classes
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

#Functions

def drawText(text: str, color: list, x: float, y: float, font: pygame.font.Font, surface = screen, mode=0):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(x, y))
    if mode == 1:
        text_rect.left = x
        text_rect.centery = y
    elif mode == 2:
        text_rect.right = x
        text_rect.centery = y
    surface.blit(text_surf, text_rect)

def getInput(question:str, y=550, color=(255, 255, 255), screen=screen):
    boxRect = pygame.Rect(0, y-50, 800, 100)
    answer = []
    REPEAT_DELAY = 110
    REPEAT_INTERVAL = 70
    button_held = False
    button_start = 0
    clock = pygame.time.Clock()
    carpet = Object(0,y+30,2,25,(0,0,0))
    carpetTime = pygame.time.get_ticks()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return(False, False)
            if event.type == pygame.KEYDOWN:
                keyName = pygame.key.name(event.key)

                if keyName == "return":
                    return(True, "".join(answer))
                elif keyName == "escape":
                    return(False, None)
                if event.key == pygame.K_BACKSPACE and len(answer) >= 1:
                    answer.pop()
                    button_held = True
                    button_start = pygame.time.get_ticks()
                else:
                    answer.append(event.unicode)
                    button_held = True
                    button_start = pygame.time.get_ticks()
            elif event.type == pygame.KEYUP:
                if pygame.key.name(event.key) == keyName:
                    REPEAT_DELAY = 300
                    button_held = False
        if button_held and (pygame.time.get_ticks()-button_start)-REPEAT_DELAY >= REPEAT_INTERVAL:
            REPEAT_DELAY = 0
            button_start = pygame.time.get_ticks()
            if keyName == pygame.key.name(pygame.K_BACKSPACE) and len(answer) >= 1:
                answer.pop()
            else:
               answer.append(keyName)
        carpet.change_position((pygame.font.Font(None, 30).size("".join(answer))[0])+12, carpet.y) #Set carpet x to the end of the caparpet
        pygame.draw.rect(screen, color, boxRect)
        drawText("".join(answer), (0,0,0), boxRect.left+10, y+30, pygame.font.Font(None, 30), screen, 1)
        pygame.draw.rect(screen, carpet.color, carpet.rect)
        if (pygame.time.get_ticks() - carpetTime) >= 60:
            carpetTime = carpetTime
        elif (pygame.time.get_ticks() - carpetTime) >= 30:
            pygame.draw.rect(screen, carpet.color, carpet.rect)
        pygame.display.flip()
        clock.tick(60)

answer = 0
running = True
while running:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if answer == 0:
        answer = getInput("Hi")
        print(answer[1])
    pygame.display.flip()