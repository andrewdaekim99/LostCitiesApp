import pygame
import os
import sys
import random
from collections import defaultdict


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
colors = ["red", "green", "blue", "yellow", "white", "purpler"]
values = [0] + list(range(2, 11))  # 0 = investment card

# Build full deck: 3 investment cards per color, 2–10 once each
deck = []
for color in colors:
    deck += [(color, 0)] * 3  # 3 investment cards
    deck += [(color, v) for v in range(2, 11)]

# Shuffle and deal 8 random cards
random.shuffle(deck)
player_hand = deck[:8]

# --- Group and sort --
grouped = defaultdict(list)
for color, value in player_hand:
    grouped[color].append((color, value))

# Sort within each color group
for color in grouped:
    grouped[color].sort(key=lambda x: x[1])

# Define the color display order
color_order = colors

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

# Game state
selected_card_index = None
expeditions = {color: [] for color in colors}

# Create clickable expedition zones
expedition_zones = {}
for i, color in enumerate(colors):
    x = 50 + i * 130
    y = 100
    expedition_zones[color] = pygame.Rect(x, y, 100, 150)
    
# Game loop
running = True
while running:
    SCREEN.fill((20, 20, 20))  # dark background

    # Draw expedition zones
    for color, rect in expedition_zones.items():
        pygame.draw.rect(SCREEN, (100, 100, 100), rect, 2)
        if expeditions[color]:
            top_card = expeditions[color][-1]
            img = load_card_image(*top_card)
            SCREEN.blit(img, rect.topleft)

    # Draw player hand
    for i, (img, rect, (color, value)) in enumerate(card_sprites):
        rect_to_draw = rect.move(0, -20) if i ==selected_card_index else rect
        SCREEN.blit(img, rect_to_draw)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            #Clicked a card?
            for i, (img, rect, (color, value)) in enumerate(card_sprites):
                if rect.collidepoint(event.pos):
                    selected_card_index = i
                    break
        else:
            # If a card is selected, check if expedition zone was clicked
            if selected_card_index is not None:
                selected_card = card_sprites[selected_card_index][2]
                selected_color = selected_card[0]

                if expedition_zones[selected_color].collidepoint(event.pos):
                    pile = expeditions[selected_color]
                    if not pile or selected_card[1] >= pile[-1][1] or selected_card[1] == 0:
                        expeditions[selected_color].append(selected_card)
                        del card_sprites[selected_card_index]
                        selected_card_index = None

                        # Recalculate layout
                        for j, (img, _, card) in enumerate(card_sprites):
                            new_x = start_x + j * (img.get_width() + spacing)
                            new_rect = img.get_rect(topleft=(new_x, 400))
                            card_sprites[j] = (img, new_rect, card)

    pygame.display.flip()

pygame.quit()
sys.exit()
