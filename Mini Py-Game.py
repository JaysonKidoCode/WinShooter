import pygame
import math
import time
import random

# Initialize pygame
pygame.init()

# Game Variables
window_size = 500
screen = pygame.display.set_mode((window_size, window_size), pygame.RESIZABLE)
pygame.display.set_caption("Expanding Window Game")
clock = pygame.time.Clock()

# Player Variables
player_radius = 20
player_color = (255, 255, 255)  # White player
player_pos = [window_size // 2, window_size // 2]
player_speed = 5

# Gun Variables
gun_color = (200, 200, 200)  # Light grey gun
gun_length = 30
gun_width = 8
gun_offset = 50  # Distance from player to the gun

# Bullet Variables
bullet_speed = 10
bullet_color = (0, 255, 0)  # Green bullet
bullet_width = 15
bullet_height = 5  # Oval shape dimensions
last_shot_time = 0
bullet_delay = 0.35  # 1 bullet per 0.35 seconds

# Particle Variables
particles = []

# Game State
bullets = []
running = True
game_over = False

# Expanding window control
expand_rate = 50 / 5  # Expand 50 pixels over 5 frames
expanding = False
expansion_direction = None  # Track direction of expansion (north, south, east, west)
frames_until_expansion = 0  # Number of frames until expansion is complete

# Text Variables
def get_font(size):
    return pygame.font.SysFont(None, size)

restart_message_line_1 = "Press 'r' to"
restart_message_line_2 = "restart"

# Function to display text
def display_text(text, position, font_size):
    font = get_font(font_size)
    text_surface = font.render(text, True, (255, 255, 255))
    screen.blit(text_surface, position)

# Reset game
def reset_game():
    global player_pos, bullets, window_size, game_over, expanding, expansion_direction, particles, frames_until_expansion
    player_pos = [window_size // 2, window_size // 2]
    bullets = []
    window_size = 500
    expanding = False
    expansion_direction = None
    particles = []
    frames_until_expansion = 0  # Reset frame counter
    game_over = False

# Function to create particles on bullet impact
def create_particles(pos):
    for _ in range(10):  # Create 10 particles per bullet impact
        particles.append({
            "pos": [pos[0], pos[1]],
            "vel": [random.uniform(-2, 2), random.uniform(-2, 2)],
            "color": (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255)),
            "life": 1.0  # Life of the particle (1.0 is full, 0 is dead)
        })

# Function to update and draw particles
def update_particles():
    for particle in particles[:]:
        particle["pos"][0] += particle["vel"][0]
        particle["pos"][1] += particle["vel"][1]
        particle["life"] -= 0.05  # Particles fade out over time
        if particle["life"] <= 0:
            particles.remove(particle)
        else:
            alpha = int(255 * particle["life"])
            particle_color = particle["color"] + (alpha,)  # Fade effect
            pygame.draw.circle(screen, particle_color, (int(particle["pos"][0]), int(particle["pos"][1])), 3)

# Main Game Loop
while running:
    clock.tick(60)
    screen.fill((0, 0, 0))

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            reset_game()

    if not game_over:
        # Window shrinking logic
        window_size -= 0.5  # Shrinks 0.5px every frame
        if window_size < 200:  # Limit window from shrinking below a certain size
            window_size = 200
        screen = pygame.display.set_mode((int(window_size), int(window_size)), pygame.RESIZABLE)

        # Handle player movement with WASD keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player_pos[1] - player_radius > 0:
            player_pos[1] -= player_speed
        if keys[pygame.K_s] and player_pos[1] + player_radius < window_size:
            player_pos[1] += player_speed
        if keys[pygame.K_a] and player_pos[0] - player_radius > 0:
            player_pos[0] -= player_speed
        if keys[pygame.K_d] and player_pos[0] + player_radius < window_size:
            player_pos[0] += player_speed

        # Player drawing
        pygame.draw.circle(screen, player_color, player_pos, player_radius)

        # Handle shooting bullets
        mouse_pos = pygame.mouse.get_pos()
        time_since_last_shot = time.time() - last_shot_time
        if (pygame.mouse.get_pressed()[0] or pygame.key.get_pressed()[pygame.K_SPACE]) and time_since_last_shot >= bullet_delay:
            # Calculate gun's direction
            dx, dy = mouse_pos[0] - player_pos[0], mouse_pos[1] - player_pos[1]
            angle = math.atan2(dy, dx)

            # Determine bullet starting position (at the end of the gun)
            bullet_start_x = player_pos[0] + (gun_length + gun_offset) * math.cos(angle)
            bullet_start_y = player_pos[1] + (gun_length + gun_offset) * math.sin(angle)
            bullets.append([bullet_start_x, bullet_start_y, angle])
            last_shot_time = time.time()

        # Update and draw bullets (as ovals)
        for bullet in bullets[:]:
            bullet[0] += bullet_speed * math.cos(bullet[2])
            bullet[1] += bullet_speed * math.sin(bullet[2])
            pygame.draw.ellipse(screen, bullet_color, (int(bullet[0]), int(bullet[1]), bullet_width, bullet_height))

            # Detect if the bullet hits the window edges
            if bullet[0] <= 0:  # Left edge
                expansion_direction = 'west'
                create_particles([0, bullet[1]])
                bullets.remove(bullet)
            elif bullet[0] >= window_size:  # Right edge
                expansion_direction = 'east'
                create_particles([window_size, bullet[1]])
                bullets.remove(bullet)
            elif bullet[1] <= 0:  # Top edge
                expansion_direction = 'north'
                create_particles([bullet[0], 0])
                bullets.remove(bullet)
            elif bullet[1] >= window_size:  # Bottom edge
                expansion_direction = 'south'
                create_particles([bullet[0], window_size])
                bullets.remove(bullet)

        # Handle window expansion
        if expansion_direction:
            if frames_until_expansion < 5:
                frames_until_expansion += 1
                if frames_until_expansion <= 5:  # Expand only 50 pixels over 5 frames
                    if expansion_direction in ['north', 'south']:
                        window_size += expand_rate
                    elif expansion_direction in ['east', 'west']:
                        window_size += expand_rate

            # Ensure player doesn't disappear for 1 frame
            player_visible = True

            if frames_until_expansion >= 5:  # Reset expansion direction after expansion completes
                expansion_direction = None  
                frames_until_expansion = 0  # Reset frame counter

        # Draw the gun (manually rotated towards mouse without transforming)
        dx, dy = mouse_pos[0] - player_pos[0], mouse_pos[1] - player_pos[1]
        angle = math.atan2(dy, dx)

        # Gun's end points relative to the player
        gun_end_x = player_pos[0] + (gun_length + gun_offset) * math.cos(angle)
        gun_end_y = player_pos[1] + (gun_length + gun_offset) * math.sin(angle)

        # Gun's starting point (the end near the player)
        gun_start_x = player_pos[0] + gun_offset * math.cos(angle)
        gun_start_y = player_pos[1] + gun_offset * math.sin(angle)

        # Draw the gun as a line from the player to the gun's end position
        pygame.draw.line(screen, gun_color, (gun_start_x, gun_start_y), (gun_end_x, gun_end_y), gun_width)

        # Check collision between player and window edges
        if player_pos[0] - player_radius <= 0 or player_pos[0] + player_radius >= window_size or \
           player_pos[1] - player_radius <= 0 or player_pos[1] + player_radius >= window_size:
            game_over = True

    if game_over:
        # Dynamically adjust font size based on the window size
        font_size = int(window_size // 10)  # Set the font size to be 1/10th of the window size
        line_spacing = font_size // 2  # Set spacing between lines
        
        # Render and display both lines of the message in the center of the screen
        text_width_line_1 = get_font(font_size).size(restart_message_line_1)[0]
        text_width_line_2 = get_font(font_size).size(restart_message_line_2)[0]
        text_height = get_font(font_size).size(restart_message_line_1)[1]

        # Calculate positions to center both lines
        position_line_1 = ((window_size - text_width_line_1) // 2, (window_size - text_height) // 2 - line_spacing)
        position_line_2 = ((window_size - text_width_line_2) // 2, (window_size - text_height) // 2 + line_spacing)

        display_text(restart_message_line_1, position_line_1, font_size)
        display_text(restart_message_line_2, position_line_2, font_size)

    # Update particles
    update_particles()

    pygame.display.flip()

pygame.quit()
