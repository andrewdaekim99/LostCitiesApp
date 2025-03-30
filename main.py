import pygame
import os
import sys
import random
from collections import defaultdict


# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 1000, 800
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

# height of the hand
card_width = 100
total_hand_width = len(card_sprites) * card_width + (len(card_sprites) - 1) * spacing
start_x = (WIDTH - total_hand_width) // 2
hand_y = HEIGHT - 150

# initial hand layout
for i, (color, value) in enumerate(sorted_hand):
    img = load_card_image(color, value)
    x = start_x + i * (card_width + spacing)
    rect = img.get_rect(topleft=(x, hand_y))
    card_sprites.append((img, rect, (color, value)))

# Game state
selected_card_index = None
expeditions = {color: [] for color in colors}

# expedition zone width setup
zone_width = 120
spacing = 20
total_zone_width = len(colors) * zone_width + (len(colors) - 1) * spacing
start_x = (WIDTH - total_zone_width) // 2

# Create clickable expedition zones
expedition_zones = {}
for i, color in enumerate(colors):
    x = start_x + i * (zone_width + spacing)
    y = 40
    image = expedition_bg_images[color]
    rect = image.get_rect(topleft=(x,y))
    expedition_zones[color] = rect
    
# Move validation
def is_valid_play(pile, card_value):
    if not pile:
        return True
    top_value = pile[-1][1]
    if card_value == 0:
        return top_value == 0  # only play 0 on 0
    if top_value == 0:
        return True  # first number after 0
    return card_value >= top_value  # ascending only

# Game loop
running = True
while running:
    SCREEN.fill((20, 20, 20))  # dark background

    # Draw expedition zones
    for color, rect in expedition_zones.items():
        bg_img = expedition_bg_images[color]
        SCREEN.blit(bg_img, rect.topleft)

        # If there are cards in the expedition pile, place them cascading down under the zone
        if expeditions[color]:
            for i, (c, v) in enumerate(expeditions[color]):
                card_img = load_card_image(c, v)
                # Offset each card by 30px vertically below the expedition zone
                card_rect = card_img.get_rect(midtop=(rect.centerx, rect.bottom + i * 30))
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
                            if is_valid_play(pile, selected_card[1]):
                                expeditions[selected_color].append(selected_card)
                                del card_sprites[selected_card_index]
                                selected_card_index = None

                                # Recalculate layout
                                hand_y = HEIGHT - 150 # anchor to bottom of screen
                                for j, (img, _, card) in enumerate(card_sprites):
                                    new_x = start_x + j * (img.get_width() + spacing)
                                    new_rect = img.get_rect(topleft=(new_x, hand_y))
                                    card_sprites[j] = (img, new_rect, card)



    pygame.display.flip()

pygame.quit()
sys.exit()
