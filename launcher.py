import pygame
import sys
import os

pygame.init()
WINDOW_SIZE = (1280, 920)  # Même taille que vos jeux
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Fruit Slicer - Menu Principal")

def main():
    running = True
    while running:
        screen.fill((0, 0, 0))
        
        # Deux gros boutons simples
        font = pygame.font.Font(None, 50)
        version1 = font.render("Fruit Slicer", True, (255, 255, 255))
        version2 = font.render("Fruit Slicer Arcade", True, (255, 255, 255))
        
        v1_rect = version1.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//3))
        v2_rect = version2.get_rect(center=(WINDOW_SIZE[0]//2, 2*WINDOW_SIZE[1]//3))
        
        # Crédits en bas à gauche (plus gros et rouge)
        credit_font = pygame.font.Font(None, 36)  # Taille augmentée de 24 à 36
        credits = credit_font.render("Présenté par Adam, Redha et Pierre", True, (255, 0, 0))  # Rouge pur
        credits_rect = credits.get_rect(bottomleft=(10, WINDOW_SIZE[1] - 10))
        
        screen.blit(version1, v1_rect)
        screen.blit(version2, v2_rect)
        screen.blit(credits, credits_rect)  # Afficher les crédits
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if v1_rect.collidepoint(event.pos):
                    os.system('python main1.py')  # Lance version classique
                elif v2_rect.collidepoint(event.pos):
                    os.system('python main4.py')  # Lance version avancée

if __name__ == "__main__":
    main() 