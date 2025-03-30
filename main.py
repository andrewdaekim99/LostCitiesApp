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

# load deck image
draw_pile_img = pygame.image.load("assets/deck/draw_pile.png")
draw_pile_rect = draw_pile_img.get_rect(topleft=(WIDTH - 150, HEIGHT // 2 - 75))


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

# temporarily build card_sprites
for color, value in sorted_hand:
    img = load_card_image(color, value)
    rect = img.get_rect() # placeholder, position will be set later
    card_sprites.append((img, rect, (color, value)))

# Center and poisiton the hand after it's built
def layout_hand():
    hand_y = HEIGHT - 150
    spacing = 20
    card_widths = [img.get_width() for img, _, _ in card_sprites]
    total_hand_width = sum(card_widths) + spacing * (len(card_sprites) - 1)
    start_x = (WIDTH -  total_hand_width) // 2

    x = start_x
    for i, (img, _, card) in enumerate(card_sprites):
        rect = img.get_rect(topleft=(x, hand_y))
        card_sprites[i] = (img, rect, card)
        x += img.get_width() + spacing

layout_hand() # calls after building the hand
# Game state
selected_card_index = None
must_draw = False # conditional for when a player is or is not allowed to draw a card
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

    # load draw pile deck
    SCREEN.blit(draw_pile_img, draw_pile_rect.topleft)
    font = pygame.font.SysFont(None, 24)
    deck_count = font.render(f"{len(deck)}", True, (255, 255, 255))
    SCREEN.blit(deck_count, draw_pile_rect.move(10, -20))

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

    # Draw reminder if player must draw
    if must_draw:
        msg = font.render("You must draw a card!", True, (255, 100, 100))
        SCREEN.blit(msg, (WIDTH // 2 - 100, HEIGHT // 2 - 200))

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if draw_pile_rect.collidepoint(event.pos):
                    if must_draw and len(card_sprites) < 8 and deck:
                        color, value = deck.pop()
                        img = load_card_image(color, value)
                        rect = img.get_rect() # placeholder
                        card_sprites.append((img, rect, (color, value)))
                        layout_hand() # re-layout the new hand
                        selected_card_index = None
                        must_draw = False
            # First: check if a card was clicked
            if not must_draw:
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

                                    layout_hand()
                                    must_draw = True



    pygame.display.flip()

pygame.quit()
sys.exit()
