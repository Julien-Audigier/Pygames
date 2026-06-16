import pygame
import os
import random
import time
os.environ['SDL_AUDIODRIVER'] = 'dummy'
pygame.init()
pygame.display.init()
BOARD_WIDTH, BOARD_HEIGHT = 13, 9
SCREEN_VAR = 25

screen = pygame.display.set_mode((BOARD_WIDTH * SCREEN_VAR, BOARD_HEIGHT * SCREEN_VAR))

class TEXT:
    def __init__(self, text, x, y, font_size=30, color=(0, 0, 0), hover_color=None,mode="center"):
        if hover_color is None:
            hover_color = color
        self.text = text
        self.x = x
        self.y = y
        self.start_color = color
        self.hover_color = hover_color
        self.deffont_size = font_size
        self.font_size = font_size
        # Create font and cache rendered surfaces to avoid recreating each frame
        self.font = pygame.font.SysFont(None, font_size)
        self.text_surface_start = self.font.render(text, True, color)
        self.text_surface_hover = self.font.render(text, True, hover_color)
        self.mode = mode
        match mode:
            case "center":
                self.text_rect = self.text_surface_start.get_rect(center=(x, y))
            case "topleft":
                self.text_rect = self.text_surface_start.get_rect(topleft=(x, y))
        self._last_hover = False
        # Tracks whether a mouse press began while the cursor was over this text
        self._pressed_inside = False

    def is_clicked(self):
        return self.text_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]
    
    def draw(self):
        pos = pygame.mouse.get_pos()
        hover = self.text_rect.collidepoint(pos)
        # Only change rendering when hover state changes
        if hover:
            surf = self.text_surface_hover
        else:
            surf = self.text_surface_start
        # Respect alignment mode set at creation
        if getattr(self, 'mode', 'center') == 'topleft':
            text_rect = surf.get_rect(topleft=(self.x, self.y))
        else:
            text_rect = surf.get_rect(center=(self.x, self.y))
        # update stored rect so click detection stays accurate
        self.text_rect = text_rect
        screen.blit(surf, text_rect)

    def change_text(self, new_text):
        self.text = new_text
        self.text_surface_start = self.font.render(new_text, True, self.start_color)
        self.text_surface_hover = self.font.render(new_text, True, self.hover_color)
        # Update rect to match new text size 
        if getattr(self, 'mode', 'center') == 'topleft':
            self.text_rect = self.text_surface_start.get_rect(topleft=(self.x, self.y))
        else:
            self.text_rect = self.text_surface_start.get_rect(center=(self.x, self.y))

    def is_released(self):
        pos = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()[0]
        hover = self.text_rect.collidepoint(pos)
        # If mouse pressed while hovering, remember that press started here
        if pressed and hover:
            self._pressed_inside = True
            return False
        # If mouse was pressed on this widget and is now released, count it as a release
        if (not pressed) and self._pressed_inside:
            # reset state and only return True if cursor is still over the widget
            self._pressed_inside = False
            return hover
        # Otherwise, no release event for this widget
        return False

    def move(self, x, y):
        self.x =x
        self.y = y
        match self.mode:
            case "center":
                self.text_rect = self.text_surface_start.get_rect(center=(self.x, self.y))
            case "topleft":
                self.text_rect = self.text_surface_start.get_rect(topleft=(self.x, self.y))

def printBoard(board,snake,food):
    # enumerate gives us the actual row index (y) and row data
    for y, row in enumerate(board):
        # enumerate gives us the actual column index (x) and cell data
        for x, cell in enumerate(row):
            # Convert 0-based index to your 1-based coordinate system
            xy = [x + 1, y + 1]
            
            if snake.count(xy) > 0:
                print(" ■ ", end="")
            elif food.count(xy) > 0:
                print(" ● ", end="")
            else:
                # Added 'else' so empty blocks don't print next to items
                print(f" {cell} ", end="")
        print() 

