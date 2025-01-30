import pygame
import random
import sys
import json
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Slicer")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load Fonts
font_path = "assets/fonts/Arcade.ttf"  # Ensure this font is in the folder
if not os.path.exists(font_path):
    print(f"Font file not found: {font_path}")
    pygame.quit()
    sys.exit()
font = pygame.font.Font(font_path, 24)
large_font = pygame.font.Font(font_path, 48)

# Load Sounds
def load_sound(path):
    if os.path.exists(path):
        return pygame.mixer.Sound(path)
    else:
        print(f"Sound file not found: {path}")
        return None

laser_sound = load_sound("assets/sounds/laser.wav")
slice_sound = load_sound("assets/sounds/slice.wav")
explosion_sound = load_sound("assets/sounds/explosion.wav")
background_music = "assets/sounds/background.mp3"  # Looping audio file

# Function to load and resize images
def load_and_resize_image(path, max_size):
    """
    Loads an image from the given path and resizes it to fit within max_size while maintaining aspect ratio.
    """
    if not os.path.exists(path):
        print(f"Image file not found: {path}")
        pygame.quit()
        sys.exit()
    image = pygame.image.load(path).convert_alpha()
    image_rect = image.get_rect()
    width_ratio = max_size[0] / image_rect.width
    height_ratio = max_size[1] / image_rect.height
    scale_ratio = min(width_ratio, height_ratio, 1)  # Do not upscale
    new_size = (int(image_rect.width * scale_ratio), int(image_rect.height * scale_ratio))
    return pygame.transform.scale(image, new_size)

# Define maximum sizes for each type of image
MAX_SIZE_FRUIT = (128, 128)         # Doubled from (64, 64)
MAX_SIZE_BOMB = (100, 100)          # Enlarged from (50, 50)
MAX_SIZE_ICE = (100, 100)           # Enlarged from (50, 50)
MAX_SIZE_SHIP = (150, 150)          # Increased size
MAX_SIZE_CHARACTER = (100, 100)
MAX_SIZE_MEDAL = (100, 100)         # Size for medals

# Load Images with resizing
fruit_images = {
    "apple": load_and_resize_image("assets/images/fruit_apple.png", MAX_SIZE_FRUIT),
    "banana": load_and_resize_image("assets/images/fruit_banana.png", MAX_SIZE_FRUIT),
    "orange": load_and_resize_image("assets/images/fruit_orange.png", MAX_SIZE_FRUIT),
    "strawberry": load_and_resize_image("assets/images/fruit_strawberry.png", MAX_SIZE_FRUIT),
    "watermelon": load_and_resize_image("assets/images/fruit_watermelon.png", MAX_SIZE_FRUIT),
    "pineapple": load_and_resize_image("assets/images/fruit_pineapple.png", MAX_SIZE_FRUIT),
}

bomb_image = load_and_resize_image("assets/images/bomb.png", MAX_SIZE_BOMB)
ice_image = load_and_resize_image("assets/images/ice.png", MAX_SIZE_ICE)

# Player Ships
ship_images = {
    "ship1": load_and_resize_image("assets/images/ship1.png", MAX_SIZE_SHIP),
    "ship2": load_and_resize_image("assets/images/ship2.png", MAX_SIZE_SHIP),
    "ship3": load_and_resize_image("assets/images/ship3.png", MAX_SIZE_SHIP),
}

# Player Characters
character_images = {
    "char1": load_and_resize_image("assets/images/char1.png", MAX_SIZE_CHARACTER),
    "char2": load_and_resize_image("assets/images/char2.png", MAX_SIZE_CHARACTER),
    "char3": load_and_resize_image("assets/images/char3.png", MAX_SIZE_CHARACTER),
}

# Load Medal Images for Combo Rewards
medal_images = {
    "bronze": load_and_resize_image("assets/images/bronze_medal.png", MAX_SIZE_MEDAL),
    "silver": load_and_resize_image("assets/images/silver_medal.png", MAX_SIZE_MEDAL),
    "gold": load_and_resize_image("assets/images/gold_medal.png", MAX_SIZE_MEDAL),
}

# Verify that all images are loaded
for key, img in fruit_images.items():
    if img is None:
        print(f"Missing fruit image: {key}")
        pygame.quit()
        sys.exit()

if bomb_image is None or ice_image is None:
    pygame.quit()
    sys.exit()

for key, img in ship_images.items():
    if img is None:
        print(f"Missing ship image: {key}")
        pygame.quit()
        sys.exit()

for key, img in character_images.items():
    if img is None:
        print(f"Missing character image: {key}")
        pygame.quit()
        sys.exit()

for key, img in medal_images.items():
    if img is None:
        print(f"Missing medal image: {key}")
        pygame.quit()
        sys.exit()

# Background Music
if os.path.exists(background_music):
    pygame.mixer.music.load(background_music)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # Loop playback
else:
    print(f"Background music file not found: {background_music}")

# Player settings
player_speed = 10

# Laser settings
laser_width = 5
laser_height = 20
laser_speed = 15
max_lasers = 3

# Game objects
objects = []
object_spawn_delay = 1000  # milliseconds
last_spawn_time = pygame.time.get_ticks()

# Difficulty levels with adjusted speeds
difficulty_levels = {
    "easy": {"speed": 3, "spawn_delay": 1500},    # Slower speed and slower spawn
    "medium": {"speed": 5, "spawn_delay": 1000},
    "hard": {"speed": 7, "spawn_delay": 800}
}
current_difficulty = "easy"

