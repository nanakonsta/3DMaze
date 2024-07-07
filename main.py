#main.py
#Σε σημεία του κώδικα όπου δεν αναφέρεται συγκεκριμένο όνομα, υλοποιήθηκαν συνεργατικά και από τους δύο.

#Imports
import pygame
import random
import time
import math
import heapq
import networkx as nx # needs pip install networkx
# Η networkx χρησιμοποιείται για να απεικονίσει το λαβύρινθο σαν γράφημα, ώστε να μπορούμε να
# ελέγξουμε αν το μονοπάτι μεταξύ παίκττη και εξόδου είναι προσβάσιμο


# Initialize Pygame
# κάνουυμε initialize την pygame ώστε να δημιουργηθεί το παράθυρο του παιχνιδιού και 
# να ορίσουμε κάποια βασικά μεγέθη (screen dimensions, colours, fonts...)
pygame.init()

# Screen dimensions and settings- create display
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)  # Player color
GREEN = (0, 255, 0) # Exit Point Colour

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("3D Maze")

# Maze settings: dimensions, tile size
TILE_SIZE = 40
MAZE_WIDTH, MAZE_HEIGHT = (SCREEN_WIDTH // 2) // TILE_SIZE, SCREEN_HEIGHT // TILE_SIZE

# Raycasting settings
FOV = 60 * math.pi / 180  # Field of view in radians
HALF_FOV = FOV / 2
CASTED_RAYS = 120
STEP_ANGLE = FOV / CASTED_RAYS
MAX_DEPTH = SCREEN_WIDTH // 4 # Adjusted for split-screen
SCALE = SCREEN_WIDTH // (2 * CASTED_RAYS)

# Loading Fonts and Sounds
# Αθηνά Κωνσταντινίδου
font = pygame.font.SysFont(None, 55)
small_font = pygame.font.SysFont(None, 35)
start_sound = pygame.mixer.Sound("start.wav")
ukelele_sound = pygame.mixer.Sound("ukelele.wav")
# Copyright ukelele.wav composed by Athina Konstantinidou
win_sound = pygame.mixer.Sound("win.wav")
lose_sound = pygame.mixer.Sound("lose.wav")

# Timer settings
# Ο χρόνος μετρά αντίστροφα
#set initial timer values 
start_time = 60
time_left = start_time

# Player settings: player speed, position, radius
## player_x = SCREEN_WIDTH // 4
## player_y = SCREEN_HEIGHT // 4
## player_angle = 0
player_speed = 2
player_radius = 15
player_pos = [0, 0]  # Will be updated with random start

# Generate a random maze position
# maze, (start_x, start_y) = generate_maze(MAZE_WIDTH, MAZE_HEIGHT)

# Δημήτρης Ζαμπάρας
# Load wall & floor texture
wall_image = pygame.image.load("wall.jpg")
wall_image = pygame.transform.scale(wall_image, (TILE_SIZE, TILE_SIZE))
floor_image = pygame.image.load('floor.jpg')
floor_image = pygame.transform.scale(floor_image, (TILE_SIZE, TILE_SIZE))

# Maze generation function-Δημιουργεί το λαβύρινθο κάθε φορά τυχαία αναδρομικά σαν γράφημα
# Δημιουργείται grid-based maze με walls & passages
# Δημήτρης Ζαμπάρας

def generate_maze(width, height):
    maze = [[1 for _ in range(width)] for _ in range(height)]
    
    # Recursive division to create maze
    def carve_passages_from(cx, cy, maze):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = cx + dx * 2, cy + dy * 2
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1:
                maze[cy + dy][cx + dx] = 0
                maze[ny][nx] = 0
                carve_passages_from(nx, ny, maze)

    # Start carving from a random point
    start_x, start_y = random.randrange(1, width, 2), random.randrange(1, height, 2)
    maze[start_y][start_x] = 0
    carve_passages_from(start_x, start_y, maze)

    # Add boundary walls around the maze
    # Βάζουμε όρια για να μην βγει οπαίκτης εκτός παραθύρου
    for i in range(width):
        maze[0][i] = 1
        maze[height - 1][i] = 1
    for i in range(height):
        maze[i][0] = 1
        maze[i][width - 1] = 1
    
    return maze, (start_x, start_y)


#checking if there is a path between start and end
# Έλεγχος αν μπορεί πάντα να επιτευχθεί ο στόχος
# Κωνσταντινίδου Αθηνά
def is_accessible(maze, start, end):
    graph = nx.Graph()
    height = len(maze)
    width = len(maze[0])

    # Check if start and end positions are within bounds
    start_x, start_y = start
    exit_x, exit_y = end
    if not (0 <= start_x < width and 0 <= start_y < height):
        return False
    if not (0 <= exit_x < width and 0 <= exit_y < height):
        return False
    

    graph = nx.Graph()

    def add_edge_if_valid(x1, y1, x2, y2):
        if 0 <= x2 < width and 0 <= y2 < height and maze[y2][x2] == 0:
            graph.add_edge((x1, y1), (x2, y2))

    # Add nodes and edges for accessible positions    
    for y in range(height):
        for x in range(width):
            if maze[y][x] == 0:
                if x > 0 and maze[y][x-1] == 0:
                    graph.add_edge((x, y), (x-1, y))
                if x < width-1 and maze[y][x+1] == 0:
                    graph.add_edge((x, y), (x+1, y))
                if y > 0 and maze[y-1][x] == 0:
                    graph.add_edge((x, y), (x, y-1))
                if y < height-1 and maze[y+1][x] == 0:
                    graph.add_edge((x, y), (x, y+1))

    # Check if there is a path between start and end
    # Explicitly add start and end nodes
    graph.add_node(start)
    graph.add_node(end)

    return nx.has_path(graph, start, end)

# Συνεργατικά
# function resets the game state when the player wins or loses, 
# generating a new maze, resetting the player's position and angle
def reset_game():
    global maze, start_x, start_y, player_x, player_y, player_angle, start_ticks, exit_x, exit_y, start_time, time_left
    while True:
        maze, (start_x, start_y) = generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
        exit_x, exit_y = random.randrange(1, MAZE_WIDTH, 2), random.randrange(1, MAZE_HEIGHT, 2)
        if maze[exit_y][exit_x] == 0:
            print(f"Start position: ({start_x}, {start_y})")
            print(f"Exit position: ({exit_x}, {exit_y})")
            if is_accessible(maze, (start_x, start_y), (exit_x, exit_y)):
                break

    # τυχαία αρχική θέση παίκτη αλλά όχι σε τοίχο            
    player_x = start_x * TILE_SIZE + TILE_SIZE // 2
    player_y = start_y * TILE_SIZE + TILE_SIZE // 2
    #player_angle: rotation του παίκτη
    player_angle = random.uniform(0, 2 * math.pi)
    start_ticks = pygame.time.get_ticks()
    
    exit_x = exit_x * TILE_SIZE + TILE_SIZE // 2
    exit_y = exit_y * TILE_SIZE + TILE_SIZE // 2

    #Ιδέα για μέλλον: 2ο level με λιγότερο χρόνο
    # start_time = max(10, start_time - 5)
    # time_left = start_time
#initial game setup
reset_game() #κάνει reset το παιχνίδι όταν ο παίκτης χάσει ή κερδίσει, συμπεριλαμβανομένου
             # δημιουργία νέου λαβυρίνθου, reset player's starting position and angle & timer update


# Draw the maze on the screen
# Helper function to draw the 2D top-down view of the maze
#Δημήτρης Ζαμπάρας
def draw_maze():
    for y in range(MAZE_HEIGHT):
        for x in range(MAZE_WIDTH):
            if maze[y][x] == 1:
                screen.blit(wall_image, (x * TILE_SIZE, y * TILE_SIZE))
            else:
                screen.blit(floor_image, (x * TILE_SIZE, y * TILE_SIZE))
    pygame.draw.rect(screen, GREEN, (exit_x - TILE_SIZE // 2, exit_y - TILE_SIZE // 2, TILE_SIZE, TILE_SIZE))


# Raycasting function για 3D Rendering
# Δημιουργεί 3D effect του λαβυρίνθου από first-person perspective, μέσω διασταυρώσεων rays με maze
# Αθηνά Κωνσταντινίδου
def cast_rays():
    start_angle = player_angle - HALF_FOV
    for ray in range(CASTED_RAYS):
        for depth in range(MAX_DEPTH):
            target_x = player_x + math.cos(start_angle) * depth
            target_y = player_y + math.sin(start_angle) * depth
            col = int(target_x // TILE_SIZE)
            row = int(target_y // TILE_SIZE)
            if col < 0 or col >= MAZE_WIDTH or row < 0 or row >= MAZE_HEIGHT:
                break
            if maze[row][col] == 1:
                color = 255 / (1 + depth * depth * 0.0001)
                depth *= math.cos(player_angle - start_angle)
                wall_height = 12000 / (depth + 0.0001)
                wall_height = min(SCREEN_HEIGHT, wall_height)
                texture = pygame.transform.scale(wall_image, (SCALE, int(wall_height)))
                screen.blit(texture, ((SCREEN_WIDTH // 2) + ray * SCALE, (SCREEN_HEIGHT // 2) - wall_height // 2))
                break
        start_angle += STEP_ANGLE


# Δημήτρης Ζαμπάρας
# Check & handle Player for collision with walls
# Εξασφαλίζει ότι ο παίκτης δεν κινείται μέσα σε τοίχους
def check_collision(x, y):
    col = int(x // TILE_SIZE)
    row = int(y // TILE_SIZE)
    if maze[row][col] == 1:
        return True
    return False


# MAIN GAME LOOP
# to handle events, move the player, draw elements, update timer, check win/lose conditions
running = True
clock = pygame.time.Clock()

# Start the game with the start sound
start_sound.play()
ukelele_sound.play(-1)  # Play background music in a loop

while running:

        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move the player # ΚΩΝΣΤΑΝΤΙΝΙΔΟΥ ΑΘΗΝΑ
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_angle -= 0.05
    if keys[pygame.K_RIGHT]:
        player_angle += 0.05
    if keys[pygame.K_UP]:
        new_x = player_x + player_speed * math.cos(player_angle)
        new_y = player_y + player_speed * math.sin(player_angle)
        if not check_collision(new_x, new_y):
            player_x, player_y = new_x, new_y
    if keys[pygame.K_DOWN]:
        new_x = player_x - player_speed * math.cos(player_angle)
        new_y = player_y - player_speed * math.sin(player_angle)
        if not check_collision(new_x, new_y):
            player_x, player_y = new_x, new_y


    screen.fill(BLACK)

    draw_maze()
    cast_rays()

    # Draw the player on the screen
    ##pygame.draw.rect(screen, RED, pygame.Rect(player_pos[0], player_pos[1], TILE_SIZE, TILE_SIZE))
    pygame.draw.circle(screen, RED, (int(player_x), int(player_y)), player_radius)

    # Timer and Win/Lose Conditions
    # updates the timer, checks if the player wins or loses and plays corresponding sounds
    time_left = start_time - (pygame.time.get_ticks() - start_ticks) // 1000
    timer_text = font.render(f"Time left: {time_left}", True, WHITE)
    screen.blit(timer_text, (10, 10))


    # Losing condition
    # Αν τελειώσει ο χρόνος ο παίκτης χάνει, εμφανίζεται Game Over στην οθόνη και ακούγεται σχετικός ήχος
    if time_left <= 0:
        lose_sound.play()
        font = pygame.font.Font(None, 72)
        defeat_surface = font.render('Game Over!', True, (255, 0, 0))
        screen.blit(defeat_surface, (SCREEN_WIDTH // 2 - defeat_surface.get_width() // 2, SCREEN_HEIGHT // 2 - defeat_surface.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        reset_game()
        continue
        #defeat_data = pygame.image.tostring(defeat_surface, "RGBA", True)
        #running = False  # End the game for simplicity, 
                         # you may want to reset the level or similar
        
      
    # Win condition
    # Αν ο παίκτης προλάβει να φτάσει στην έξοδο πριν τη λήξη του χρόνου, εμφανίζεται Victory και ακούγεται σχετικός ήχος
    if abs(player_x - exit_x) < TILE_SIZE // 2 and abs(player_y - exit_y) < TILE_SIZE // 2:
        win_sound.play()
        victory_surface = font.render('Victory!', True, (255, 0, 0))
        screen.blit(victory_surface, (SCREEN_WIDTH // 2 - victory_surface.get_width() // 2, SCREEN_HEIGHT // 2 - victory_surface.get_height() // 2))
        #victory_data = pygame.image.tostring(victory_surface, "RGBA", True)
        #running = False  # End the game for simplicity, 
                        # you may want to reset the level or similar
        pygame.display.flip()
        pygame.time.wait(3000)
        reset_game() #Should it stay or should it go?
        continue



    # Update the display
    # Refreshes the display and controls the frame rate
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