def showBoard(board,snake,food):
    screen.fill((255, 255, 255))  # Clear the screen with white background
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            xy = [x + 1, y + 1]
            if (x + y) % 2 == 0:
                    pygame.draw.rect(screen, (170, 215, 81), (x * SCREEN_VAR, y * SCREEN_VAR, SCREEN_VAR, SCREEN_VAR))  # Draw empty cell
            else:
                    pygame.draw.rect(screen, (162, 209, 73), (x * SCREEN_VAR, y * SCREEN_VAR, SCREEN_VAR, SCREEN_VAR))  # Draw empty cell
            if snake.count(xy) > 0:
                # Gradient color between head_color and tail_color based on segment position
                head_color = (66, 133, 244)
                tail_color = (150, 200, 255)  # lighter tail color (can be adjusted)
                # find the index of this segment in the snake list
                try:
                    idx = snake.index(xy)
                except ValueError:
                    idx = 0
                seg_count = len(snake)
                if seg_count > 1:
                    # position from head: 0=head, seg_count-1=tail
                    pos_from_head = (seg_count - 1) - idx
                    t = pos_from_head / (seg_count - 1)
                else:
                    t = 0.0
                # linear interpolation between head_color (t=0) and tail_color (t=1)
                color = tuple(int(head_color[i] * (1 - t) + tail_color[i] * t) for i in range(3))
                pygame.draw.rect(screen, color, (x * SCREEN_VAR, y * SCREEN_VAR, SCREEN_VAR, SCREEN_VAR))  # Draw snake segment
            elif food.count(xy) > 0:
                # Draw food as a circle centered in the cell
                center = (x * SCREEN_VAR + SCREEN_VAR // 2, y * SCREEN_VAR + SCREEN_VAR // 2)
                radius = SCREEN_VAR // 2 - 3
                pygame.draw.circle(screen, (255, 0, 0), center, radius)
    pygame.display.flip()  # Update the display

def genBoard(length,height):
    board = []
    for i in range(0,height):
        board.append([])
    for row in board:
        for i in range(0,length):
            row.append("□")
    return board

#seqment = "■"
#food = "●"

#Buttons:
StartButton = TEXT("Start", BOARD_WIDTH * SCREEN_VAR // 2, BOARD_HEIGHT * SCREEN_VAR // 2, font_size=50, color=(0, 0, 0), hover_color=(255, 0, 0))

clock = pygame.Clock()
tickrate = 60
mode = "Menu"
running = True
movement = [0, 0]

while running:
    #Movement Detection
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
                running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and movement != [0, 1]:
                movement = [0, -1]
            elif event.key == pygame.K_DOWN and movement != [0, -1]:
                movement = [0, 1]
            elif event.key == pygame.K_LEFT and movement != [1, 0]:
                movement = [-1, 0]
            elif event.key == pygame.K_RIGHT and movement != [-1, 0]:
                movement = [1, 0]

    match mode:
        case "Menu":
            screen.fill((255, 255, 255))  # Clear the screen with white background
            StartButton.draw()
            if StartButton.is_released():
                mode = "SetVars"         
        case "SetVars":
            board = genBoard(BOARD_WIDTH, BOARD_HEIGHT)
            snake = [[8,5],[7,5],[6,5]]
            food = []
            for i in range(10): #Make Food
                for attempt in range(1000):
                    food.append([random.randint(1, BOARD_WIDTH), random.randint(1, BOARD_HEIGHT)])
                    if food[-1] in snake or food[-1] in food[:-1]:
                        food.pop()
                    else:
                        break
            movement=[0,0]
            firstMove = True
            tickrate = 7
            mode = "Game"
        case "Game":
            #Movement:
            if movement != [0, 0]:
                if firstMove and movement == [1, 0]:
                    snake.reverse()
                current_head = snake[-1]
                new_head = [current_head[0] + movement[0], current_head[1] + movement[1]]
                snake.append(new_head)
                if new_head in food:
                    food.remove(new_head)
                    for attempt in range(100):
                        food.append([random.randint(1, BOARD_WIDTH), random.randint(1, BOARD_HEIGHT)])
                        if food[-1] in snake or food[-1] in food[:-1]:
                            food.pop()
                        else:
                            break
                elif new_head in snake[:-1] or new_head[0] < 1 or new_head[0] > BOARD_WIDTH or new_head[1] < 1 or new_head[1] > BOARD_HEIGHT:
                    mode = "GameOver"
                else:
                    snake.pop(0)
                head = snake[-1]
                firstMove = False

            #Display:
            showBoard(board, snake, food)
        case "GameOver":
            StartButton.change_text("Play Again")
            tickrate = 60
            time.sleep(0.5)
            mode = "Menu"
        case "Win":
            pass
        case "Settings":
            pass 

    pygame.display.flip() 
    clock.tick(tickrate)

pygame.quit()