# Game state
score = 0
game_over = False
combo_count = 0
combo_time = 1000  # milliseconds
last_combo_time = 0
freeze_time_remaining = 0
is_frozen = False
current_medal = None  # To track the current medal to display

# Best scores file
scores_file = "scores.json"

# Reward system thresholds
reward_thresholds = [10, 20, 30, 50]

# Medal thresholds
medal_thresholds = {
    "bronze": 3,   # 3 combos
    "silver": 5,   # 5 combos
    "gold": 10     # 10 combos
}

# Multi-language support
languages = {
    "en": {
        "title": "Fruit Slicer",
        "easy": "Press 1 for Easy",
        "medium": "Press 2 for Medium",
        "hard": "Press 3 for Hard",
        "game_over": "Game Over",
        "final_score": "Final Score: ",
        "enter_name": "Enter your name: ",
        "best_scores": "Best Scores",
        "press_any_key": "Press any key to continue",
        "select_ship": "Select Your Ship:",
        "select_character": "Select Your Character:",
        "ship1": "Press 1 for Ship 1",
        "ship2": "Press 2 for Ship 2",
        "ship3": "Press 3 for Ship 3",
        "char1": "Press 1 for Character 1",
        "char2": "Press 2 for Character 2",
        "char3": "Press 3 for Character 3",
        "score": "Score",
        "reward_unlocked": "Reward Unlocked: {points} Points!",
        "select_name": "Select Your Name from Top 10 or Enter New:",
        "name_exists": "Press the number corresponding to your name:",
        "enter_new_name": "Press N to enter a new name",
        "combo_reward": "Combo Reward!",
        "freeze_time": "Frozen: {seconds}s",
        "next_level": "Next Level: {level}",
        "time_up": "Time's Up!",
        "retry_easy": "Do you want to retry Easy level? Press Y for Yes or N for No."
    },
    "fr": {
        "title": "Trancheur de Fruits",
        "easy": "Appuyez sur 1 pour Facile",
        "medium": "Appuyez sur 2 pour Moyen",
        "hard": "Appuyez sur 3 pour Difficile",
        "game_over": "Jeu Terminé",
        "final_score": "Score Final : ",
        "enter_name": "Entrez votre nom : ",
        "best_scores": "Meilleurs Scores",
        "press_any_key": "Appuyez sur une touche pour continuer",
        "select_ship": "Sélectionnez Votre Vaisseau :",
        "select_character": "Sélectionnez Votre Personnage :",
        "ship1": "Appuyez sur 1 pour Vaisseau 1",
        "ship2": "Appuyez sur 2 pour Vaisseau 2",
        "ship3": "Appuyez sur 3 pour Vaisseau 3",
        "char1": "Appuyez sur 1 pour Personnage 1",
        "char2": "Appuyez sur 2 pour Personnage 2",
        "char3": "Appuyez sur 3 pour Personnage 3",
        "score": "Score",
        "reward_unlocked": "Récompense Débloquée : {points} Points !",
        "select_name": "Sélectionnez Votre Nom dans le Top 10 ou Entrez un Nouveau :",
        "name_exists": "Appuyez sur le numéro correspondant à votre nom :",
        "enter_new_name": "Appuyez sur N pour entrer un nouveau nom",
        "combo_reward": "Récompense Combo!",
        "freeze_time": "Gelé : {seconds}s",
        "next_level": "Niveau Suivant : {level}",
        "time_up": "Le Temps Est Écoulé !",
        "retry_easy": "Voulez-vous réessayer le niveau Facile ? Appuyez sur Y pour Oui ou N pour Non."
    }
}
current_language = "en"

# Player name
player_name = ""

# Selected ship and character
selected_ship = "ship1"
selected_character = "char1"

# Define game states
STATE_MENU = "MENU"
STATE_SELECT_NAME = "SELECT_NAME"
STATE_GAME = "GAME"
STATE_GAME_OVER = "GAME_OVER"

# Define classes for better structure
class Player:
    def __init__(self):
        self.speed = player_speed
        self.update_image()
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 10  # Slightly above the bottom

    def update_image(self):
        # Only load the ship image for gameplay
        ship_image = ship_images.get(selected_ship, ship_images["ship1"])
        self.image = ship_image
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def move_left(self):
        if self.x > 0:
            self.x -= self.speed

    def move_right(self):
        if self.x < WIDTH - self.width:
            self.x += self.speed

class Laser:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = laser_width
        self.height = laser_height

    def move(self):
        self.y -= laser_speed

    def draw(self):
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.width, self.height))  # Red

class GameObject:
    def __init__(self, obj_type, scale=1.0):
        self.type = obj_type
        self.speed = difficulty_levels[current_difficulty]["speed"]
        self.y = 0
        self.scale = scale
        if self.type == "fruit":
            self.name = random.choice(list(fruit_images.keys()))
            base_image = fruit_images[self.name]
            if self.scale != 1.0:
                self.image = pygame.transform.scale(base_image, 
                                (int(base_image.get_width() * self.scale), 
                                 int(base_image.get_height() * self.scale)))
            else:
                self.image = base_image
            self.width = self.image.get_width()
            self.height = self.image.get_height()
            # Ensure the object fits within the screen
            max_x = max(WIDTH - self.width, 0)
            self.x = random.randint(0, max_x)
            self.direction = random.choice([-1, 1])
        elif self.type == "ice":
            self.image = ice_image
            self.width = self.image.get_width()
            self.height = self.image.get_height()
            max_x = max(WIDTH - self.width, 0)
            self.x = random.randint(0, max_x)
        elif self.type == "bomb":
            self.image = bomb_image
            self.width = self.image.get_width()
            self.height = self.image.get_height()
            max_x = max(WIDTH - self.width, 0)
            self.x = random.randint(0, max_x)
            self.direction = random.choice([-1, 1])  # Random horizontal direction

    def move(self):
        if not is_frozen:
            self.y += self.speed
            if self.type in ["fruit", "bomb"]:
                self.x += self.direction * 2  # Horizontal movement
                # Bounce off the edges
                if self.x <= 0 or self.x + self.width >= WIDTH:
                    self.direction *= -1

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

