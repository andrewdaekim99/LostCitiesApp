import pygame
import os
import sys

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 1000, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lost Cities")

# Load a card image
def load_card_image(color, value):
    filename = f"{color}_{value}.png"
    path = os.path.join("assets", "cards", filename)
    try:
        return pygame.image.load(path)
    except FileNotFoundError:
        print(f"Image not found: {path}")
        return pygame.Surface((100, 150))  # blank placeholder

# Example hand: 8 cards of mixed colors/values
player_hand = [
    ("red", 3), ("green", 4), ("blue", 7),
    ("yellow", 4), ("purple", 10), ("red", 5),
    ("blue", 2), ("green", 9)
]

# Load images and positions
card_sprites = []
spacing = 20
start_x = 50

for i, (color, value) in enumerate(player_hand):
    img = load_card_image(color, value)
    rect = img.get_rect(topleft=(start_x + i * (img.get_width() + spacing), 400))
    card_sprites.append((img, rect, (color, value)))

# Game loop
running = True
while running:
    SCREEN.fill((20, 20, 20))  # dark background

    for img, rect, _ in card_sprites:
        SCREEN.blit(img, rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            for img, rect, (color, value) in card_sprites:
                if rect.collidepoint(event.pos):
                    print(f"Clicked: {color} {value}")

    pygame.display.flip()

pygame.quit()
sys.exit()
