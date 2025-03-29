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
colors = ["red", "green", "blue", "yellow", "white", "purple"]
values = [0] + list(range(2, 11))  # 0 = investment card


# Load expedition zone background images
expedition_bg_images = {}
for color in colors:
    filename = f"expedition_{color}.png"
    path = os.path.join("assets", "expeditions", filename)
    try:
        expedition_bg_images[color] = pygame.image.load(path)
    except FileNotFoundError:
        print(f"Missing expedition zone image: {path}")
        expedition_bg_images[color] = pygame.Surface((120, 180))  # fallback

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
    x = 50 + i * 140 # spacing
    y = 100
    image = expedition_bg_images[color]
    rect = image.get_rect(topleft=(x,y))
    expedition_zones[color] = rect
    
# Game loop
running = True
while running:
    SCREEN.fill((20, 20, 20))  # dark background

    # Draw expedition zones
    for color, rect in expedition_zones.items():
        bg_img = expedition_bg_images[color]
        SCREEN.blit(bg_img, rect.topleft)

        # If there are cards in the expedition pile, draw the top one centered
        if expeditions[color]:
            top_card = expeditions[color][-1]
            card_img = load_card_image(*top_card)

            # Center the card over the expedition zone
            card_rect = card_img.get_rect(center=rect.center)
            SCREEN.blit(card_img, card_rect.topleft)

    # Draw player hand
    for i, (img, rect, (color, value)) in enumerate(card_sprites):
        rect_to_draw = rect.move(0, -20) if i ==selected_card_index else rect
        SCREEN.blit(img, rect_to_draw)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # First: check if a card was clicked
            for i, (img, rect, (color, value)) in enumerate(card_sprites):
                if rect.collidepoint(event.pos):
                    selected_card_index = i
                    break
            else:
                # If not clicking a card, check if clicked an expedition zone
                for color, rect in expedition_zones.items():
                    if rect.collidepoint(event.pos) and selected_card_index is not None:
                        selected_card = card_sprites[selected_card_index][2]
                        selected_color = selected_card[0]

                        if selected_color == color:
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
