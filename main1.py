import pygame
import sys
import random
import math
import numpy as np
from pygame import mixer
from PIL import Image
import json
import gettext
import locale
import os
import datetime

# Initialisation de Pygame
pygame.init()
mixer.init()

# Configuration de la fenêtre
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 920
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Ninja Slicer")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Chargement des images (à remplacer par vos propres assets)
class AssetLoader:
    FRUITS = ['apple', 'banana', 'watermelon', 'pineapple']
    FRUIT_IMAGES = {}
    SLICED_IMAGES_LEFT = {}
    SLICED_IMAGES_RIGHT = {}
    SOUNDS = {}
    
    # Déplacer les ratios ici, à l'intérieur de la classe
    fruit_cut_ratios = {
        'apple': 0.52,      # La lame est légèrement décalée vers la droite
        'banana': 0.48,     # La lame est légèrement décalée vers la gauche
        'watermelon': 0.51, # La lame est presque au milieu
        'pineapple': 0.49   # La lame est légèrement décalée vers la gauche
    }
    
    @staticmethod
    def remove_background(image_path):
        # Ouvre l'image avec PIL
        img = Image.open(image_path)
        img = img.convert("RGBA")
        
        # Obtient les données des pixels
        datas = img.getdata()
        
        # Crée une nouvelle liste de pixels
        new_data = []
        
        # Définit les seuils (ajustés pour l'ananas)
        white_threshold = 230
        brown_threshold = 30  # Pour détecter le fond marron
        
        for item in datas:
            # Si le pixel est proche du blanc OU si c'est un marron foncé
            if (item[0] > white_threshold and item[1] > white_threshold and item[2] > white_threshold) or \
               (item[0] < brown_threshold and item[1] < brown_threshold and item[2] < brown_threshold):
                new_data.append((255, 255, 255, 0))  # Transparent
            else:
                new_data.append(item)  # Garde la couleur d'origine
                
        # Met à jour l'image avec les nouveaux pixels
        img.putdata(new_data)
        return img
    
    @staticmethod
    def create_fruit_halves(sliced_path, cut_ratio=0.5):
        """
        Crée les deux moitiés d'un fruit à partir de l'image coupée
        cut_ratio: position de la coupe (0.5 = milieu, 0.4 = 40% depuis la gauche, etc.)
        """
        fruit_img = Image.open(sliced_path)
        width, height = fruit_img.size
        
        # Calculer le point de coupe en fonction du ratio
        cut_point = int(width * cut_ratio)
        
        # Créer les deux moitiés avec le point de coupe personnalisé
        left_half = fruit_img.crop((0, 0, cut_point, height))
        right_half = fruit_img.crop((cut_point, 0, width, height))
        
        # Convertir en surfaces Pygame
        mode = fruit_img.mode
        size_left = left_half.size
        size_right = right_half.size
        
        left_data = left_half.tobytes()
        right_data = right_half.tobytes()
        
        left_surface = pygame.image.fromstring(left_data, size_left, mode)
        right_surface = pygame.image.fromstring(right_data, size_right, mode)
        
        return left_surface, right_surface
    
    @staticmethod
    def load_assets():
        # Charge les images des fruits normaux et coupés
        for fruit in AssetLoader.FRUITS:
            try:
                # Chargement du fruit normal
                if fruit == 'pineapple':
                    image_path = 'assets_fruits/ananas.png'
                    sliced_path = 'assets_fruits/ananas_sliced2.png'
                else:
                    image_path = f'assets_fruits/{fruit.capitalize()}.png'
                    sliced_path = f'assets_fruits/{fruit}sliced.png'
                
                # Charger l'image normale
                if fruit == 'pineapple':
                    # Suppression du fond pour l'ananas normal et coupé
                    pil_img = AssetLoader.remove_background(image_path)
                    mode = pil_img.mode
                    size = pil_img.size
                    data = pil_img.tobytes()
                    img = pygame.image.fromstring(data, size, mode)
                    
                    # Même traitement pour l'ananas coupé
                    pil_sliced = AssetLoader.remove_background(sliced_path)
                    sliced_mode = pil_sliced.mode
                    sliced_size = pil_sliced.size
                    sliced_data = pil_sliced.tobytes()
                    sliced_img = pygame.image.fromstring(sliced_data, sliced_size, sliced_mode)
                else:
                    img = pygame.image.load(image_path).convert_alpha()
                sliced_img = pygame.image.load(sliced_path).convert_alpha()
                
                # Mettre à l'échelle l'image normale
                if fruit == 'pineapple':
                    AssetLoader.FRUIT_IMAGES[fruit] = pygame.transform.scale(img, (150, 150))
                else:
                    AssetLoader.FRUIT_IMAGES[fruit] = pygame.transform.scale(img, (130, 130))
                
                # Créer les deux moitiés
                try:
                    # Utiliser le ratio de coupe spécifique à chaque fruit
                    cut_ratio = AssetLoader.fruit_cut_ratios.get(fruit, 0.5)
                    left_img, right_img = AssetLoader.create_fruit_halves(sliced_path, cut_ratio)
                    
                    # Mettre à l'échelle les moitiés
                    if fruit == 'pineapple':
                        size = (75, 150)
                    else:
                        size = (65, 130)
                        
                    AssetLoader.SLICED_IMAGES_LEFT[fruit] = pygame.transform.scale(left_img, size)
                    AssetLoader.SLICED_IMAGES_RIGHT[fruit] = pygame.transform.scale(right_img, size)
                except Exception as e:
                    print(f"Erreur lors de la découpe de {fruit}: {e}")
                    
            except Exception as e:
                print(f"Erreur de chargement pour {fruit}: {e}")
                surface = pygame.Surface((100, 100), pygame.SRCALPHA)
                pygame.draw.circle(surface, (255, 0, 0), (50, 50), 50)
                AssetLoader.FRUIT_IMAGES[fruit] = surface
                AssetLoader.SLICED_IMAGES_LEFT[fruit] = surface
                AssetLoader.SLICED_IMAGES_RIGHT[fruit] = surface
        
        # Enlever le chargement des assets manquants
        try:
            AssetLoader.BOMB_IMAGE = pygame.image.load('assets_fruits/nonfatalbomb.png').convert_alpha()
            AssetLoader.BOMB_IMAGE = pygame.transform.scale(AssetLoader.BOMB_IMAGE, (120, 120))
            
            AssetLoader.BOMB_EFFECT = pygame.image.load('assets_fruits/boooomb.png').convert_alpha()
            AssetLoader.BOMB_EFFECT = pygame.transform.scale(AssetLoader.BOMB_EFFECT, (200, 200))
            
            AssetLoader.ICE_IMAGE = pygame.image.load('assets_fruits/ice_cube.png').convert_alpha()
            AssetLoader.ICE_IMAGE = pygame.transform.scale(AssetLoader.ICE_IMAGE, (120, 120))
            
            AssetLoader.ICE_TOP = pygame.image.load('assets_fruits/ice_cube_top.png').convert_alpha()
            AssetLoader.ICE_TOP = pygame.transform.scale(AssetLoader.ICE_TOP, (120, 60))
            
            AssetLoader.ICE_BOTTOM = pygame.image.load('assets_fruits/ice_cube_bottom.png').convert_alpha()
            AssetLoader.ICE_BOTTOM = pygame.transform.scale(AssetLoader.ICE_BOTTOM, (120, 60))
            
            AssetLoader.KNIFE_IMAGE = pygame.image.load('assets_fruits/knife.png').convert_alpha()
            AssetLoader.KNIFE_IMAGE = pygame.transform.scale(AssetLoader.KNIFE_IMAGE, (100, 100))
            
            AssetLoader.BACKGROUND = pygame.image.load('assets_fruits/background.jpg').convert()
            AssetLoader.BACKGROUND = pygame.transform.scale(AssetLoader.BACKGROUND, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except Exception as e:
            print(f"Erreur de chargement des autres assets: {e}")
        
        # Charger les sons
        AssetLoader.SOUNDS = {}
        sound_files = {
            'slice': ('assets_fruits/knife_cut.mp3', 1.0),
            'game_over': ('assets_fruits/gameOver.mp3', 1.0)
        }
        
        for sound_name, (file_path, volume) in sound_files.items():
            try:
                sound = pygame.mixer.Sound(file_path)
                sound.set_volume(volume)
                AssetLoader.SOUNDS[sound_name] = sound
            except Exception as e:
                print(f"Erreur de chargement du son {sound_name}: {e}")
        
        # Charger et démarrer la musique de fond
        try:
            pygame.mixer.music.load('assets_fruits/ambiance_zik1h.mp3')
            pygame.mixer.music.set_volume(0.2)  # Volume à 20%
            pygame.mixer.music.play(-1)  # -1 pour boucle infinie
        except Exception as e:
            print(f"Erreur de chargement de la musique: {e}")
        
        # Charger les images du haut-parleur
        try:
            AssetLoader.SPEAKER_ON = pygame.image.load('assets_fruits/speaker_on_remoove.png').convert_alpha()
            AssetLoader.SPEAKER_OFF = pygame.image.load('assets_fruits/speaker_off-remove.png').convert_alpha()
            AssetLoader.SPEAKER_ON = pygame.transform.scale(AssetLoader.SPEAKER_ON, (60, 60))
            AssetLoader.SPEAKER_OFF = pygame.transform.scale(AssetLoader.SPEAKER_OFF, (60, 60))
        except Exception as e:
            print(f"Erreur de chargement des images du haut-parleur: {e}")
    
    @staticmethod
    def get_random_fruit_image():
        if not AssetLoader.FRUIT_IMAGES:
            AssetLoader.load_assets()
        # Définir des poids pour chaque fruit
        weights = {
            'apple': 0.25,
            'banana': 0.25,
            'watermelon': 0.25,
            'pineapple': 0.25  # Même probabilité pour l'ananas
        }
        fruit = random.choices(AssetLoader.FRUITS, weights=[weights[f] for f in AssetLoader.FRUITS])[0]
        return AssetLoader.FRUIT_IMAGES[fruit], fruit

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = 30

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Gravité
        self.lifetime -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, screen):
        if self.lifetime > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class GameObject:
    # Touches fixes pour chaque type d'objet
    FRUIT_KEYS = [pygame.K_a, pygame.K_z, pygame.K_e, pygame.K_r]  # AZER pour les fruits
    BOMB_KEY = pygame.K_q   # Q pour les bombes
    ICE_KEY = pygame.K_s    # S pour les glaçons
    
    def __init__(self, x, y, object_type):
        self.x = x
        self.y = y
        self.object_type = object_type
        
        # Apparence - on définit d'abord le type de fruit et la surface
        if object_type == 'fruit':
            self.surface, self.fruit_type = AssetLoader.get_random_fruit_image()
            self.sliced_surface = AssetLoader.SLICED_IMAGES_LEFT[self.fruit_type]
        elif object_type == 'bomb':
            self.surface = AssetLoader.BOMB_IMAGE
            self.fruit_type = None
        else:  # ice
            self.surface = AssetLoader.ICE_IMAGE
            self.fruit_type = None
        
        # Maintenant on peut définir la taille en fonction du type
        if object_type == 'fruit':
            self.size = 150 if self.fruit_type == 'pineapple' else 130
        else:
            self.size = 120  # Pour les bombes et les glaçons
        
        # Trajectoire parabolique ajustée
        angle = random.uniform(math.pi/3, 2*math.pi/3)  # Garde l'angle entre 60° et 120°
        speed = random.uniform(18, 22)  # Vitesse réduite
        self.vx = math.cos(angle) * speed
        self.vy = -math.sin(angle) * speed
        
        # Rotation
        self.angle = 0
        self.rotation_speed = random.uniform(-8, 8)
            
        self.sliced = False
        self.particles = []
        self.gravity = 0.45  # Gravité légèrement augmentée
        self.slice_time = 0
        self.disappear_delay = 1000  # Temps en ms avant de disparaître
        self.ice_parts = []
        self.ice_velocities = []
        self.fruit_positions = []  # Pour stocker la position des fruits coupés
        self.fruit_velocities = []  # Pour stocker les vélocités des fruits coupés
        self.zone = self.get_zone(x)
        
        # Attribuer une touche selon le type d'objet
        if object_type == 'fruit':
            self.key = random.choice(GameObject.FRUIT_KEYS)
        elif object_type == 'bomb':
            self.key = GameObject.BOMB_KEY
        else:  # ice
            self.key = GameObject.ICE_KEY
            
        self.key_char = pygame.key.name(self.key).upper()

    def get_zone(self, x):
        # Diviser l'écran en 4 zones (A, Z, E, R)
        zone_width = WINDOW_WIDTH / 4
        if x < zone_width:
            return 'A'
        elif x < zone_width * 2:
            return 'Z'
        elif x < zone_width * 3:
            return 'E'
        else:
            return 'R'

    def update(self):
        if not self.sliced:
            # Mise à jour normale pour tous les objets non coupés
            self.x += self.vx
            self.y += self.vy
            self.vy += self.gravity
            self.angle += self.rotation_speed
        elif self.object_type == 'ice' and self.ice_parts:
            # Mettre à jour la position des parties du glaçon
            for i in range(len(self.ice_positions)):
                # Appliquer la gravité aux vélocités
                self.ice_velocities[i][1] += self.gravity * 1.5  # Gravité plus forte pour les glaçons
                self.ice_velocities[i][0] *= 0.98  # Plus de friction horizontale
                
                # Mettre à jour les positions
                self.ice_positions[i][0] += self.ice_velocities[i][0]
                self.ice_positions[i][1] += self.ice_velocities[i][1]
                
                # Faire tourner les morceaux plus rapidement
                self.angle += self.rotation_speed * 1.5
        elif self.object_type == 'fruit' and self.fruit_positions:
            # Mettre à jour la position des parties du fruit
            for i in range(len(self.fruit_positions)):
                self.fruit_velocities[i][1] += self.gravity
                self.fruit_velocities[i][0] *= 0.99
                self.fruit_positions[i][0] += self.fruit_velocities[i][0]
                self.fruit_positions[i][1] += self.fruit_velocities[i][1]

    def draw(self, screen):
        current_time = pygame.time.get_ticks()
        
        # Si l'objet est coupé depuis trop longtemps, ne pas le dessiner
        if self.sliced and current_time - self.slice_time > self.disappear_delay:
            return

        if self.sliced:
            if self.object_type == 'fruit':
                # Dessiner les deux moitiés du fruit
                left_surface = pygame.transform.rotate(AssetLoader.SLICED_IMAGES_LEFT[self.fruit_type], self.angle)
                right_surface = pygame.transform.rotate(AssetLoader.SLICED_IMAGES_RIGHT[self.fruit_type], self.angle)
                
                # Position de chaque moitié
                left_rect = left_surface.get_rect(center=(self.fruit_positions[0][0], self.fruit_positions[0][1]))
                right_rect = right_surface.get_rect(center=(self.fruit_positions[1][0], self.fruit_positions[1][1]))
                
                # Dessiner les deux moitiés
                screen.blit(left_surface, left_rect)
                screen.blit(right_surface, right_rect)
                return
            elif self.object_type == 'ice':
                # Dessiner les deux parties du glaçon
                for i, (part, pos) in enumerate(zip(self.ice_parts, self.ice_positions)):
                    rotated_surface = pygame.transform.rotate(part, self.angle)
                    rect = rotated_surface.get_rect(center=(pos[0], pos[1]))
                    screen.blit(rotated_surface, rect)
                return
        
        # Si l'objet n'est pas coupé, dessiner normalement
        rotated_surface = pygame.transform.rotate(self.surface, self.angle)
        rect = rotated_surface.get_rect(center=(self.x, self.y))
        screen.blit(rotated_surface, rect)
        
        # Afficher la lettre au-dessus de l'objet avec un meilleur style
        if not self.sliced:
            # Plus grande taille de police
            font = pygame.font.Font(None, 48)  # Augmenté de 36 à 48
            
            # Créer le contour noir
            shadow_text = font.render(self.key_char, True, BLACK)
            shadow_rect = shadow_text.get_rect(center=(self.x, self.y - self.size/2 - 25))
            
            # Créer le texte blanc
            key_text = font.render(self.key_char, True, WHITE)
            text_rect = key_text.get_rect(center=(self.x, self.y - self.size/2 - 25))
            
            # Dessiner le contour en décalant légèrement le texte noir
            for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                screen.blit(shadow_text, (shadow_rect.x + dx, shadow_rect.y + dy))
            
            # Dessiner le texte blanc par-dessus
            screen.blit(key_text, text_rect)

    def slice(self):
        if not self.sliced:
            self.sliced = True
            self.slice_time = pygame.time.get_ticks()
            
            if self.object_type == 'ice':
                # Créer les deux parties du glaçon
                self.ice_parts = [AssetLoader.ICE_TOP, AssetLoader.ICE_BOTTOM]
                # Positions initiales des deux parties BEAUCOUP plus éloignées
                self.ice_positions = [
                    [self.x - 80, self.y - 100],  # Partie supérieure : beaucoup plus écartée
                    [self.x + 80, self.y + 100]   # Partie inférieure : beaucoup plus écartée
                ]
                # Vélocités BEAUCOUP plus importantes pour le glaçon
                self.ice_velocities = [
                    [-25, -35],  # Partie supérieure : explose très fort vers le haut-gauche
                    [25, 15]     # Partie inférieure : explose très fort vers le bas-droite
                ]
            elif self.object_type == 'fruit':
                # Créer deux positions pour les moitiés du fruit
                self.fruit_positions = [
                    [self.x - 20, self.y - 20],  # Moitié gauche : moins décalée
                    [self.x + 20, self.y + 20]   # Moitié droite : moins décalée
                ]
                # Vélocités réduites pour les fruits
                self.fruit_velocities = [
                    [-8, -15],  # Moitié gauche : monte moins haut et va moins loin
                    [8, 3]      # Moitié droite : descend doucement
                ]
            
            # Création de particules lors de la découpe
            particle_color = (200, 200, 255) if self.object_type == 'ice' else (random.randint(100, 255), random.randint(100, 255), 0)
            for _ in range(20):
                self.particles.append(Particle(self.x, self.y, particle_color))

    def is_clicked(self, pos):
        distance = math.sqrt((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2)
        return distance < self.size/2

class Trail:
    def __init__(self):
        self.points = []
        self.max_length = 20  # Plus long pour un meilleur effet
        # Couleurs futuristes : dégradé de bleu néon vers blanc
        self.colors = []
        for i in range(20):
            progress = i / 20
            # Mélange de bleu néon et blanc
            r = int(0 + (255 - 0) * progress)
            g = int(191 + (255 - 191) * progress)
            b = 255
            a = min(255, int(255 * (i+10)/20))  # Plus opaque
            self.colors.append((r, g, b, a))

    def add_point(self, pos):
        self.points.append(pos)
        if len(self.points) > self.max_length:
            self.points.pop(0)

    def draw(self, screen):
        if len(self.points) > 1:
            # Effet de lueur (glow effect)
            for i in range(len(self.points)-1):
                start = self.points[i]
                end = self.points[i+1]
                
                # Dessiner plusieurs lignes de différentes épaisseurs pour l'effet de lueur
                pygame.draw.line(screen, (0, 100, 255, 50), start, end, 20)  # Lueur externe
                pygame.draw.line(screen, (100, 200, 255, 100), start, end, 15)  # Lueur moyenne
                pygame.draw.line(screen, self.colors[i], start, end, 10)  # Ligne principale
                
                # Ligne centrale blanche pour l'effet néon
                pygame.draw.line(screen, (255, 255, 255, 255), start, end, 4)

class AnimatedHeart:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.animation_speed = 0.2
        self.animation_time = 0
        self.frames = []
        
        # Charger toutes les frames du GIF
        try:
            gif = Image.open('assets_fruits/animated-heart-image-0503.gif')
            for frame_index in range(gif.n_frames):
                gif.seek(frame_index)
                frame = gif.convert('RGBA')
                frame_surface = pygame.image.fromstring(
                    frame.tobytes(), frame.size, frame.mode
                )
                # Encore plus grands cœurs (100,100 -> 120,120)
                frame_surface = pygame.transform.scale(frame_surface, (120, 120))
                self.frames.append(frame_surface)
        except Exception as e:
            print(f"Erreur de chargement du cœur animé: {e}")
            # Cœur par défaut aussi plus grand
            surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 0, 0), (60, 60), 60)
            self.frames = [surface]

    def update(self):
        self.animation_time += self.animation_speed
        self.frame = int(self.animation_time) % len(self.frames)

    def draw(self, screen):
        screen.blit(self.frames[self.frame], (self.x, self.y))

