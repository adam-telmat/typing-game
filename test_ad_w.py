import pygame
import random
import math
from pygame import mixer

# Initialisation de Pygame
pygame.init()

# Configuration de la fenêtre
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Fruit Ninja")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Variables du jeu
score = 0
strikes = 0
game_over = False
combo_timer = 0
combo_count = 0
frozen_time = 0

class GameObject:
    def __init__(self, x, y, object_type):
        self.x = x
        self.y = y
        self.speed_x = random.randint(-5, 5)
        self.speed_y = -15  # Vitesse initiale vers le haut
        self.object_type = object_type  # 'fruit', 'bomb', 'ice'
        self.sliced = False
        self.gravity = 0.5

    def update(self):
        if not self.sliced:
            self.x += self.speed_x
            self.y += self.speed_y
            self.speed_y += self.gravity

    def is_clicked(self, pos):
        # Distance entre le point de clic et l'objet
        distance = math.sqrt((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2)
        return distance < 30  # Rayon de collision

def spawn_object():
    x = random.randint(100, WINDOW_WIDTH - 100)
    object_type = random.choices(['fruit', 'bomb', 'ice'], weights=[0.7, 0.2, 0.1])[0]
    return GameObject(x, WINDOW_HEIGHT, object_type)

def main():
    global score, strikes, game_over, combo_timer, combo_count, frozen_time
    clock = pygame.time.Clock()
    objects = []
    last_spawn = 0
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                pos = pygame.mouse.get_pos()
                sliced_objects = []
                for obj in objects:
                    if not obj.sliced and obj.is_clicked(pos):
                        obj.sliced = True
                        sliced_objects.append(obj)
                
                # Gestion du combo
                if len(sliced_objects) > 1:
                    score += len(sliced_objects) + 1  # Bonus pour le combo
                    combo_count = len(sliced_objects)
                    combo_timer = current_time
                else:
                    for obj in sliced_objects:
                        if obj.object_type == 'fruit':
                            score += 1
                        elif obj.object_type == 'bomb':
                            game_over = True
                        elif obj.object_type == 'ice':
                            frozen_time = current_time

        if not game_over and (current_time - frozen_time > 5000):  # Si pas gelé
            # Spawn de nouveaux objets
            if current_time - last_spawn > 2000:  # Toutes les 2 secondes
                objects.append(spawn_object())
                last_spawn = current_time

            # Mise à jour des objets
            for obj in objects[:]:
                obj.update()
                if obj.y > WINDOW_HEIGHT + 50:  # Objet sort de l'écran
                    if not obj.sliced and obj.object_type == 'fruit':
                        strikes += 1
                        if strikes >= 3:
                            game_over = True
                    objects.remove(obj)

        # Affichage
        screen.fill(BLACK)
        
        # Dessiner les objets
        for obj in objects:
            if not obj.sliced:
                color = RED if obj.object_type == 'bomb' else WHITE
                pygame.draw.circle(screen, color, (int(obj.x), int(obj.y)), 20)

        # Afficher le score et les strikes
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, WHITE)
        strikes_text = font.render(f'Strikes: {strikes}/3', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(strikes_text, (10, 50))

        if game_over:
            game_over_text = font.render('Game Over!', True, RED)
            screen.blit(game_over_text, (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
