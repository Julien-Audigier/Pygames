import os
import pygame
os.environ['SDL_AUDIODRIVER'] = 'dummy'  # To avoid audio errors on systems without sound
pygame.init()

# Set up the game window
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("My Pygame Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Paddle settings
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
PADDLE_SPEED = 7

# Ball settings
BALL_SIZE = 15
BALL_SPEED_X, BALL_SPEED_Y = 5, 5

# Initialize paddles and ball
left_paddle = pygame.Rect(30, (screen_height - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(screen_width - 40, (screen_height - PADDLE_HEIGHT) // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect((screen_width - BALL_SIZE) // 2, (screen_height - BALL_SIZE) // 2, BALL_SIZE, BALL_SIZE)
ball_vel_x, ball_vel_y = BALL_SPEED_X, BALL_SPEED_Y

# Score
left_score, right_score = 0, 0
font = pygame.font.SysFont(None, 48)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Paddle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and left_paddle.top > 0:
        left_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s] and left_paddle.bottom < screen_height:
        left_paddle.y += PADDLE_SPEED
    if keys[pygame.K_UP] and right_paddle.top > 0:
        right_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and right_paddle.bottom < screen_height:
        right_paddle.y += PADDLE_SPEED
    if keys[pygame.K_ESCAPE]:
        running = False

    # Ball movement
    ball.x += ball_vel_x
    ball.y += ball_vel_y

    # Ball collision with top/bottom
    if ball.top <= 0 or ball.bottom >= screen_height:
        ball_vel_y *= -1

    # Ball collision with paddles
    if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
        ball_vel_x *= -1

    # Ball out of bounds
    if ball.left <= 0:
        right_score += 1
        ball.x, ball.y = (screen_width - BALL_SIZE) // 2, (screen_height - BALL_SIZE) // 2
        ball_vel_x = BALL_SPEED_X
        ball_vel_y = BALL_SPEED_Y
    if ball.right >= screen_width:
        left_score += 1
        ball.x, ball.y = (screen_width - BALL_SIZE) // 2, (screen_height - BALL_SIZE) // 2
        ball_vel_x = -BALL_SPEED_X
        ball_vel_y = BALL_SPEED_Y

    # Draw everything
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, left_paddle)
    pygame.draw.rect(screen, WHITE, right_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (screen_width // 2, 0), (screen_width // 2, screen_height))

    left_text = font.render(str(left_score), True, WHITE)
    right_text = font.render(str(right_score), True, WHITE)
    screen.blit(left_text, (screen_width // 4, 20))
    screen.blit(right_text, (screen_width * 3 // 4, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()