class ComboAnimation:
    def __init__(self, x, y, points, combo_size):
        self.x = x
        self.y = y
        self.points = points
        self.combo_size = combo_size  # Nombre de fruits dans le combo
        self.lifetime = 60  # Durée de l'animation en frames
        self.current_frame = 0
        self.font = pygame.font.Font(None, 74)
        self.colors = [
            (255, 255, 0),    # Jaune
            (255, 165, 0),    # Orange
            (255, 0, 0)       # Rouge
        ]
        
    def update(self):
        self.current_frame += 1
        return self.current_frame < self.lifetime
        
    def draw(self, screen):
        # Calculer la taille du texte (grandit puis rétrécit)
        progress = self.current_frame / self.lifetime
        if progress < 0.5:
            scale = 1 + progress * 2  # Grandit jusqu'à 2x
        else:
            scale = 3 - progress * 2  # Rétrécit
            
        # Faire varier la couleur
        color_index = min(self.combo_size - 1, len(self.colors) - 1)
        color = self.colors[color_index]
        
        # Texte du combo
        if self.combo_size >= 4:
            text = f"MEGA COMBO! +{self.points}"  # 4+ fruits = 3 points
        elif self.combo_size == 3:
            text = f"TRIPLE! +{self.points}"      # 3 fruits = 2 points
        else:
            text = f"+{self.points}"              # 1-2 fruits = 1 point
            
        # Rendre le texte avec la taille actuelle
        base_size = 74
        current_size = int(base_size * scale)
        font = pygame.font.Font(None, current_size)
        text_surface = font.render(text, True, color)
        
        # Position avec un petit mouvement vers le haut
        y_offset = -50 * progress  # Monte progressivement
        pos = (self.x - text_surface.get_width()//2, 
               self.y - text_surface.get_height()//2 + y_offset)
        
        screen.blit(text_surface, pos)

class Scoreboard:
    def __init__(self):
        self.scores = {
            'facile': [],
            'moyen': [],
            'difficile': []
        }
        self.filename = 'highscores.json'
        self.load_scores()
    
    def load_scores(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    self.scores = json.load(f)
            else:
                # Créer le fichier avec une structure par défaut
                self.save_scores()
                print("Nouveau fichier de scores créé!")
        except Exception as e:
            print(f"Erreur lors du chargement des scores: {e}")
            self.save_scores()  # Créer un nouveau fichier en cas d'erreur
    
    def save_scores(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.scores, f, indent=4)  # indent=4 pour un format plus lisible
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des scores: {e}")
    
    def add_score(self, difficulty, name, score):
        if difficulty not in self.scores:
            self.scores[difficulty] = []
        
        # Ajouter le nouveau score
        self.scores[difficulty].append({
            'name': name,
            'score': score,
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Ajouter la date
        })
        
        # Trier et garder les 10 meilleurs
        self.scores[difficulty] = sorted(
            self.scores[difficulty], 
            key=lambda x: x['score'], 
            reverse=True
        )[:10]
        
        self.save_scores()
    
    def get_top_scores(self, difficulty):
        return self.scores.get(difficulty, [])

class NameInput:
    def __init__(self, score, difficulty):
        self.score = score
        self.difficulty = difficulty
        self.name = ""
        self.font = pygame.font.Font(None, 74)
        self.done = False
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and self.name:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            elif len(self.name) < 10 and event.unicode.isalnum():
                self.name += event.unicode
        return False
    
    def draw(self, screen):
        screen.fill(BLACK)
        
        # Afficher le score
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, 200))
        
        # Afficher l'invite de saisie
        prompt = self.font.render('Entrez votre pseudo:', True, WHITE)
        screen.blit(prompt, (WINDOW_WIDTH//2 - prompt.get_width()//2, 300))
        
        # Afficher le pseudo
        name_text = self.font.render(self.name + "_", True, WHITE)
        screen.blit(name_text, (WINDOW_WIDTH//2 - name_text.get_width()//2, 400))

class Translation:
    TEXTS = {
        'fr': {
            'play': 'Jouer',
            'scores': 'Voir les scores',
            'language': 'Langue FR',
            'quit': 'Quitter',
            'easy': 'Facile',
            'medium': 'Moyen',
            'hard': 'Difficile',
            'game_over': 'Partie terminée! Appuyez sur ESPACE pour recommencer',
            'score': 'Score',
            'best_score': 'Meilleur score',
            'combo': 'Combo x{}',
            'enter_name': 'Entrez votre pseudo:',
            'press_enter': 'Appuyez sur Entrée pour continuer',
            'high_scores': 'Meilleurs Scores',
            'back': 'Retour'
        },
        'en': {
            'play': 'Play',
            'scores': 'High Scores',
            'language': 'Language EN',
            'quit': 'Quit',
            'easy': 'Easy',
            'medium': 'Medium',
            'hard': 'Hard',
            'game_over': 'Game Over! Press SPACE to restart',
            'score': 'Score',
            'best_score': 'Best Score',
            'combo': 'Combo x{}',
            'enter_name': 'Enter your username:',
            'press_enter': 'Press Enter to continue',
            'high_scores': 'High Scores',
            'back': 'Back'
        }
    }

    def __init__(self):
        self.current_language = 'fr'  # Langue par défaut

    def get_text(self, key):
        return self.TEXTS[self.current_language][key]

    def switch_language(self):
        # Simplement alterner entre FR et EN
        self.current_language = 'en' if self.current_language == 'fr' else 'fr'

class Game:
    # Paramètres de difficulté
    DIFFICULTY_SETTINGS = {
        'facile': {
            'spawn_interval': 800,     # Plus rapide pour plus de fruits
            'min_interval': 600,       # Reste assez rapide
            'spawn_count': 5,          # 5 objets en même temps
            'weights': [0.95, 0.02, 0.03]  # 95% fruits, 2% bombes, 3% glaçons - Idéal pour les combos
        },
        'moyen': {
            'spawn_interval': 1000,    # Normal
            'min_interval': 500,       # Vitesse moyenne
            'spawn_count': 5,          # 5 objets en même temps
            'weights': [0.80, 0.15, 0.05]  # 80% fruits, 15% bombes, 5% glaçons - Équilibré
        },
        'difficile': {
            'spawn_interval': 600,     # Très rapide
            'min_interval': 300,       # Devient super rapide
            'spawn_count': 5,          # 5 objets en même temps
            'weights': [0.70, 0.25, 0.05]  # 70% fruits, 25% bombes, 5% glaçons - Plus dangereux
        }
    }

    def __init__(self, difficulty='moyen', player_name=''):
        self.difficulty = difficulty
        self.player_name = player_name
        self.translation = Translation()  # Initialiser la traduction
        self.settings = Game.DIFFICULTY_SETTINGS[difficulty]
        
        self.score = 0
        self.strikes = 0
        self.lives = 3
        self.game_over = False
        self.combo_timer = 0
        self.combo_count = 0
        self.frozen_time = 0
        self.objects = []
        self.trail = Trail()
        self.font = pygame.font.Font(None, 36)
        self.last_spawn = 0
        self.spawn_interval = self.settings['spawn_interval']
        self.high_score = 0
        self.combo_multiplier = 1
        self.music_on = True
        self.speaker_rect = pygame.Rect(WINDOW_WIDTH - 80, 20, 60, 60)  # Position en haut à droite
        self.mouse_pressed = False
        self.combo_window = 500  # 500ms pour tous les combos
        self.last_slice_time = 0
        self.current_combo_fruits = []
        self.game_over_sound_played = False  # Ajouter cette variable
        self.scoreboard = Scoreboard()
        
        # Créer un fond noir par défaut
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background.fill((0, 0, 0))
        
        try:
            self.background = pygame.image.load('assets_fruits/background.jpg').convert()
            self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except Exception as e:
            print(f"Erreur de chargement du fond: {e}")

        self.hearts = [
            AnimatedHeart(20 + i * 110, 60) for i in range(3)
        ]
        self.combo_animations = []  # Liste pour stocker les animations en cours
        self.key_zones = {
            pygame.K_a: 'A',
            pygame.K_z: 'Z',
            pygame.K_e: 'E',
            pygame.K_r: 'R'
        }

    def spawn_object(self):
        for _ in range(random.randint(1, self.settings['spawn_count'])):
            x = random.randint(100, WINDOW_WIDTH - 100)
            weights = self.settings['weights']
            object_type = random.choices(['fruit', 'bomb', 'ice'], weights=weights)[0]
            self.objects.append(GameObject(x, WINDOW_HEIGHT, object_type))

    def update(self):
        current_time = pygame.time.get_ticks()
        
        if self.frozen_time > current_time:
            return
        
        if current_time - self.last_spawn > self.spawn_interval and not self.game_over:
            self.spawn_object()
            self.last_spawn = current_time
            # Accélération progressive avec limite minimale selon la difficulté
            self.spawn_interval = max(self.settings['min_interval'], 
                                    self.spawn_interval - 1)

        # Mise à jour des objets
        for obj in self.objects[:]:
            obj.update()
            if obj.y > WINDOW_HEIGHT + 100:
                if not obj.sliced and obj.object_type == 'fruit':
                    self.strikes += 1
                    if self.strikes >= 3:
                        self.end_game()  # Utiliser la nouvelle méthode
                self.objects.remove(obj)

        # Mettre à jour l'animation des cœurs
        for heart in self.hearts:
            heart.update()

        # Mettre à jour les animations de combo
        self.combo_animations = [anim for anim in self.combo_animations if anim.update()]

    def draw(self, screen):
        # Affichage du fond
        screen.blit(self.background, (0, 0))
        
        # Dessin de la trainée du curseur
        self.trail.draw(screen)
        
        # Dessin des objets
        for obj in self.objects:
            obj.draw(screen)

        # Interface utilisateur
        score_text = self.font.render(f"{self.translation.get_text('score')}: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Affichage des vies avec les cœurs animés
        for i, heart in enumerate(self.hearts):
            if i < (3 - self.strikes):  # Affiche uniquement les cœurs restants
                heart.draw(screen)

        if self.game_over:
            # Utiliser la traduction pour le message de game over
            game_over_text = self.font.render(
                self.translation.get_text('game_over'), 
                True, RED
            )
            screen.blit(game_over_text, (WINDOW_WIDTH//2 - game_over_text.get_width()//2, WINDOW_HEIGHT//2))
            
        # Affichage du couteau à la position de la souris
        mouse_pos = pygame.mouse.get_pos()
        knife_rect = AssetLoader.KNIFE_IMAGE.get_rect(center=mouse_pos)
        screen.blit(AssetLoader.KNIFE_IMAGE, knife_rect)

        # Affichage du meilleur score
        high_score_text = self.font.render(
            f"{self.translation.get_text('best_score')}: {self.high_score}", 
            True, WHITE
        )
        screen.blit(high_score_text, (WINDOW_WIDTH - 250, 10))
        
        # Affichage du multiplicateur de combo
        if self.combo_count > 1:
            combo_text = self.font.render(
                self.translation.get_text('combo').format(self.combo_multiplier), 
                True, (255, 255, 0))
            screen.blit(combo_text, (WINDOW_WIDTH//2 - 50, 10))

        # Afficher l'icône du haut-parleur
        speaker_img = AssetLoader.SPEAKER_ON if self.music_on else AssetLoader.SPEAKER_OFF
        screen.blit(speaker_img, self.speaker_rect)

        # Dessiner les animations de combo
        for anim in self.combo_animations:
            anim.draw(screen)

    def slice_at_position(self, pos):
        if self.game_over:
            return

        sliced_objects = []
        current_time = pygame.time.get_ticks()
        
        # Créer une ligne entre le point précédent et le point actuel de la souris
        if len(self.trail.points) > 1:
            prev_pos = self.trail.points[-2]
            current_pos = self.trail.points[-1]
            
            # Calculer le vecteur de direction
            dx = current_pos[0] - prev_pos[0]
            dy = current_pos[1] - prev_pos[1]
            movement_length = math.sqrt(dx*dx + dy*dy)
            
            # Ne couper que si la souris bouge suffisamment vite
            if movement_length > 5:
                for obj in self.objects:
                    if not obj.sliced:
                        x0, y0 = obj.x, obj.y
                        x1, y1 = prev_pos
                        x2, y2 = current_pos
                        
                        # Calculer la distance point-ligne
                        numerator = abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1)
                        denominator = math.sqrt((y2-y1)**2 + (x2-x1)**2)
                        
                        if denominator != 0:
                            distance = numerator/denominator
                            
                            # Vérifier si le point est entre les deux points de la ligne
                            dot_product = ((x0-x1)*(x2-x1) + (y0-y1)*(y2-y1)) / (denominator * denominator)
                            
                            # Zone de coupe plus précise selon le type d'objet
                            cut_threshold = obj.size/3 if obj.object_type == 'bomb' else obj.size/2
                            
                            # Ne couper que si l'objet est vraiment sur la trajectoire
                            if distance < cut_threshold and 0 <= dot_product <= 1:
                                obj.slice()
                                sliced_objects.append(obj)
                                try:
                                    AssetLoader.SOUNDS['slice'].play()  # Son de coupe
                                    if obj.object_type == 'bomb':
                                        self.game_over = True
                                        AssetLoader.SOUNDS['game_over'].play()
                                    elif obj.object_type == 'ice':
                                        AssetLoader.SOUNDS['slice'].play()
                                        self.frozen_time = current_time + random.randint(3000, 5000)  # Effet de gel
                                    elif obj.object_type == 'fruit':
                                        AssetLoader.SOUNDS['slice'].play()
                                except Exception as e:
                                    print(f"Erreur lors de la lecture du son: {e}")
        
        # Gestion des combos avec une seule fenêtre de temps
        fruits_sliced = [obj for obj in sliced_objects if obj.object_type == 'fruit']
        if fruits_sliced:
            current_time = pygame.time.get_ticks()
            time_since_last = current_time - self.last_slice_time
            
            # Si on est dans la fenêtre de temps
            if time_since_last < self.combo_window:
                self.current_combo_fruits.extend(fruits_sliced)
            else:
                # Nouveau combo
                self.current_combo_fruits = fruits_sliced.copy()
            
            self.last_slice_time = current_time
            
            # Calculer les points basés sur le combo total
            combo_size = len(self.current_combo_fruits)
            if combo_size == 1:
                points = 1
            elif combo_size == 2:
                points = 1
            elif combo_size == 3:
                points = 2
            else:
                points = 3
            
            self.score += points
            if self.score > self.high_score:
                self.high_score = self.score
            
            # Animation de combo
            if sliced_objects:
                center_x = sum(obj.x for obj in sliced_objects) / len(sliced_objects)
                center_y = sum(obj.y for obj in sliced_objects) / len(sliced_objects)
                self.combo_animations.append(
                    ComboAnimation(center_x, center_y, points, combo_size)
                )
        
        # Réinitialiser le combo si on dépasse la fenêtre de temps
        elif current_time - self.last_slice_time >= self.combo_window:
            self.current_combo_fruits = []

    def handle_key(self, key):
        if self.game_over:
            return
            
        sliced_objects = []
        current_time = pygame.time.get_ticks()
        
        # Vérifier tous les objets qui correspondent à cette touche
        for obj in self.objects:
            if not obj.sliced and obj.key == key:
                obj.slice()
                sliced_objects.append(obj)
                try:
                    AssetLoader.SOUNDS['slice'].play()  # Jouer le son de coupe
                    if obj.object_type == 'bomb':
                        self.game_over = True
                        AssetLoader.SOUNDS['game_over'].play()
                    elif obj.object_type == 'ice':
                        AssetLoader.SOUNDS['slice'].play()
                        self.frozen_time = current_time + random.randint(3000, 5000)  # Effet de gel
                    elif obj.object_type == 'fruit':
                        AssetLoader.SOUNDS['slice'].play()
                except Exception as e:
                    print(f"Erreur lors de la lecture du son: {e}")
        
        # Calculer les points comme avant...
        fruits_sliced = sum(1 for obj in sliced_objects if obj.object_type == 'fruit')
        if fruits_sliced > 0:
            if fruits_sliced == 1:
                points = 1
            elif fruits_sliced == 2:
                points = 1
            elif fruits_sliced == 3:
                points = 2
            else:
                points = 3
            
            self.score += points
            if self.score > self.high_score:
                self.high_score = self.score
            
            # Animation de combo
            if sliced_objects:
                center_x = sum(obj.x for obj in sliced_objects) / len(sliced_objects)
                center_y = sum(obj.y for obj in sliced_objects) / len(sliced_objects)
                self.combo_animations.append(
                    ComboAnimation(center_x, center_y, points, fruits_sliced)
                )

    def end_game(self):
        if not self.game_over:
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
            if not self.game_over_sound_played:
                AssetLoader.SOUNDS['game_over'].play()
                self.game_over_sound_played = True
            # Sauvegarder le score avec le pseudo
            self.scoreboard.add_score(self.difficulty, self.player_name, self.score)
            return NameInput(self.score, self.difficulty)
        return None

    def reset(self):
        self.__init__(self.difficulty, self.player_name)

class Menu:
    def __init__(self):
        self.font = pygame.font.Font(None, 74)
        self.translation = Translation()
        self.state = 'main'
        self.selected = 0
        self.main_options = [
            self.translation.get_text('play'),
            self.translation.get_text('scores'),
            self.translation.get_text('language'),
            self.translation.get_text('quit')
        ]
        self.difficulty_options = [
            self.translation.get_text('easy'),
            self.translation.get_text('medium'),
            self.translation.get_text('hard')
        ]
        self.option_rects = []
        self.player_name = ""
        self.scoreboard = Scoreboard()
        
        # Effets d'animation
        self.hover_scale = 1.0
        self.target_scale = 1.0
        self.animation_speed = 0.2
        self.option_positions = []
        self.current_positions = []
        self.hover_offset = 0
        self.time = 0
        
        # Charger le background
        try:
            background_path = 'assets_fruits/background_menu2.jpg'
            pil_image = Image.open(background_path)
            pil_image = pil_image.resize((WINDOW_WIDTH, WINDOW_HEIGHT), Image.Resampling.LANCZOS)
            mode = pil_image.mode
            size = pil_image.size
            data = pil_image.tobytes()
            self.background = pygame.image.fromstring(data, size, mode)
        except Exception as e:
            print(f"Erreur de chargement du background menu: {str(e)}")
            self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            self.background.fill(BLACK)
        
        # Modifier la position et la taille du bouton de langue
        self.language_button = pygame.Rect(20, 20, 150, 50)  # Plus grand et en haut à gauche
        self.music_on = True
        self.speaker_rect = pygame.Rect(WINDOW_WIDTH - 80, 20, 60, 60)  # Position en haut à droite

    def update_animations(self):
        self.time += 0.05
        # Animation de flottement
        self.hover_offset = math.sin(self.time) * 10
        
        # Animation d'échelle au survol
        self.hover_scale += (self.target_scale - self.hover_scale) * self.animation_speed
        
        # Mise à jour des positions
        for i in range(len(self.current_positions)):
            target = self.option_positions[i]
            current = self.current_positions[i]
            self.current_positions[i] = current + (target - current) * 0.2
    
    def render_text(self, text, color):
        # Méthode simplifiée pour le rendu du texte
        return self.font.render(text, True, color)

    def draw_main_menu(self, screen):
        # Initialiser les positions si nécessaire
        if not self.option_positions:
            self.option_positions = [300 + i * 100 for i in range(len(self.main_options))]
            self.current_positions = self.option_positions.copy()
        
        # Mettre à jour les animations
        self.update_animations()
        
        for i, option in enumerate(self.main_options):
            # Enlever la condition spéciale pour l'option langue
            color = RED if i == self.selected else WHITE
            text = self.render_text(option, color)
            
            # Mise à l'échelle et positionnement
            base_width = text.get_width()
            base_height = text.get_height()
            scaled_width = int(base_width * self.hover_scale)
            scaled_height = int(base_height * self.hover_scale)
            text = pygame.transform.scale(text, (scaled_width, scaled_height))
            text_rect = text.get_rect(center=(WINDOW_WIDTH//2, self.current_positions[i]))
            
            screen.blit(text, text_rect)
            self.option_rects.append(text_rect)
    
    def handle_input(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Effet de survol fluide
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(event.pos):
                    self.selected = i
                    self.target_scale = 1.2
                    break
                else:
                    self.target_scale = 1.0
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Vérifier d'abord si on clique sur le haut-parleur
            if self.speaker_rect.collidepoint(event.pos):
                self.music_on = not self.music_on
                pygame.mixer.music.set_volume(0.2 if self.music_on else 0)
                return None
                
            # Reste de la gestion des clics
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(event.pos):
                    if self.state == 'main':
                        if i == 0:  # Jouer
                            self.state = 'name_input'
                            return None
                        elif i == 1:  # Voir les scores
                            self.state = 'scores'
                        elif i == 2:  # Changer de langue
                            self.translation.switch_language()
                            # Mettre à jour les textes
                            self.main_options = [
                                self.translation.get_text('play'),
                                self.translation.get_text('scores'),
                                self.translation.get_text('language'),
                                self.translation.get_text('quit')
                            ]
                            self.difficulty_options = [
                                self.translation.get_text('easy'),
                                self.translation.get_text('medium'),
                                self.translation.get_text('hard')
                            ]
                        elif i == 3:  # Quitter
                            return 'quit'
                    elif self.state == 'difficulty':
                        return self.difficulty_options[i].lower()
                    elif self.state == 'scores':
                        self.state = 'main'
        
        elif event.type == pygame.KEYDOWN and self.state == 'name_input':
            if event.key == pygame.K_RETURN and self.player_name:  # Si on appuie sur Entrée
                self.state = 'difficulty'  # Passer au choix de la difficulté
            elif event.key == pygame.K_BACKSPACE:  # Si on appuie sur Retour arrière
                self.player_name = self.player_name[:-1]  # Supprimer le dernier caractère
            elif len(self.player_name) < 10 and event.unicode.isalnum():  # Si c'est une lettre ou un chiffre
                self.player_name += event.unicode  # Ajouter le caractère au pseudo
        
        return None

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        self.option_rects = []
        
        # Dessiner le haut-parleur
        speaker_img = AssetLoader.SPEAKER_ON if self.music_on else AssetLoader.SPEAKER_OFF
        screen.blit(speaker_img, self.speaker_rect)
        
        if self.state == 'main':
            self.draw_main_menu(screen)
        elif self.state == 'name_input':
            self.draw_name_input(screen)
        elif self.state == 'difficulty':
            self.draw_difficulty_menu(screen)
        elif self.state == 'scores':
            self.draw_scores(screen)
    
    def draw_difficulty_menu(self, screen):
        # Initialiser les positions si nécessaire
        if not self.option_positions:
            self.option_positions = [300 + i * 100 for i in range(len(self.difficulty_options))]
            self.current_positions = self.option_positions.copy()
        
        # Mettre à jour les animations
        self.update_animations()
        
        for i, option in enumerate(self.difficulty_options):
            # Même effet que pour le menu principal
            scale = self.hover_scale if i == self.selected else 1.0
            y = self.current_positions[i]
            if i == self.selected:
                y += self.hover_offset
                pulse = math.sin(self.time * 3) * 0.05 + 1.0
                scale *= pulse
            
            color = RED if i == self.selected else WHITE
            
            if i == self.selected:
                glow_surf = pygame.Surface((400, 100), pygame.SRCALPHA)
                for radius in range(10, 0, -2):
                    text = self.render_text(option, color)
                    text_rect = text.get_rect(center=(200, 50))
                    text = pygame.transform.scale(text, 
                        (int(text_rect.width * (1 + radius/100)), 
                         int(text_rect.height * (1 + radius/100))))
                    text_rect = text.get_rect(center=(200, 50))
                    glow_surf.blit(text, text_rect)
            
            text = self.render_text(option, color)
            base_width = text.get_width()
            base_height = text.get_height()
            
            scaled_width = int(base_width * scale)
            scaled_height = int(base_height * scale)
            text = pygame.transform.scale(text, (scaled_width, scaled_height))
            text_rect = text.get_rect(center=(WINDOW_WIDTH//2, y))
            
            if i == self.selected:
                glow_rect = glow_surf.get_rect(center=(WINDOW_WIDTH//2, y))
                screen.blit(glow_surf, glow_rect)
            screen.blit(text, text_rect)
            
            self.option_rects.append(text_rect)

    def draw_scores(self, screen):
        title = self.font.render(self.translation.get_text('high_scores'), True, WHITE)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 50))
        
        y = 150
        for difficulty in ['facile', 'moyen', 'difficile']:
            # Titre de la difficulté
            diff_text = self.font.render(difficulty.upper(), True, RED)
            screen.blit(diff_text, (WINDOW_WIDTH//2 - diff_text.get_width()//2, y))
            
            # Scores pour cette difficulté
            scores = self.scoreboard.get_top_scores(difficulty)[:5]  # Top 5
            y += 50
            for i, score in enumerate(scores):
                score_text = pygame.font.Font(None, 36).render(
                    f"{i+1}. {score['name']}: {score['score']}", 
                    True, WHITE
                )
                screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, y))
                y += 30
            
            y += 50  # Espace entre les difficultés
        
        # Bouton retour
        back_text = self.font.render(self.translation.get_text('back'), True, WHITE)
        back_rect = back_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 50))
        screen.blit(back_text, back_rect)
        self.option_rects = [back_rect]

    def draw_name_input(self, screen):
        # Afficher le fond
        screen.blit(self.background, (0, 0))
        
        # Titre
        title = self.font.render(self.translation.get_text('enter_name'), True, WHITE)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 200))
        
        # Zone de saisie
        name_text = self.font.render(self.player_name + "_", True, WHITE)
        screen.blit(name_text, (WINDOW_WIDTH//2 - name_text.get_width()//2, 300))
        
        # Instructions
        info = pygame.font.Font(None, 36).render(
            self.translation.get_text('press_enter'), True, WHITE
        )
        screen.blit(info, (WINDOW_WIDTH//2 - info.get_width()//2, 400))

def main():
    clock = pygame.time.Clock()
    AssetLoader.load_assets()
    
    menu = Menu()
    game = None
    in_menu = True
    
    # Dictionnaire de conversion des difficultés
    difficulty_convert = {
        'easy': 'facile',
        'medium': 'moyen',
        'hard': 'difficile',
        # Garder aussi les versions françaises pour quand on joue en français
        'facile': 'facile',
        'moyen': 'moyen',
        'difficile': 'difficile'
    }
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif in_menu:
                result = menu.handle_input(event)
                if result == 'quit':
                    running = False
                elif result in difficulty_convert:
                    # Créer le jeu avec le pseudo
                    game = Game(
                        difficulty=difficulty_convert[result],
                        player_name=menu.player_name
                    )
                    # Transférer la langue actuelle du menu au jeu
                    game.translation.current_language = menu.translation.current_language
                    in_menu = False
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if game.speaker_rect.collidepoint(mouse_pos):
                        # Gestion du son
                        game.music_on = not game.music_on
                        pygame.mixer.music.set_volume(0.2 if game.music_on else 0)
                    else:
                        # Activer la coupe si on ne clique pas sur le haut-parleur
                        game.mouse_pressed = True
                        game.slice_at_position(mouse_pos)  # Commencer la coupe immédiatement
                elif event.type == pygame.MOUSEBUTTONUP:
                    game.mouse_pressed = False
                elif event.type == pygame.MOUSEMOTION and game.mouse_pressed:
                    # Continuer la coupe pendant le mouvement si le bouton est enfoncé
                    game.slice_at_position(pygame.mouse.get_pos())
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and game.game_over:
                        in_menu = True
                        menu = Menu()
                    else:
                        game.handle_key(event.key)
        
        if in_menu:
            menu.draw(screen)
        else:
            mouse_pos = pygame.mouse.get_pos()
            game.trail.add_point(mouse_pos)
            game.update()
            game.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
