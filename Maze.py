import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 640  # Increased height for score and timer display
TILE_SIZE = 20
COLS = SCREEN_WIDTH // TILE_SIZE
ROWS = (SCREEN_HEIGHT - 40) // TILE_SIZE  # Adjust rows for new height

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# Player attributes
player_size = TILE_SIZE
player_pos = [20, 60]  # Start position
player_speed = 10

# Maze layout (walls and paths)
maze = [['1' for _ in range(COLS)] for _ in range(ROWS)]  # Initialize with walls (1)

# Function to create maze using DFS
def create_maze(x, y):
    directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]  # right, left, down, up
    random.shuffle(directions)  # Randomize directions to create a unique maze

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] == '1':
            maze[y + dy // 2][x + dx // 2] = '0'  # Remove wall
            maze[ny][nx] = '0'  # Mark the new cell as a path
            create_maze(nx, ny)  # Recursive call to create more paths

# Start maze generation from the top-left corner
create_maze(1, 1)

# Convert maze into wall rectangles
maze_walls = []
for y in range(ROWS):
    for x in range(COLS):
        if maze[y][x] == '1':
            wall_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE + 40, TILE_SIZE, TILE_SIZE)  # Offset by 40 pixels
            maze_walls.append(wall_rect)

# Coins (random positions)
coin_positions = []
while len(coin_positions) < 10:  # Add 10 coins randomly
    while True:
        coin_pos = [random.randint(1, (SCREEN_WIDTH // TILE_SIZE) - 1) * TILE_SIZE,
                    random.randint(2, (SCREEN_HEIGHT // TILE_SIZE) - 3) * TILE_SIZE + 40]  # Offset for new height
        coin_rect = pygame.Rect(coin_pos[0], coin_pos[1], player_size, player_size)
        # Ensure coins do not spawn in walls or player start position
        if not any(wall.colliderect(coin_rect) for wall in maze_walls) and coin_pos not in coin_positions:
            coin_positions.append(coin_pos)
            break

# Finish line
finish_line = pygame.Rect(580, 620, 20, 20)  # Offset by 40 pixels
finish_line_enabled = False

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Maze Game')

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Score and Timer
score = 0
timer = 90  # Set timer for 60 seconds

# Initialize font
font = pygame.font.Font(None, 48)  # Font size for score and timer
instruction_font = pygame.font.Font(None, 36)  # Smaller font for instructions

# Function to render text
def render_text(text, pos, background_color=BLACK, is_instruction=False):
    if is_instruction:
        text_surface = instruction_font.render(text, True, WHITE)
    else:
        text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=pos)
    
    # Draw background rectangle
    background_rect = pygame.Rect(text_rect.x - 10, text_rect.y - 10, text_rect.width + 20, text_rect.height + 20)
    pygame.draw.rect(screen, background_color, background_rect)
    
    screen.blit(text_surface, text_rect)

# Function to draw the instruction screen
def show_instructions():
    screen.fill(BLACK)
    render_text("Welcome to the Maze Game!", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80), is_instruction=True)
    render_text("Navigate through the maze to collect 10 coins.", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40), is_instruction=True)
    render_text("The finish line will be enabled after collecting all coins.", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), is_instruction=True)
    render_text("Reach the finish line before time runs out!", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40), is_instruction=True)
    render_text("Controls: Use W, A, S, D to move.", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80), is_instruction=True)

    # Draw "I understand" button
    button_rect = pygame.Rect((SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 120), (200, 50))
    pygame.draw.rect(screen, WHITE, button_rect)  # Draw button background
    pygame.draw.rect(screen, BLACK, button_rect, 3)  # Draw button outline with increased thickness
    render_text("I understand", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 145), BLACK)

    pygame.display.flip()

    return button_rect

# Function to check if a point is inside the maze and not a wall
def is_valid_point(x, y):
    if x < 0 or y < 0 or x >= SCREEN_WIDTH or y >= SCREEN_HEIGHT:
        return False
    test_rect = pygame.Rect(x, y, player_size, player_size)
    for wall in maze_walls:
        if test_rect.colliderect(wall):
            return False
    return True

# Game loop
running = True
game_won = False
game_over = False
instructions_shown = True  # Flag to show instructions screen
button_rect = show_instructions()  # Display instructions screen

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and instructions_shown:
            if button_rect.collidepoint(event.pos):
                instructions_shown = False  # Hide instructions and start the game
                score = 0  # Reset score
                player_pos[0] = 20  # Reset player position
                player_pos[1] = 60

    # Update timer
    if not game_won and not game_over and not instructions_shown:
        timer -= clock.get_time() / 1000  # Decrease timer based on time elapsed
        if timer <= 0:
            game_over = True  # End game when time runs out

    # Get keys
    keys = pygame.key.get_pressed()

    # Store intended position
    intended_pos = player_pos[:]

    # Player movement with W, A, S, D
    if keys[pygame.K_a]:
        intended_pos[0] -= player_speed
    if keys[pygame.K_d]:
        intended_pos[0] += player_speed
    if keys[pygame.K_w]:
        intended_pos[1] -= player_speed
    if keys[pygame.K_s]:
        intended_pos[1] += player_speed

    # Ensure the intended position is within bounds
    intended_pos[0] = max(0, min(intended_pos[0], SCREEN_WIDTH - player_size))
    intended_pos[1] = max(40, min(intended_pos[1], SCREEN_HEIGHT - player_size))  # Adjust for new height

    # Check for collision with walls at the intended position
    intended_rect = pygame.Rect(intended_pos[0], intended_pos[1], player_size, player_size)
    collision_with_wall = False
    for wall in maze_walls:
        if intended_rect.colliderect(wall):
            collision_with_wall = True
            break

    # If no collision with walls, update player position
    if not collision_with_wall:
        player_pos = intended_pos[:]

    # Player rectangle
    player_rect = pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)

    # Check if player reached the finish line and if it's enabled
    if player_rect.colliderect(finish_line) and finish_line_enabled:
        game_won = True

    # Check if player collected any coins
    for coin in coin_positions[:]:
        coin_rect = pygame.Rect(coin[0], coin[1], player_size, player_size)
        if player_rect.colliderect(coin_rect):
            coin_positions.remove(coin)
            score += 1
            if score >= 10:
                finish_line_enabled = True

    # Fill screen
    if not instructions_shown:
        screen.fill(WHITE)

        # Draw maze walls
        for wall in maze_walls:
            pygame.draw.rect(screen, BLACK, wall)

        # Draw finish line with conditional color based on enablement
        if finish_line_enabled:
            pygame.draw.rect(screen, GREEN, finish_line)
        else:
            pygame.draw.rect(screen, BLUE, finish_line)

        # Draw coins
        for coin in coin_positions:
            pygame.draw.circle(screen, YELLOW, (coin[0] + player_size // 2, coin[1] + player_size // 2), player_size // 2)

        # Draw player
        pygame.draw.rect(screen, RED, player_rect)

        # Render score and timer
        render_text(f"Score: {score}", (SCREEN_WIDTH - 100, 20))
        render_text(f"Time: {max(0, int(timer))}", (100, 20))

        # Display win or game over message
        if game_won:
            render_text(f"You win! Final Score: {score}", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            player_speed = 0
        elif game_over:
            render_text("Time's up! Game Over.", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            player_speed = 0

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(30)

pygame.quit()