def spawn_object():
    object_type = random.choice(["fruit", "ice", "bomb"])
    objects.append(GameObject(object_type))

def move_objects():
    for obj in objects[:]:
        obj.move()
        if obj.y > HEIGHT:
            objects.remove(obj)

def shoot_laser(player):
    if len(lasers) < max_lasers:
        laser_x = player.x + player.width // 2 - laser_width // 2
        laser_y = player.y
        lasers.append(Laser(laser_x, laser_y))
        if laser_sound:
            laser_sound.play()

def move_lasers():
    for laser in lasers[:]:
        laser.move()
        if laser.y < 0:
            lasers.remove(laser)

def check_collisions(player):
    global score, game_over, player_name, combo_count, last_combo_time, is_frozen, freeze_time_remaining, current_medal
    for laser in lasers[:]:
        for obj in objects[:]:
            if obj.type == "fruit":
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                laser_rect = pygame.Rect(laser.x, laser.y, laser.width, laser.height)
                if rect.colliderect(laser_rect):
                    if slice_sound:
                        slice_sound.play()
                    # Split the fruit into two if it's above a minimum size
                    if obj.width > (MAX_SIZE_FRUIT[0] / 2) and obj.height > (MAX_SIZE_FRUIT[1] / 2):
                        # Create two new fruits with half the scale
                        obj1 = GameObject("fruit", scale=obj.scale / 2)
                        obj1.name = obj.name
                        obj1.x = obj.x
                        obj1.y = obj.y
                        obj1.direction = -1
                        
                        obj2 = GameObject("fruit", scale=obj.scale / 2)
                        obj2.name = obj.name
                        obj2.x = obj.x + obj.width // 2
                        obj2.y = obj.y
                        obj2.direction = 1
                        
                        # Ensure the split fruits fit within the screen
                        obj1.x = max(min(obj1.x, WIDTH - obj1.width), 0)
                        obj2.x = max(min(obj2.x, WIDTH - obj2.width), 0)
                        
                        objects.append(obj1)
                        objects.append(obj2)
                    objects.remove(obj)
                    lasers.remove(laser)
                    score += 1
                    combo_count += 1
                    last_combo_time = pygame.time.get_ticks()
                    check_rewards()
                    break
            elif obj.type == "ice":
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                laser_rect = pygame.Rect(laser.x, laser.y, laser.width, laser.height)
                if rect.colliderect(laser_rect):
                    # Freeze time (stop object movement for 3 seconds)
                    is_frozen = True
                    freeze_time_remaining = 3000  # milliseconds
                    pygame.time.set_timer(pygame.USEREVENT + 2, 1000)  # Update every second
                    objects.remove(obj)
                    lasers.remove(laser)
                    break
            elif obj.type == "bomb":
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                laser_rect = pygame.Rect(laser.x, laser.y, laser.width, laser.height)
                if rect.colliderect(laser_rect):
                    if explosion_sound:
                        explosion_sound.play()
                    game_over = True
                    lasers.remove(laser)
                    break

