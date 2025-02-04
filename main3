import pygame, random, sys, json, os, math

# ==============================
# Initialization and Global Setup
# ==============================
pygame.init()
pygame.key.set_repeat(500, 50)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Slicer")

# Global constant: menu elements start at y = 150.
MENU_Y_OFFSET = 150

# ==============================
# Colors and Fonts
# ==============================
BLACK = (0, 0, 0)
FONT_COLOR = BLACK

menu_font    = pygame.font.SysFont("Arial", 24)
game_font    = pygame.font.SysFont("Arial", 20)
large_font   = pygame.font.SysFont("Arial", 36)
title_font   = pygame.font.SysFont("Arial", 48, bold=True)
dev_font     = pygame.font.SysFont("Arial", 16)

# ==============================
# Global Button Dimensions
# ==============================
BUTTON_WIDTH  = 300
BUTTON_HEIGHT = 70

# ==============================
# Button Class
# ==============================
class Button:
    def __init__(self, x, y, width, height, text, callback=None,
                 font=menu_font, bg_color=(200, 200, 200), text_color=FONT_COLOR, image=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.image = image

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        if self.image:
            image_rect = self.image.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
            surface.blit(self.image, image_rect)
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(midleft=(image_rect.right + 10, self.rect.centery))
        else:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# ==============================
# Sound Loading
# ==============================
def load_sound(path):
    if os.path.exists(path):
        s = pygame.mixer.Sound(path)
        s.set_volume(1.0)
        return s
    else:
        print(f"Sound file not found: {path}")
        return None

laser_sound     = load_sound("assets/sounds/laser.wav")
slice_sound     = load_sound("assets/sounds/slice.wav")
explosion_sound = load_sound("assets/sounds/explosion.wav")
crush_sound     = load_sound("assets/sounds/crush.mp3")
medal_sound     = load_sound("assets/sounds/medal.wav")
background_music = "assets/sounds/background.mp3"
victory_music   = load_sound("assets/sounds/youwon.wav")
gameover_music  = load_sound("assets/sounds/gameover.wav")

if os.path.exists(background_music):
    pygame.mixer.music.load(background_music)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
else:
    print(f"Background music not found: {background_music}")

# ==============================
# Image Loading Helper and Asset Sizes
# ==============================
def load_and_resize_image(path, max_size):
    if not os.path.exists(path):
        print(f"Image file not found: {path}")
        pygame.quit()
        sys.exit()
    img = pygame.image.load(path).convert_alpha()
    if "background" in path.lower():
        return pygame.transform.scale(img, (WIDTH, HEIGHT))
    rect = img.get_rect()
    scale_ratio = min(max_size[0] / rect.width, max_size[1] / rect.height, 1)
    new_size = (int(rect.width * scale_ratio), int(rect.height * scale_ratio))
    return pygame.transform.scale(img, new_size)

MAX_SIZE_FRUIT     = (128, 128)
MAX_SIZE_BOMB      = (100, 100)
MAX_SIZE_ICE       = (100, 100)
MAX_SIZE_SHIP      = (150, 150)
MAX_SIZE_CHARACTER = (100, 100)
MAX_SIZE_MEDAL     = (100, 100)
MAX_SIZE_BACKGROUND= (WIDTH, HEIGHT)
MAX_SIZE_WEAPON    = (80, 80)

fruit_images = {
    "apple": load_and_resize_image("assets/images/fruit_apple.png", MAX_SIZE_FRUIT),
    "banana": load_and_resize_image("assets/images/fruit_banana.png", MAX_SIZE_FRUIT),
    "orange": load_and_resize_image("assets/images/fruit_orange.png", MAX_SIZE_FRUIT),
    "strawberry": load_and_resize_image("assets/images/fruit_strawberry.png", MAX_SIZE_FRUIT),
    "watermelon": load_and_resize_image("assets/images/fruit_watermelon.png", MAX_SIZE_FRUIT),
    "pineapple": load_and_resize_image("assets/images/fruit_pineapple.png", MAX_SIZE_FRUIT)
}

bomb_image = load_and_resize_image("assets/images/bomb.png", MAX_SIZE_BOMB)
ice_image  = load_and_resize_image("assets/images/ice.png", MAX_SIZE_ICE)

ship_images = {
    "ship1": load_and_resize_image("assets/images/ship1.png", MAX_SIZE_SHIP),
    "ship2": load_and_resize_image("assets/images/ship2.png", MAX_SIZE_SHIP),
    "ship3": load_and_resize_image("assets/images/ship3.png", MAX_SIZE_SHIP)
}

character_images = {
    "char1": load_and_resize_image("assets/images/char1.png", MAX_SIZE_CHARACTER),
    "char2": load_and_resize_image("assets/images/char2.png", MAX_SIZE_CHARACTER),
    "char3": load_and_resize_image("assets/images/char3.png", MAX_SIZE_CHARACTER)
}

medal_images = {
    "bronze": load_and_resize_image("assets/images/bronze_medal.png", MAX_SIZE_MEDAL),
    "silver": load_and_resize_image("assets/images/silver_medal.png", MAX_SIZE_MEDAL),
    "gold": load_and_resize_image("assets/images/gold_medal.png", MAX_SIZE_MEDAL)
}

background_images = {
    "menu": load_and_resize_image("assets/images/background1.jpg", MAX_SIZE_BACKGROUND),
    "name": load_and_resize_image("assets/images/background2.jpg", MAX_SIZE_BACKGROUND),
    "easy": load_and_resize_image("assets/images/background3.jpg", MAX_SIZE_BACKGROUND),
    "medium": load_and_resize_image("assets/images/background4.jpg", MAX_SIZE_BACKGROUND),
    "hard": load_and_resize_image("assets/images/background5.jpg", MAX_SIZE_BACKGROUND)
}

saber_images = {
    "saber1": load_and_resize_image("assets/images/saber1.png", MAX_SIZE_WEAPON),
    "saber2": load_and_resize_image("assets/images/saber2.png", MAX_SIZE_WEAPON),
    "saber3": load_and_resize_image("assets/images/saber3.png", MAX_SIZE_WEAPON)
}

THUMBNAIL_SIZE = (120, 90)
background_thumbnails = {}
for key, img in background_images.items():
    background_thumbnails[key] = pygame.transform.scale(img, THUMBNAIL_SIZE)

menu_bg = background_images["menu"]

# ==============================
# Load and Scale the Logo (LAPLateforme)
# ==============================
platform_logo = load_and_resize_image("assets/images/platform logo.png", (250, 250))
def draw_logo():
    screen.blit(platform_logo, (WIDTH - platform_logo.get_width() - 10, 10))

# ==============================
# Draw Developer Names (Lower Left)
# ==============================
def draw_developers():
    dev_text = "Redha, Adam & Pierre (4-Feb-2025)"
    dev_surface = dev_font.render(dev_text, True, FONT_COLOR)
    screen.blit(dev_surface, (10, HEIGHT - dev_surface.get_height() - 10))

# ==============================
# Global Game Variables and States
# ==============================
player_speed = 10
weapon_speed = 15
max_weapons = 3
objects = []
weapons = []

ROUND_DURATION = 30000

difficulty_levels = {
    "easy": {"speed": 3, "spawn_delay": 1200},
    "medium": {"speed": 5, "spawn_delay": 1000},
    "hard": {"speed": 7, "spawn_delay": 800}
}
current_difficulty = "easy"

score = 0
game_over = False
combo_count = 0
combo_time = 1000
last_combo_time = 0
current_medal = None

scores_file = "scores.json"
medal_thresholds = {"bronze": 3, "silver": 5, "gold": 10}

PLAYER_NAME_FILE = "player_name.txt"

# Global Freeze Variables (for ice collisions)
frozen = False
freeze_end_time = 0

# ==============================
# Multilingual Support
# ==============================
languages = {
    "en": {
        "title": "FRUIT SLICER",
        "easy": "Easy",
        "medium": "Medium",
        "hard": "Hard",
        "game_over": "Game Over",
        "you_win": "You Win!",
        "final_score": "Final Score:",
        "enter_name": "Enter your name:",
        "best_scores": "Best Scores",
        "press_any_key": "Press any key to continue",
        "select_ship": "Select Your Ship:",
        "select_character": "Select Your Character:",
        "ship1": "Ship 1",
        "ship2": "Ship 2",
        "ship3": "Ship 3",
        "char1": "Character 1",
        "char2": "Character 2",
        "char3": "Character 3",
        "score": "Score",
        "combo_reward": "Combo Reward!",
        "select_name": "Enter your name",
        "enter_new_name": "Enter New Name",
        "select_background": "Select Your Background:",
        "background_menu": "Background 1",
        "background_name": "Background 2",
        "background_easy": "Background 3",
        "background_medium": "Background 4",
        "background_hard": "Background 5",
        "select_weapon": "Select Your Weapon:",
        "weapon1": "Saber 1",
        "weapon2": "Saber 2",
        "weapon3": "Saber 3",
        "round_over": "You Win! Continue?"
    },
    "fr": {
        "title": "FRUIT SLICER",
        "easy": "Facile",
        "medium": "Moyen",
        "hard": "Difficile",
        "game_over": "Jeu Terminé",
        "you_win": "Vous avez gagné !",
        "final_score": "Score Final :",
        "enter_name": "Entrez votre nom :",
        "best_scores": "Meilleurs Scores",
        "press_any_key": "Appuyez sur une touche pour continuer",
        "select_ship": "Sélectionnez Votre Vaisseau :",
        "select_character": "Sélectionnez Votre Personnage :",
        "ship1": "Vaisseau 1",
        "ship2": "Vaisseau 2",
        "ship3": "Vaisseau 3",
        "char1": "Personnage 1",
        "char2": "Personnage 2",
        "char3": "Personnage 3",
        "score": "Score",
        "combo_reward": "Récompense Combo!",
        "select_name": "Entrez votre nom",
        "enter_new_name": "Entrer un Nouveau Nom",
        "select_background": "Sélectionnez Votre Arrière-Plan :",
        "background_menu": "Arrière-Plan 1",
        "background_name": "Arrière-Plan 2",
        "background_easy": "Arrière-Plan 3",
        "background_medium": "Arrière-Plan 4",
        "background_hard": "Arrière-Plan 5",
        "select_weapon": "Sélectionnez Votre Arme :",
        "weapon1": "Sabre 1",
        "weapon2": "Sabre 2",
        "weapon3": "Sabre 3",
        "round_over": "Vous avez gagné ! Continuer ?"
    }
}

current_language = "fr"

if os.path.exists(PLAYER_NAME_FILE):
    with open(PLAYER_NAME_FILE, "r") as f:
        player_name = f.read().strip()
else:
    player_name = ""

selected_ship = "ship1"
selected_character = "char1"
selected_background = "menu"
selected_weapon = "saber1"

STATE_MENU = "MENU"
STATE_GAME = "GAME"
STATE_ROUND_OVER = "ROUND_OVER"
STATE_GAME_OVER = "GAME_OVER"
game_state = STATE_MENU

# ==============================
# In-Game Menu Button (to return to main menu)
# ==============================
in_game_menu_button = Button(WIDTH - 110, HEIGHT - 50, 100, 40, "Menu")
def go_to_menu():
    reset_game_state()
    setup_game()

# ==============================
# Menu Helper Function (with Developer Names)
# ==============================
def run_menu_screen(title_text, buttons, bg_image=None, bottom_text=None):
    running = True
    while running:
        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill((220, 220, 220))
        title_surface = title_font.render(title_text, True, FONT_COLOR)
        screen.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, MENU_Y_OFFSET - 100))
        for btn in buttons:
            btn.draw(screen)
        draw_logo()
        draw_developers()
        if bottom_text:
            bottom_surface = menu_font.render(bottom_text, True, FONT_COLOR)
            screen.blit(bottom_surface, (10, HEIGHT - bottom_surface.get_height() - 20))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for btn in buttons:
                    if btn.is_clicked(pos):
                        if btn.callback:
                            btn.callback()
                        running = False
                        break

