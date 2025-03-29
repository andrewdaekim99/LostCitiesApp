import pygame
import os
import sys
import random

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

# Define available colors and values
colors = ["red", "green", "blue", "yellow", "white"]
values = [0] + list(range(2, 11))  # 0 = investment card

# Build full deck: 3 investment cards per color, 2–10 once each
deck = []
for color in colors:
    deck += [(color, 0)] * 3  # 3 investment cards
    deck += [(color, v) for v in range(2, 11)]

# Shuffle and deal 8 random cards
random.shuffle(deck)
player_hand = deck[:8]

# --- NEW: Group and sort ---
from collections import defaultdict

grouped = defaultdict(list)
for color, value in player_hand:
    grouped[color].append((color, value))

# Sort within each color group
for color in grouped:
    grouped[color].sort(key=lambda x: x[1])

# Define the color display order
color_order = ["red", "green", "blue", "yellow", "white"]

# Flatten into a sorted display hand
sorted_hand = []
for color in color_order:
    sorted_hand.extend(grouped[color])

# --- Load images and assign positions ---
card_sprites = []
spacing = 20
start_x = 50

for i, (color, value) in enumerate(sorted_hand):
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