def draw_score(game_time_remaining):
    score_text = font.render(f"{languages[current_language]['score']}: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    timer_text = font.render(f"Time: {game_time_remaining}", True, WHITE)
    screen.blit(timer_text, (WIDTH - timer_text.get_width() - 10, 10))
    if is_frozen:
        freeze_text = font.render(languages[current_language]['freeze_time'].format(seconds=freeze_time_remaining // 1000), True, (0, 255, 255))
        screen.blit(freeze_text, (WIDTH // 2 - freeze_text.get_width() // 2, 10))

def show_game_over_screen():
    global game_over, game_state
    screen.fill(BLACK)
    game_over_text = large_font.render(languages[current_language]['game_over'], True, WHITE)
    score_text = font.render(f"{languages[current_language]['final_score']} {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 150))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 100))
    pygame.display.flip()
    pygame.time.wait(2000)
    save_score()
    show_best_scores()

def show_menu():
    global current_language, player_name, selected_ship, selected_character, game_state, current_difficulty
    game_state = STATE_MENU
    while game_state == STATE_MENU:
        screen.fill(BLACK)
        title_text = large_font.render(languages[current_language]['title'], True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 250))

        # Language Selection
        lang_text = font.render("Select Language / Sélectionnez la langue:", True, WHITE)
        screen.blit(lang_text, (WIDTH // 2 - lang_text.get_width() // 2, HEIGHT // 2 - 200))
        en_text = font.render("Press E for English", True, WHITE)
        fr_text = font.render("Appuyez sur F pour Français", True, WHITE)
        screen.blit(en_text, (WIDTH // 2 - en_text.get_width() // 2, HEIGHT // 2 - 150))
        screen.blit(fr_text, (WIDTH // 2 - fr_text.get_width() // 2, HEIGHT // 2 - 100))
        pygame.display.flip()

        selecting_language = True
        while selecting_language and game_state == STATE_MENU:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        current_language = "en"
                        selecting_language = False
                    elif event.key == pygame.K_f:
                        current_language = "fr"
                        selecting_language = False

        # Difficulty Selection
        screen.fill(BLACK)
        title_text = large_font.render(languages[current_language]['title'], True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 250))

        easy_text = font.render(languages[current_language]['easy'], True, WHITE)
        medium_text = font.render(languages[current_language]['medium'], True, WHITE)
        hard_text = font.render(languages[current_language]['hard'], True, WHITE)
        screen.blit(easy_text, (WIDTH // 2 - easy_text.get_width() // 2, HEIGHT // 2 - 150))
        screen.blit(medium_text, (WIDTH // 2 - medium_text.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(hard_text, (WIDTH // 2 - hard_text.get_width() // 2, HEIGHT // 2 - 50))
        pygame.display.flip()

        selecting_difficulty = True
        while selecting_difficulty and game_state == STATE_MENU:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        current_difficulty = "easy"
                        selecting_difficulty = False
                    elif event.key == pygame.K_2:
                        current_difficulty = "medium"
                        selecting_difficulty = False
                    elif event.key == pygame.K_3:
                        current_difficulty = "hard"
                        selecting_difficulty = False

        # Select Ship
        screen.fill(BLACK)
        ship_prompt = font.render(languages[current_language]['select_ship'], True, WHITE)
        screen.blit(ship_prompt, (WIDTH // 2 - ship_prompt.get_width() // 2, HEIGHT // 2 - 200))

        # Display ship images at the bottom with clear labels
        ship1_text = font.render(languages[current_language]['ship1'], True, WHITE)
        ship2_text = font.render(languages[current_language]['ship2'], True, WHITE)
        ship3_text = font.render(languages[current_language]['ship3'], True, WHITE)
        screen.blit(ship1_text, (WIDTH // 4 - ship1_text.get_width() // 2, HEIGHT - 150))
        screen.blit(ship2_text, (WIDTH // 2 - ship2_text.get_width() // 2, HEIGHT - 150))
        screen.blit(ship3_text, (3 * WIDTH // 4 - ship3_text.get_width() // 2, HEIGHT - 150))

        # Display ship images at the bottom
        screen.blit(ship_images["ship1"], (WIDTH // 4 - ship_images["ship1"].get_width() // 2, HEIGHT - 100))
        screen.blit(ship_images["ship2"], (WIDTH // 2 - ship_images["ship2"].get_width() // 2, HEIGHT - 100))
        screen.blit(ship_images["ship3"], (3 * WIDTH // 4 - ship_images["ship3"].get_width() // 2, HEIGHT - 100))

        pygame.display.flip()

        selecting_ship = True
        while selecting_ship and game_state == STATE_MENU:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        selected_ship = "ship1"
                        selecting_ship = False
                    elif event.key == pygame.K_2:
                        selected_ship = "ship2"
                        selecting_ship = False
                    elif event.key == pygame.K_3:
                        selected_ship = "ship3"
                        selecting_ship = False

        # Select Character
        screen.fill(BLACK)
        char_prompt = font.render(languages[current_language]['select_character'], True, WHITE)
        screen.blit(char_prompt, (WIDTH // 2 - char_prompt.get_width() // 2, HEIGHT // 2 - 200))

        # Display character images at the bottom with clear labels
        char1_text = font.render(languages[current_language]['char1'], True, WHITE)
        char2_text = font.render(languages[current_language]['char2'], True, WHITE)
        char3_text = font.render(languages[current_language]['char3'], True, WHITE)
        screen.blit(char1_text, (WIDTH // 4 - char1_text.get_width() // 2, HEIGHT - 150))
        screen.blit(char2_text, (WIDTH // 2 - char2_text.get_width() // 2, HEIGHT - 150))
        screen.blit(char3_text, (3 * WIDTH // 4 - char3_text.get_width() // 2, HEIGHT - 150))

        # Display character images at the bottom
        screen.blit(character_images["char1"], (WIDTH // 4 - character_images["char1"].get_width() // 2, HEIGHT - 100))
        screen.blit(character_images["char2"], (WIDTH // 2 - character_images["char2"].get_width() // 2, HEIGHT - 100))
        screen.blit(character_images["char3"], (3 * WIDTH // 4 - character_images["char3"].get_width() // 2, HEIGHT - 100))

        pygame.display.flip()

        selecting_character = True
        while selecting_character and game_state == STATE_MENU:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        selected_character = "char1"
                        selecting_character = False
                    elif event.key == pygame.K_2:
                        selected_character = "char2"
                        selecting_character = False
                    elif event.key == pygame.K_3:
                        selected_character = "char3"
                        selecting_character = False

        # Select Name (from top 10 or enter new)
        game_state = STATE_SELECT_NAME

def load_scores():
    if not os.path.exists(scores_file):
        with open(scores_file, 'w') as f:
            json.dump([], f)
    with open(scores_file, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_scores(new_score):
    scores = load_scores()
    scores.append(new_score)
    # Sort scores descending by 'score'
    scores = sorted(scores, key=lambda x: x['score'], reverse=True)
    # Keep top 10
    scores = scores[:10]
    with open(scores_file, 'w') as f:
        json.dump(scores, f)

def save_score():
    new_score = {"name": player_name, "score": score, "ship": selected_ship, "character": selected_character}
    save_scores(new_score)

def show_best_scores():
    global current_difficulty, game_state
    scores = load_scores()
    screen.fill(BLACK)
    title_text = large_font.render(languages[current_language]['best_scores'], True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
    y_offset = 150

    # Display table headers
    headers = ["Rank", "Name", "Ship", "Character", "Score"]
    header_x_positions = [50, 150, 300, 450, 600]
    for idx, header in enumerate(headers):
        header_text = font.render(header, True, WHITE)
        screen.blit(header_text, (header_x_positions[idx], y_offset))
    y_offset += 30

    # Display top 10 scores with ship and character images
    player_in_top = False
    player_position = None
    for idx, entry in enumerate(scores[:10], start=1):
        if (entry['name'] == player_name and entry['score'] == score and 
            entry['ship'] == selected_ship and entry['character'] == selected_character):
            player_in_top = True
            player_position = idx
            highlight_color = (255, 215, 0)  # Gold color for the player's score
        else:
            highlight_color = WHITE

        rank_text = font.render(str(idx), True, highlight_color)
        name_text = font.render(entry['name'], True, highlight_color)
        score_text = font.render(str(entry['score']), True, highlight_color)

        screen.blit(rank_text, (header_x_positions[0], y_offset))
        screen.blit(name_text, (header_x_positions[1], y_offset))

        # Load ship and character images
        ship_img = ship_images.get(entry['ship'], ship_images["ship1"])
        char_img = character_images.get(entry['character'], character_images["char1"])

        # Resize images if necessary
        ship_img = pygame.transform.scale(ship_img, (50, 50))
        char_img = pygame.transform.scale(char_img, (50, 50))

        screen.blit(ship_img, (header_x_positions[2], y_offset))
        screen.blit(char_img, (header_x_positions[3], y_offset))
        screen.blit(score_text, (header_x_positions[4], y_offset))
        y_offset += 60

    # If player is not in top 10, show their position
    if not player_in_top and score > 0:
        player_position = len(scores) + 1
        # Display player's own score
        rank_text = font.render(str(player_position), True, (0, 255, 0))  # Green color
        name_text = font.render(player_name, True, (0, 255, 0))
        score_text = font.render(str(score), True, (0, 255, 0))

        screen.blit(rank_text, (header_x_positions[0], y_offset))
        screen.blit(name_text, (header_x_positions[1], y_offset))

        # Load ship and character images
        ship_img = ship_images.get(selected_ship, ship_images["ship1"])
        char_img = character_images.get(selected_character, character_images["char1"])

        # Resize images if necessary
        ship_img = pygame.transform.scale(ship_img, (50, 50))
        char_img = pygame.transform.scale(char_img, (50, 50))

        screen.blit(ship_img, (header_x_positions[2], y_offset))
        screen.blit(char_img, (header_x_positions[3], y_offset))
        screen.blit(score_text, (header_x_positions[4], y_offset))
        y_offset += 60

    # Highlight player's position if in top 10
    if player_in_top:
        pass  # Already highlighted above

    # Display player's position if not in top 10
    if not player_in_top and score > 0:
        pass  # Already displayed

    prompt_text = font.render(languages[current_language]['press_any_key'], True, WHITE)
    screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT - 100))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

    # Determine next action based on current difficulty
    if current_difficulty == "easy":
        # Prompt to retry or go to menu
        screen.fill(BLACK)
        retry_text = font.render(languages[current_language]['retry_easy'], True, WHITE)
        screen.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        # Retry easy level
                        current_difficulty = "easy"
                        waiting = False
                        game_state = STATE_GAME
                    elif event.key == pygame.K_n:
                        # Return to menu
                        game_state = STATE_MENU
                        waiting = False
    elif current_difficulty == "medium":
        # Automatically proceed to hard after medium
        current_difficulty = "hard"
        game_state = STATE_GAME
    elif current_difficulty == "hard":
        # After hard, return to menu
        game_state = STATE_MENU

def check_rewards():
    global combo_count, current_medal
    current_time = pygame.time.get_ticks()
    # Reset combo if time exceeded
    if combo_count > 0 and current_time - last_combo_time > combo_time:
        combo_count = 0
    # Check for combo
    if combo_count >= 3:
        # Determine medal based on number of combos
        if combo_count >= medal_thresholds["gold"]:
            current_medal = "gold"
        elif combo_count >= medal_thresholds["silver"]:
            current_medal = "silver"
        elif combo_count >= medal_thresholds["bronze"]:
            current_medal = "bronze"
        else:
            current_medal = None

        if current_medal:
            combo_count = 0
            # Display medal
            medal_image = medal_images[current_medal]
            screen.blit(medal_image, (WIDTH // 2 - medal_image.get_width() // 2, HEIGHT // 2 - medal_image.get_height() // 2))
            # Display combo reward text
            reward_message = languages[current_language]['combo_reward']
            reward_text = font.render(reward_message, True, (255, 215, 0))  # Gold color
            screen.blit(reward_text, (WIDTH // 2 - reward_text.get_width() // 2, HEIGHT // 2 + medal_image.get_height() // 2))
            pygame.display.flip()
            pygame.time.wait(1500)

def select_name():
    global player_name, game_state
    screen.fill(BLACK)
    select_name_prompt = font.render(languages[current_language]['select_name'], True, WHITE)
    screen.blit(select_name_prompt, (WIDTH // 2 - select_name_prompt.get_width() // 2, HEIGHT // 2 - 200))
    
    scores = load_scores()
    if scores:
        name_exists_prompt = font.render(languages[current_language]['name_exists'], True, WHITE)
        screen.blit(name_exists_prompt, (WIDTH // 2 - name_exists_prompt.get_width() // 2, HEIGHT // 2 - 150))
        for idx, entry in enumerate(scores[:10], start=1):
            name_text = font.render(f"{idx}. {entry['name']}", True, WHITE)
            screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, HEIGHT // 2 - 100 + idx * 30))
    else:
        no_scores_text = font.render("No scores available.", True, WHITE)
        screen.blit(no_scores_text, (WIDTH // 2 - no_scores_text.get_width() // 2, HEIGHT // 2 - 100))
    
    enter_new_prompt = font.render(languages[current_language]['enter_new_name'], True, WHITE)
    screen.blit(enter_new_prompt, (WIDTH // 2 - enter_new_prompt.get_width() // 2, HEIGHT // 2 + 150))
    pygame.display.flip()

    selecting_name = True
    while selecting_name:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # Check if player wants to enter a new name
                if event.key == pygame.K_n:
                    # Enter new name
                    screen.fill(BLACK)
                    enter_new_prompt = font.render(languages[current_language]['enter_new_name'], True, WHITE)
                    screen.blit(enter_new_prompt, (WIDTH // 2 - enter_new_prompt.get_width() // 2, HEIGHT // 2 - 50))
                    pygame.display.flip()
                    
                    entering_new_name = True
                    input_text = ""
                    while entering_new_name:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_RETURN:
                                    player_name = input_text if input_text else "Player"
                                    entering_new_name = False
                                    selecting_name = False
                                elif event.key == pygame.K_BACKSPACE:
                                    input_text = input_text[:-1]
                                else:
                                    if len(input_text) < 10 and event.unicode.isprintable():
                                        input_text += event.unicode
                        # Render the current input
                        screen.fill(BLACK)
                        enter_new_prompt = font.render(languages[current_language]['enter_new_name'], True, WHITE)
                        screen.blit(enter_new_prompt, (WIDTH // 2 - enter_new_prompt.get_width() // 2, HEIGHT // 2 - 50))
                        name_surface = font.render(input_text, True, WHITE)
                        screen.blit(name_surface, (WIDTH // 2 - name_surface.get_width() // 2, HEIGHT // 2))
                        pygame.display.flip()
                # Check if player wants to select an existing name
                else:
                    # Check if a number key was pressed corresponding to a name in the list
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                                     pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]:
                        num = event.key - pygame.K_0
                        if 1 <= num <= len(scores[:10]):
                            player_name = scores[num - 1]['name']
                            selected_ship = scores[num - 1]['ship']
                            selected_character = scores[num - 1]['character']
                            selecting_name = False
                            break
        # Render the screen again (in case something changed)
        screen.fill(BLACK)
        select_name_prompt = font.render(languages[current_language]['select_name'], True, WHITE)
        screen.blit(select_name_prompt, (WIDTH // 2 - select_name_prompt.get_width() // 2, HEIGHT // 2 - 200))
        
        scores = load_scores()
        if scores:
            name_exists_prompt = font.render(languages[current_language]['name_exists'], True, WHITE)
            screen.blit(name_exists_prompt, (WIDTH // 2 - name_exists_prompt.get_width() // 2, HEIGHT // 2 - 150))
            for idx, entry in enumerate(scores[:10], start=1):
                name_text = font.render(f"{idx}. {entry['name']}", True, WHITE)
                screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, HEIGHT // 2 - 100 + idx * 30))
        else:
            no_scores_text = font.render("No scores available.", True, WHITE)
            screen.blit(no_scores_text, (WIDTH // 2 - no_scores_text.get_width() // 2, HEIGHT // 2 - 100))
        
        enter_new_prompt = font.render(languages[current_language]['enter_new_name'], True, WHITE)
        screen.blit(enter_new_prompt, (WIDTH // 2 - enter_new_prompt.get_width() // 2, HEIGHT // 2 + 150))
        pygame.display.flip()

    # After selecting the name, start the game
    game_state = STATE_GAME

def load_scores():
    if not os.path.exists(scores_file):
        with open(scores_file, 'w') as f:
            json.dump([], f)
    with open(scores_file, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_scores(new_score):
    scores = load_scores()
    scores.append(new_score)
    # Sort scores descending by 'score'
    scores = sorted(scores, key=lambda x: x['score'], reverse=True)
    # Keep top 10
    scores = scores[:10]
    with open(scores_file, 'w') as f:
        json.dump(scores, f)

def save_score():
    new_score = {"name": player_name, "score": score, "ship": selected_ship, "character": selected_character}
    save_scores(new_score)

def show_best_scores():
    global current_difficulty, game_state
    scores = load_scores()
    screen.fill(BLACK)
    title_text = large_font.render(languages[current_language]['best_scores'], True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
    y_offset = 150

    # Display table headers
    headers = ["Rank", "Name", "Ship", "Character", "Score"]
    header_x_positions = [50, 150, 300, 450, 600]
    for idx, header in enumerate(headers):
        header_text = font.render(header, True, WHITE)
        screen.blit(header_text, (header_x_positions[idx], y_offset))
    y_offset += 30

    # Display top 10 scores with ship and character images
    player_in_top = False
    player_position = None
    for idx, entry in enumerate(scores[:10], start=1):
        if (entry['name'] == player_name and entry['score'] == score and 
            entry['ship'] == selected_ship and entry['character'] == selected_character):
            player_in_top = True
            player_position = idx
            highlight_color = (255, 215, 0)  # Gold color for the player's score
        else:
            highlight_color = WHITE

        rank_text = font.render(str(idx), True, highlight_color)
        name_text = font.render(entry['name'], True, highlight_color)
        score_text = font.render(str(entry['score']), True, highlight_color)

        screen.blit(rank_text, (header_x_positions[0], y_offset))
        screen.blit(name_text, (header_x_positions[1], y_offset))

        # Load ship and character images
        ship_img = ship_images.get(entry['ship'], ship_images["ship1"])
        char_img = character_images.get(entry['character'], character_images["char1"])

        # Resize images if necessary
        ship_img = pygame.transform.scale(ship_img, (50, 50))
        char_img = pygame.transform.scale(char_img, (50, 50))

        screen.blit(ship_img, (header_x_positions[2], y_offset))
        screen.blit(char_img, (header_x_positions[3], y_offset))
        screen.blit(score_text, (header_x_positions[4], y_offset))
        y_offset += 60

    # If player is not in top 10, show their position
    if not player_in_top and score > 0:
        player_position = len(scores) + 1
        # Display player's own score
        rank_text = font.render(str(player_position), True, (0, 255, 0))  # Green color
        name_text = font.render(player_name, True, (0, 255, 0))
        score_text = font.render(str(score), True, (0, 255, 0))

        screen.blit(rank_text, (header_x_positions[0], y_offset))
        screen.blit(name_text, (header_x_positions[1], y_offset))

        # Load ship and character images
        ship_img = ship_images.get(selected_ship, ship_images["ship1"])
        char_img = character_images.get(selected_character, character_images["char1"])

        # Resize images if necessary
        ship_img = pygame.transform.scale(ship_img, (50, 50))
        char_img = pygame.transform.scale(char_img, (50, 50))

        screen.blit(ship_img, (header_x_positions[2], y_offset))
        screen.blit(char_img, (header_x_positions[3], y_offset))
        screen.blit(score_text, (header_x_positions[4], y_offset))
        y_offset += 60

    # Highlight player's position if in top 10
    if player_in_top:
        pass  # Already highlighted above

    # Display player's position if not in top 10
    if not player_in_top and score > 0:
        pass  # Already displayed

    prompt_text = font.render(languages[current_language]['press_any_key'], True, WHITE)
    screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT - 100))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

    # Determine next action based on current difficulty
    if current_difficulty == "easy":
        # Prompt to retry or go to menu
        screen.fill(BLACK)
        retry_text = font.render(languages[current_language]['retry_easy'], True, WHITE)
        screen.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        # Retry easy level
                        current_difficulty = "easy"
                        waiting = False
                        game_state = STATE_GAME
                    elif event.key == pygame.K_n:
                        # Return to menu
                        game_state = STATE_MENU
                        waiting = False
    elif current_difficulty == "medium":
        # Automatically proceed to hard after medium
        current_difficulty = "hard"
        game_state = STATE_GAME
    elif current_difficulty == "hard":
        # After hard, return to menu
        game_state = STATE_MENU

def check_rewards():
    global combo_count, current_medal
    current_time = pygame.time.get_ticks()
    # Reset combo if time exceeded
    if combo_count > 0 and current_time - last_combo_time > combo_time:
        combo_count = 0
    # Check for combo
    if combo_count >= 3:
        # Determine medal based on number of combos
        if combo_count >= medal_thresholds["gold"]:
            current_medal = "gold"
        elif combo_count >= medal_thresholds["silver"]:
            current_medal = "silver"
        elif combo_count >= medal_thresholds["bronze"]:
            current_medal = "bronze"
        else:
            current_medal = None

        if current_medal:
            combo_count = 0
            # Display medal
            medal_image = medal_images[current_medal]
            screen.blit(medal_image, (WIDTH // 2 - medal_image.get_width() // 2, HEIGHT // 2 - medal_image.get_height() // 2))
            # Display combo reward text
            reward_message = languages[current_language]['combo_reward']
            reward_text = font.render(reward_message, True, (255, 215, 0))  # Gold color
            screen.blit(reward_text, (WIDTH // 2 - reward_text.get_width() // 2, HEIGHT // 2 + medal_image.get_height() // 2))
            pygame.display.flip()
            pygame.time.wait(1500)

def select_name():
    global player_name, game_state
    screen.fill(BLACK)
    select_name_prompt = font.render(languages[current_language]['select_name'], True, WHITE)
    screen.blit(select_name_prompt, (WIDTH // 2 - select_name_prompt.get_width() // 2, HEIGHT // 2 - 200))
    
    scores = load_scores()
    if scores:
        name_exists_prompt = font.render(languages[current_language]['name_exists'], True, WHITE)
        screen.blit(name_exists_prompt, (WIDTH // 2 - name_exists_prompt.get_width() // 2, HEIGHT // 2 - 150))
        for idx, entry in enumerate(scores[:10], start=1):
            name_text = font.render(f"{idx}. {entry['name']}", True, WHITE)
            screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, HEIGHT // 2 - 100 + idx * 30))
    else:
        no_scores_text = font.render("No scores available.", True, WHITE)
        screen.blit(no_scores_text, (WIDTH // 2 - no_scores_text.get_width() // 2, HEIGHT // 2 - 100))
    
    enter_new_prompt = font.render(languages[current_language]['enter_new_name'], True, WHITE)
    screen.blit(enter_new_prompt, (WIDTH // 2 - enter_new_prompt.get_width() // 2, HEIGHT // 2 + 150))
    pygame.display.flip()

    selecting_name = True
    while selecting_name:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # Check if player wants to enter a new name
                if event.key == pygame.K_n:
                    # Enter new name
                    screen.fill(BLACK)
                    enter_new_prompt = font.render(languages[current_language]['enter_new_name'], True, WHITE)
                    screen.blit(enter_new_prompt, (WIDTH // 2 - enter_new_prompt.get_width() // 2, HEIGHT // 2 - 50))
                    pygame.display.flip()
                    
                    entering_new_name = True
                    input_text = ""
                    while entering_new_name:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_RETURN:
                                    player_name = input_text if input_text else "Player"
                                    entering_new_name = False
                                    selecting_name = False
                                elif event.key == pygame.K_BACKSPACE:
                                    input_text = input_text[:-1]
                                else:
                                    if len(input_text) < 10 and event.unicode.isprintable():
                                        input_text += event.unicode
                        # Render the current input
                        screen.fill(BLACK)
                        enter_new_prompt = font.render(languages[current_language]['enter_new_name'], True, WHITE)
                        screen.blit(enter_new_prompt, (WIDTH // 2 - enter_new_prompt.get_width() // 2, HEIGHT // 2 - 50))
                        name_surface = font.render(input_text, True, WHITE)
                        screen.blit(name_surface, (WIDTH // 2 - name_surface.get_width() // 2, HEIGHT // 2))
                        pygame.display.flip()
                # Check if player wants to select an existing name
                else:
                    # Check if a number key was pressed corresponding to a name in the list
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                                     pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]:
                        num = event.key - pygame.K_0
                        if 1 <= num <= len(scores[:10]):
                            player_name = scores[num - 1]['name']
                            selected_ship = scores[num - 1]['ship']
                            selected_character = scores[num - 1]['character']
                            selecting_name = False
                            break
        # Render the screen again (in case something changed)
        screen.fill(BLACK)
        select_name_prompt = font.render(languages[current_language]['select_name'], True, WHITE)
        screen.blit(select_name_prompt, (WIDTH // 2 - select_name_prompt.get_width() // 2, HEIGHT // 2 - 200))
        
        scores = load_scores()
        if scores:
            name_exists_prompt = font.render(languages[current_language]['name_exists'], True, WHITE)
            screen.blit(name_exists_prompt, (WIDTH // 2 - name_exists_prompt.get_width() // 2, HEIGHT // 2 - 150))
            for idx, entry in enumerate(scores[:10], start=1):
                name_text = font.render(f"{idx}. {entry['name']}", True, WHITE)
                screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, HEIGHT // 2 - 100 + idx * 30))
        else:
            no_scores_text = font.render("No scores available.", True, WHITE)
            screen.blit(no_scores_text, (WIDTH // 2 - no_scores_text.get_width() // 2, HEIGHT // 2 - 100))
        
        enter_new_prompt = font.render(languages[current_language]['enter_new_name'], True, WHITE)
        screen.blit(enter_new_prompt, (WIDTH // 2 - enter_new_prompt.get_width() // 2, HEIGHT // 2 + 150))
        pygame.display.flip()

    # After selecting the name, start the game
    game_state = STATE_GAME

def main():
    global last_spawn_time, game_over, score, current_language, game_state, is_frozen, freeze_time_remaining, current_medal
    game_state = STATE_GAME
    player = Player()
    global lasers
    lasers = []

    # Game Timer
    game_duration = 60000  # 1 minute in milliseconds
    game_start_time = pygame.time.get_ticks()

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        game_time_remaining = max(0, (game_start_time + game_duration - current_time) // 1000)  # in seconds

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_state == STATE_GAME:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:  # Shoot with up arrow
                        shoot_laser(player)
            if game_state == STATE_GAME:
                if event.type == pygame.USEREVENT + 1:
                    # Freeze has ended
                    is_frozen = False
                    freeze_time_remaining = 0
                    pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            if game_state == STATE_GAME:
                if event.type == pygame.USEREVENT + 2:
                    # Freeze timer countdown
                    freeze_time_remaining -= 1000
                    if freeze_time_remaining <= 0:
                        is_frozen = False
                        freeze_time_remaining = 0
                        pygame.time.set_timer(pygame.USEREVENT + 2, 0)
                    else:
                        pygame.time.set_timer(pygame.USEREVENT + 2, 1000)  # Update every second

        if game_state == STATE_GAME:
            if not game_over:
                if not is_frozen:
                    # Player movement
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LEFT]:
                        player.move_left()
                    if keys[pygame.K_RIGHT]:
                        player.move_right()

                    # Spawn objects
                    if current_time - last_spawn_time > difficulty_levels[current_difficulty]["spawn_delay"]:
                        spawn_object()
                        last_spawn_time = current_time

                    # Move objects and lasers
                    move_objects()
                    move_lasers()

                # Check collisions
                check_collisions(player)

                # Check for combo rewards
                check_rewards()

                # Draw everything
                screen.fill(BLACK)
                for obj in objects:
                    obj.draw()
                player.draw()
                for laser in lasers:
                    laser.draw()
                draw_score(game_time_remaining)

                # Check if time is up
                if current_time - game_start_time >= game_duration:
                    game_over = True

                # Check for game over
                if game_over:
                    show_game_over_screen()
            else:
                pass  # Handled in check_collisions and show_game_over_screen
        elif game_state == STATE_SELECT_NAME:
            select_name()
        elif game_state == STATE_MENU:
            show_menu()
        elif game_state == STATE_GAME_OVER:
            pass  # Handled in show_game_over_screen

        # Update display
        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()

if __name__ == "__main__":
    show_menu()
    main()