# ==============================
# Menu Screens (Shifted Downward)
# ==============================
def menu_language():
    global current_language
    def set_en():
        global current_language
        current_language = "en"
    def set_fr():
        global current_language
        current_language = "fr"
    btn1 = Button(WIDTH//2 - BUTTON_WIDTH//2, MENU_Y_OFFSET, BUTTON_WIDTH, BUTTON_HEIGHT, "English", callback=set_en)
    btn2 = Button(WIDTH//2 - BUTTON_WIDTH//2, MENU_Y_OFFSET + 80, BUTTON_WIDTH, BUTTON_HEIGHT, "Français", callback=set_fr)
    run_menu_screen("Select Language", [btn1, btn2], bg_image=menu_bg)

def menu_difficulty():
    global current_difficulty
    def set_easy():
        global current_difficulty
        current_difficulty = "easy"
    def set_medium():
        global current_difficulty
        current_difficulty = "medium"
    def set_hard():
        global current_difficulty
        current_difficulty = "hard"
    btn_easy = Button(WIDTH//2 - BUTTON_WIDTH//2, MENU_Y_OFFSET, BUTTON_WIDTH, BUTTON_HEIGHT,
                      languages[current_language]['easy'], callback=set_easy)
    btn_medium = Button(WIDTH//2 - BUTTON_WIDTH//2, MENU_Y_OFFSET + 90, BUTTON_WIDTH, BUTTON_HEIGHT,
                        languages[current_language]['medium'], callback=set_medium)
    btn_hard = Button(WIDTH//2 - BUTTON_WIDTH//2, MENU_Y_OFFSET + 180, BUTTON_WIDTH, BUTTON_HEIGHT,
                      languages[current_language]['hard'], callback=set_hard)
    run_menu_screen(languages[current_language]['title'], [btn_easy, btn_medium, btn_hard], bg_image=menu_bg)

def menu_background():
    global selected_background
    def set_bg(key):
        global selected_background
        selected_background = key
    spacing = 15
    y = MENU_Y_OFFSET
    btn1 = Button(WIDTH//2 - BUTTON_WIDTH//2, y, BUTTON_WIDTH, BUTTON_HEIGHT,
                  languages[current_language]['background_menu'], callback=lambda: set_bg("menu"),
                  image=background_thumbnails["menu"])
    y += BUTTON_HEIGHT + spacing
    btn2 = Button(WIDTH//2 - BUTTON_WIDTH//2, y, BUTTON_WIDTH, BUTTON_HEIGHT,
                  languages[current_language]['background_name'], callback=lambda: set_bg("name"),
                  image=background_thumbnails["name"])
    y += BUTTON_HEIGHT + spacing
    btn3 = Button(WIDTH//2 - BUTTON_WIDTH//2, y, BUTTON_WIDTH, BUTTON_HEIGHT,
                  languages[current_language]['background_easy'], callback=lambda: set_bg("easy"),
                  image=background_thumbnails["easy"])
    y += BUTTON_HEIGHT + spacing
    btn4 = Button(WIDTH//2 - BUTTON_WIDTH//2, y, BUTTON_WIDTH, BUTTON_HEIGHT,
                  languages[current_language]['background_medium'], callback=lambda: set_bg("medium"),
                  image=background_thumbnails["medium"])
    y += BUTTON_HEIGHT + spacing
    btn5 = Button(WIDTH//2 - BUTTON_WIDTH//2, y, BUTTON_WIDTH, BUTTON_HEIGHT,
                  languages[current_language]['background_hard'], callback=lambda: set_bg("hard"),
                  image=background_thumbnails["hard"])
    run_menu_screen(languages[current_language]['select_background'], [btn1, btn2, btn3, btn4, btn5], bg_image=menu_bg)

def menu_weapon():
    global selected_weapon
    def set_weapon(w):
        global selected_weapon
        selected_weapon = w
    btn1 = Button(WIDTH//2 - BUTTON_WIDTH//2, MENU_Y_OFFSET, BUTTON_WIDTH, BUTTON_HEIGHT,
                  languages[current_language]['weapon1'], callback=lambda: set_weapon("saber1"),
                  image=saber_images["saber1"])
    btn2 = Button(WIDTH//2 - BUTTON_WIDTH//2, MENU_Y_OFFSET + 90, BUTTON_WIDTH, BUTTON_HEIGHT,
                  languages[current_language]['weapon2'], callback=lambda: set_weapon("saber2"),
                  image=saber_images["saber2"])
    btn3 = Button(WIDTH//2 - BUTTON_WIDTH//2, MENU_Y_OFFSET + 180, BUTTON_WIDTH, BUTTON_HEIGHT,
                  languages[current_language]['weapon3'], callback=lambda: set_weapon("saber3"),
                  image=saber_images["saber3"])
    run_menu_screen(languages[current_language]['select_weapon'], [btn1, btn2, btn3], bg_image=menu_bg)

def menu_ship():
    global selected_ship
    def set_ship(s):
        global selected_ship
        selected_ship = s
    btn1 = Button(WIDTH//2 - BUTTON_WIDTH//2, MENU_Y_OFFSET, BUTTON_WIDTH, BUTTON_HEIGHT,
                  languages[current_language]['ship1'], callback=lambda: set_ship("ship1"),
                  image=ship_images["ship1"])
    btn2 = Button(WIDTH//2 - BUTTON_WIDTH//2, MENU_Y_OFFSET + 90, BUTTON_WIDTH, BUTTON_HEIGHT,
                  languages[current_language]['ship2'], callback=lambda: set_ship("ship2"),
                  image=ship_images["ship2"])
    btn3 = Button(WIDTH//2 - BUTTON_WIDTH//2, MENU_Y_OFFSET + 180, BUTTON_WIDTH, BUTTON_HEIGHT,
                  languages[current_language]['ship3'], callback=lambda: set_ship("ship3"),
                  image=ship_images["ship3"])
    run_menu_screen(languages[current_language]['select_ship'], [btn1, btn2, btn3], bg_image=menu_bg)

def menu_character():
    global selected_character
    def set_char(c):
        global selected_character
        selected_character = c
    btn1 = Button(WIDTH//2 - BUTTON_WIDTH//2, MENU_Y_OFFSET, BUTTON_WIDTH, BUTTON_HEIGHT,
                  languages[current_language]['char1'], callback=lambda: set_char("char1"),
                  image=character_images["char1"])
    btn2 = Button(WIDTH//2 - BUTTON_WIDTH//2, MENU_Y_OFFSET + 90, BUTTON_WIDTH, BUTTON_HEIGHT,
                  languages[current_language]['char2'], callback=lambda: set_char("char2"),
                  image=character_images["char2"])
    btn3 = Button(WIDTH//2 - BUTTON_WIDTH//2, MENU_Y_OFFSET + 180, BUTTON_WIDTH, BUTTON_HEIGHT,
                  languages[current_language]['char3'], callback=lambda: set_char("char3"),
                  image=character_images["char3"])
    run_menu_screen(languages[current_language]['select_character'], [btn1, btn2, btn3], bg_image=menu_bg)

# ==============================
# New Name Input Screen
# ==============================
def input_new_name():
    pygame.event.clear()
    input_text = ""
    clock = pygame.time.Clock()
    input_box = pygame.Rect(WIDTH//2 - 150, MENU_Y_OFFSET + 20, 300, 50)
    ok_box = pygame.Rect(WIDTH//2 - 75, MENU_Y_OFFSET + 90, 150, 50)
    prompt = languages[current_language]['enter_name'] + " (max 10 chars)"
    if os.path.exists(PLAYER_NAME_FILE):
        with open(PLAYER_NAME_FILE, "r") as f:
            input_text = f.read().strip()
    while True:
        screen.blit(menu_bg, (0, 0))
        prompt_surface = menu_font.render(prompt, True, FONT_COLOR)
        screen.blit(prompt_surface, (WIDTH//2 - prompt_surface.get_width()//2, MENU_Y_OFFSET - 20))
        pygame.draw.rect(screen, (255, 255, 255), input_box)
        pygame.draw.rect(screen, BLACK, input_box, 2)
        text_surface = menu_font.render(input_text, True, FONT_COLOR)
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 10))
        pygame.draw.rect(screen, (200, 200, 200), ok_box)
        pygame.draw.rect(screen, BLACK, ok_box, 2)
        ok_text = menu_font.render("OK", True, FONT_COLOR)
        screen.blit(ok_text, (ok_box.centerx - ok_text.get_width()//2, ok_box.centery - ok_text.get_height()//2))
        draw_logo()
        draw_developers()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    final_name = input_text if input_text != "" else "Player"
                    with open(PLAYER_NAME_FILE, "w") as f:
                        f.write(final_name)
                    return final_name
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if len(input_text) < 10:
                        input_text += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if ok_box.collidepoint(event.pos):
                    final_name = input_text if input_text != "" else "Player"
                    with open(PLAYER_NAME_FILE, "w") as f:
                        f.write(final_name)
                    return final_name
        clock.tick(30)

def menu_name():
    global player_name
    player_name = input_new_name()
    print("Selected name:", player_name)

# ==============================
# Game Classes: Player, Weapon, GameObject
# ==============================
class Player:
    def __init__(self):
        self.speed = player_speed
        self.update_image()
        self.x = WIDTH//2 - self.width//2
        self.y = HEIGHT - self.height - 10

    def update_image(self):
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

class Weapon:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = saber_images.get(selected_weapon, None)
        if self.image:
            self.width, self.height = self.image.get_size()
        else:
            self.width, self.height = (5, 20)

    def move(self):
        self.y -= weapon_speed

    def draw(self):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.width, self.height))

class GameObject:
    def __init__(self, obj_type, scale=1.0):
        self.type = obj_type
        self.scale = scale
        if self.type == "fruit":
            self.spawn_x = random.randint(50, WIDTH - 50)
            self.spawn_y = HEIGHT - 50
            self.velocity_x = random.uniform(-5, 5)
            self.velocity_y = random.uniform(-25, -20)
        else:
            self.spawn_x = random.randint(50, WIDTH - 50)
            self.spawn_y = -50
            self.velocity_x = random.uniform(-3, 3)
            self.velocity_y = random.uniform(5, 10)
        self.image = self.load_image()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = pygame.Rect(self.spawn_x, self.spawn_y, self.width, self.height)
        self.gravity = 0.5

    def load_image(self):
        if self.type == "fruit":
            fruit_name = random.choice(list(fruit_images.keys()))
            base_image = fruit_images[fruit_name]
            if self.scale != 1.0:
                return pygame.transform.scale(base_image,
                                              (int(base_image.get_width() * self.scale),
                                               int(base_image.get_height() * self.scale)))
            return base_image
        elif self.type == "ice":
            return ice_image
        elif self.type == "bomb":
            return bomb_image
        else:
            return pygame.Surface((50, 50))

    def update(self):
        self.velocity_y += self.gravity
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def is_off_screen(self):
        return (self.rect.y > HEIGHT + 50 or self.rect.x < -50 or self.rect.x > WIDTH + 50)

# ==============================
# Object Spawning and Movement
# ==============================
def spawn_object():
    obj_type = random.choices(["fruit", "ice", "bomb"], weights=[70, 15, 15])[0]
    if obj_type == "fruit":
        count = random.randint(2, 3)
        for _ in range(count):
            objects.append(GameObject("fruit"))
    else:
        objects.append(GameObject(obj_type))

def move_objects():
    global frozen, freeze_end_time
    if frozen and pygame.time.get_ticks() < freeze_end_time:
        return
    else:
        frozen = False
    for obj in objects[:]:
        obj.update()
        if obj.is_off_screen():
            objects.remove(obj)

def shoot_weapon(player):
    if len(weapons) < max_weapons:
        saber_img = saber_images.get(selected_weapon)
        offset = saber_img.get_width() // 2 if saber_img else 2
        weapon_x = player.x + player.width // 2 - offset
        weapon_y = player.y
        weapons.append(Weapon(weapon_x, weapon_y))
        if laser_sound:
            laser_sound.play()

def move_weapons():
    for w in weapons[:]:
        w.move()
        if w.y < -w.height:
            weapons.remove(w)

# ==============================
# Collision and Reward Logic
# ==============================
def check_collisions(player):
    global score, game_over, combo_count, last_combo_time, current_medal, frozen, freeze_end_time
    for w in weapons[:]:
        w_rect = pygame.Rect(w.x, w.y, w.width, w.height)
        fruits_hit = []
        non_fruit_hit = None
        for obj in objects[:]:
            if obj.rect.colliderect(w_rect):
                if obj.type == "fruit":
                    fruits_hit.append(obj)
                else:
                    non_fruit_hit = obj
                    break
        # If ice is hit, freeze objects.
        if non_fruit_hit and non_fruit_hit.type == "ice":
            if non_fruit_hit in objects: objects.remove(non_fruit_hit)
            if w in weapons: weapons.remove(w)
            score += 1
            combo_count += 1
            last_combo_time = pygame.time.get_ticks()
            frozen = True
            freeze_end_time = pygame.time.get_ticks() + 3000
            continue
        # New Medal Condition: only when frozen and exactly 2 fruits are hit.
        if frozen and len(fruits_hit) == 2:
            for fruit in fruits_hit:
                if fruit in objects: objects.remove(fruit)
                score += 1
            if w in weapons: weapons.remove(w)
            combo_count += 2
            last_combo_time = pygame.time.get_ticks()
            if medal_sound:
                medal_sound.play()
        elif len(fruits_hit) == 1:
            fruit = fruits_hit[0]
            if crush_sound:
                crush_sound.play()
            if fruit.scale > 0.5:
                obj1 = GameObject("fruit", scale=fruit.scale/2)
                obj1.rect.x, obj1.rect.y = fruit.rect.x, fruit.rect.y
                obj1.velocity_x = fruit.velocity_x - 2
                obj1.velocity_y = fruit.velocity_y
                obj2 = GameObject("fruit", scale=fruit.scale/2)
                obj2.rect.x, obj2.rect.y = fruit.rect.x + fruit.width//2, fruit.rect.y
                obj2.velocity_x = fruit.velocity_x + 2
                obj2.velocity_y = fruit.velocity_y
                objects.append(obj1)
                objects.append(obj2)
            if fruit in objects:
                objects.remove(fruit)
            if w in weapons:
                weapons.remove(w)
            score += 1
            combo_count += 1
            last_combo_time = pygame.time.get_ticks()
        if non_fruit_hit and non_fruit_hit.type == "bomb":
            if explosion_sound:
                explosion_sound.play()
            if non_fruit_hit in objects:
                objects.remove(non_fruit_hit)
            if w in weapons:
                weapons.remove(w)
            game_over = True

def check_ship_collision(player):
    global game_over
    player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
    for obj in objects:
        if obj.type == "bomb" and obj.rect.colliderect(player_rect):
            if explosion_sound:
                explosion_sound.play()
            if obj in objects:
                objects.remove(obj)
            game_over = True
            break

def draw_score(time_remaining):
    score_text = game_font.render(f"{languages[current_language]['score']}: {score}", True, FONT_COLOR)
    time_text = game_font.render(f"Time: {time_remaining}s", True, FONT_COLOR)
    screen.blit(score_text, (10, 10))
    screen.blit(time_text, (10, 30))
    person_logo = pygame.transform.scale(character_images.get(selected_character, character_images["char1"]), (30, 30))
    screen.blit(person_logo, (10 + score_text.get_width() + 10, 10))
    saber_icon = pygame.transform.scale(saber_images.get(selected_weapon, saber_images["saber1"]), (30, 30))
    screen.blit(saber_icon, (10 + score_text.get_width() + 10 + 40, 10))

# ==============================
# Victory Animation: Orbiting Animation
# ==============================
def animate_victory():
    duration = 2000
    start_time = pygame.time.get_ticks()
    center_x = WIDTH / 2
    center_y = HEIGHT / 2
    # Define three radii for the orbits.
    R_outer = 200  # for saber
    R_middle = 120 # for character
    R_inner = 60   # for ship
    while True:
        t = pygame.time.get_ticks() - start_time
        progress = t / duration
        if progress > 1:
            progress = 1
        # Calculate the current rotation angle (in degrees, 0 -> 720)
        angle_deg = progress * 720
        angle_rad = math.radians(angle_deg)
        # Outer orbit (saber)
        saber_x = center_x + R_outer * math.cos(angle_rad) - 20
        saber_y = center_y + R_outer * math.sin(angle_rad) - 20
        rotated_saber = pygame.transform.rotate(saber_images[selected_weapon], -angle_deg)
        # Middle orbit (character) with an offset
        angle_char_rad = math.radians(angle_deg + 30)
        char_img = character_images[selected_character]
        char_width, char_height = char_img.get_size()
        char_x = center_x + R_middle * math.cos(angle_char_rad) - char_width / 2
        char_y = center_y + R_middle * math.sin(angle_char_rad) - char_height / 2
        # Inner orbit (ship) with a different offset
        angle_ship_rad = math.radians(angle_deg + 60)
        ship_img = ship_images[selected_ship]
        ship_width, ship_height = ship_img.get_size()
        ship_x = center_x + R_inner * math.cos(angle_ship_rad) - ship_width / 2
        ship_y = center_y + R_inner * math.sin(angle_ship_rad) - ship_height / 2
        # Clear screen and draw background.
        screen.blit(background_images[selected_background] if selected_background in background_images else background_images[current_difficulty], (0,0))
        # Draw the three objects in their orbits.
        screen.blit(rotated_saber, (saber_x, saber_y))
        screen.blit(char_img, (char_x, char_y))
        screen.blit(ship_img, (ship_x, ship_y))
        draw_logo()
        draw_developers()
        pygame.display.flip()
        if progress >= 1:
            break
        pygame.time.delay(30)

# ==============================
# Loss Animation: Bombs coming from edges
# ==============================
def animate_loss():
    duration = 2000
    start_time = pygame.time.get_ticks()
    temp_player = Player()
    ship_center = (temp_player.x + temp_player.width/2, temp_player.y + temp_player.height/2)
    bomb_starts = []
    for i in range(8):
        side = i % 4
        if side == 0:
            pos = (0, random.randint(0, HEIGHT))
        elif side == 1:
            pos = (WIDTH, random.randint(0, HEIGHT))
        elif side == 2:
            pos = (random.randint(0, WIDTH), 0)
        else:
            pos = (random.randint(0, WIDTH), HEIGHT)
        bomb_starts.append(pos)
    while True:
        current_time = pygame.time.get_ticks()
        progress = (current_time - start_time) / duration
        if progress > 1:
            progress = 1
        screen.blit(background_images[selected_background] if selected_background in background_images else background_images[current_difficulty], (0,0))
        temp_player.draw()
        for pos in bomb_starts:
            cur_x = pos[0] + (ship_center[0] - pos[0]) * progress
            cur_y = pos[1] + (ship_center[1] - pos[1]) * progress
            screen.blit(bomb_image, (cur_x, cur_y))
            if progress >= 0.9:
                if explosion_sound:
                    explosion_sound.play()
        draw_logo()
        draw_developers()
        pygame.display.flip()
        if progress >= 1:
            break
        pygame.time.delay(30)

def show_victory_screen():
    global game_state, current_difficulty
    pygame.mixer.music.stop()
    if victory_music:
        victory_music.play()
    animate_victory()
    screen.fill((200, 200, 200))
    win_txt = large_font.render(languages[current_language]['you_win'], True, FONT_COLOR)
    score_txt = game_font.render(f"{languages[current_language]['final_score']} {score}", True, FONT_COLOR)
    instructions = game_font.render("Click to continue.", True, FONT_COLOR)
    screen.blit(win_txt, (WIDTH//2 - win_txt.get_width()//2, HEIGHT//2 - 120))
    screen.blit(score_txt, (WIDTH//2 - score_txt.get_width()//2, HEIGHT//2 - 60))
    screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT//2))
    draw_logo()
    draw_developers()
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
    if victory_music:
        victory_music.stop()
    pygame.mixer.music.play(-1)
    return pygame.time.get_ticks()

def show_game_over_screen():
    global game_over, game_state
    pygame.mixer.music.stop()
    if gameover_music:
        gameover_music.play()
    animate_loss()
    screen.fill((200, 200, 200))
    over_txt = large_font.render(languages[current_language]['game_over'], True, FONT_COLOR)
    sc_txt = game_font.render(f"{languages[current_language]['final_score']} {score}", True, FONT_COLOR)
    prompt_txt = game_font.render("Click to restart.", True, FONT_COLOR)
    screen.blit(over_txt, (WIDTH//2 - over_txt.get_width()//2, HEIGHT//2 - 100))
    screen.blit(sc_txt, (WIDTH//2 - sc_txt.get_width()//2, HEIGHT//2 - 50))
    screen.blit(prompt_txt, (WIDTH//2 - prompt_txt.get_width()//2, HEIGHT//2 + 20))
    draw_logo()
    draw_developers()
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
                return pygame.time.get_ticks()
    if gameover_music:
        gameover_music.stop()
    pygame.mixer.music.play(-1)
    return None

# ==============================
# Main Game Loop
# ==============================
def main():
    global game_state, last_spawn_time, frozen, freeze_end_time
    player = Player()
    weapons.clear()
    clock = pygame.time.Clock()
    round_start_time = pygame.time.get_ticks()
    last_spawn_time = pygame.time.get_ticks()
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        elapsed = current_time - round_start_time
        time_remaining = max(0, (ROUND_DURATION - elapsed) // 1000)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.MOUSEBUTTONDOWN:
                if in_game_menu_button.is_clicked(e.pos):
                    go_to_menu()
            if game_state == STATE_GAME:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_UP:
                        shoot_weapon(player)
        keys = pygame.key.get_pressed()
        if game_state == STATE_GAME:
            if keys[pygame.K_LEFT]:
                player.move_left()
            if keys[pygame.K_RIGHT]:
                player.move_right()
            if elapsed < ROUND_DURATION and not game_over:
                if current_time - last_spawn_time > difficulty_levels[current_difficulty]["spawn_delay"]:
                    spawn_object()
                    last_spawn_time = current_time
            if elapsed > ROUND_DURATION and not game_over:
                new_start = show_victory_screen()
                if new_start is not None:
                    round_start_time = new_start
                else:
                    game_state = STATE_MENU
            if not frozen:
                move_objects()
            else:
                if current_time >= freeze_end_time:
                    frozen = False
            move_weapons()
            check_collisions(player)
            check_ship_collision(player)
            bg_key = selected_background if selected_background in background_images and selected_background not in ["menu", "name"] else current_difficulty
            screen.blit(background_images[bg_key], (0, 0))
            for obj in objects:
                obj.draw()
            player.draw()
            for w in weapons:
                w.draw()
            draw_score(time_remaining)
            draw_logo()
            draw_developers()
            in_game_menu_button.draw(screen)
            if game_over:
                new_start = show_game_over_screen()
                if new_start is not None:
                    round_start_time = new_start
                    reset_game_state()
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

# ==============================
# Reset Game State (for Restart)
# ==============================
def reset_game_state():
    global score, objects, weapons, game_over, combo_count, game_state, frozen
    score = 0
    objects.clear()
    weapons.clear()
    combo_count = 0
    game_over = False
    frozen = False
    game_state = STATE_GAME

# ==============================
# In-Game Menu Button and Function to Return to Main Menu
# ==============================
in_game_menu_button = Button(WIDTH - 110, HEIGHT - 50, 100, 40, "Menu")
def go_to_menu():
    reset_game_state()
    setup_game()

# ==============================
# Entry Point: Setup Menus and Name Input
# ==============================
def setup_game():
    menu_language()
    menu_difficulty()
    menu_background()
    menu_weapon()
    menu_ship()
    menu_character()
    global player_name, game_state
    player_name = input_new_name()
    print("Selected name:", player_name)
    pygame.mixer.music.play(-1)
    game_state = STATE_GAME

if __name__ == "__main__":
    setup_game()
    main()
