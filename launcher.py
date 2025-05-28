import pygame
import sys
import os
import subprocess
import math
import random

# Initialisation de Pygame
pygame.init()
pygame.mixer.init()

# Configuration de l'écran
WIDTH = 1280
HEIGHT = 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Slicer - Launcher")

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NEON_BLUE = (0, 195, 255)
NEON_PINK = (255, 0, 128)
NEON_GREEN = (0, 255, 128)
NEON_PURPLE = (128, 0, 255)

# Police
title_font = pygame.font.Font(None, 72)
menu_font = pygame.font.Font(None, 48)
credit_font = pygame.font.Font(None, 36)

# Classe pour les particules
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2, 4)
        self.color = random.choice([NEON_BLUE, NEON_PINK, NEON_GREEN, NEON_PURPLE])
        self.speed = random.uniform(1, 3)
        self.angle = random.uniform(0, 2 * math.pi)
        self.life = 255

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.life -= 5
        self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        if self.life > 0:
            alpha = min(255, self.life)
            color = (*self.color, alpha)
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size))

# Classe pour les boutons animés
class AnimatedButton:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.is_hovered = False
        self.animation_offset = 0
        self.glow_intensity = 0
        self.particles = []

    def draw(self, surface):
        # Effet de lueur
        glow_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
        glow_color = (*self.color, int(self.glow_intensity))
        pygame.draw.rect(glow_surface, glow_color, (10, 10, self.rect.width, self.rect.height), border_radius=10)
        surface.blit(glow_surface, (self.rect.x - 10, self.rect.y - 10))

        # Bouton principal
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)

        # Texte avec animation
        text_surface = menu_font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        text_rect.y += math.sin(self.animation_offset) * 2
        surface.blit(text_surface, text_rect)

        # Particules
        for particle in self.particles[:]:
            particle.update()
            particle.draw(surface)
            if particle.life <= 0:
                self.particles.remove(particle)

    def update(self):
        self.animation_offset += 0.1
        if self.is_hovered:
            self.glow_intensity = min(100, self.glow_intensity + 5)
            if random.random() < 0.1:
                self.particles.append(Particle(
                    random.randint(self.rect.left, self.rect.right),
                    random.randint(self.rect.top, self.rect.bottom)
                ))
        else:
            self.glow_intensity = max(0, self.glow_intensity - 5)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

# Création des boutons
classic_button = AnimatedButton(WIDTH//2 - 200, HEIGHT//2 - 100, 400, 80, "Fruit Slicer Classic", NEON_BLUE)
arcade_button = AnimatedButton(WIDTH//2 - 200, HEIGHT//2 + 20, 400, 80, "Fruit Slicer Arcade", NEON_PINK)
quit_button = AnimatedButton(WIDTH//2 - 200, HEIGHT//2 + 140, 400, 80, "Quitter", NEON_PURPLE)

# Particules de fond
background_particles = [Particle(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(50)]

# Boucle principale
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)
    
    # Mise à jour et affichage des particules de fond
    for particle in background_particles[:]:
        particle.update()
        particle.draw(screen)
        if particle.life <= 0:
            background_particles.remove(particle)
            background_particles.append(Particle(random.randint(0, WIDTH), random.randint(0, HEIGHT)))

    # Affichage du titre avec effet de lueur
    title = title_font.render("FRUIT SLICER", True, WHITE)
    title_rect = title.get_rect(center=(WIDTH//2, 100))
    
    # Effet de lueur pour le titre
    for offset in range(5, 0, -1):
        glow_color = (*NEON_BLUE, 50 - offset * 10)
        glow_surface = pygame.Surface((title_rect.width + offset * 4, title_rect.height + offset * 4), pygame.SRCALPHA)
        glow_title = title_font.render("FRUIT SLICER", True, glow_color)
        glow_rect = glow_title.get_rect(center=(glow_surface.get_width()//2, glow_surface.get_height()//2))
        glow_surface.blit(glow_title, glow_rect)
        screen.blit(glow_surface, (title_rect.x - offset * 2, title_rect.y - offset * 2))
    
    screen.blit(title, title_rect)

    # Mise à jour et affichage des boutons
    classic_button.update()
    arcade_button.update()
    quit_button.update()
    
    classic_button.draw(screen)
    arcade_button.draw(screen)
    quit_button.draw(screen)

    # Crédits
    credits = credit_font.render("Présenté par Adam, Redha et Pierre", True, NEON_GREEN)
    credits_rect = credits.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))
    screen.blit(credits, credits_rect)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if classic_button.handle_event(event):
            pygame.quit()
            subprocess.run([sys.executable, "main1.py"])
            pygame.init()
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            
        if arcade_button.handle_event(event):
            pygame.quit()
            subprocess.run([sys.executable, "main4.py"])
            pygame.init()
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            
        if quit_button.handle_event(event):
            running = False
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit() 