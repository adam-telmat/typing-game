# Import du code de main4
import main4
import pygame
import os

def start_game():
    # Initialisation
    clock = pygame.time.Clock()
    
    # Configuration initiale
    main4.setup_game()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Permettre de revenir au menu
                    running = False
            
            # Gérer les autres événements du jeu normalement
            if main4.game_state == main4.STATE_GAME:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        main4.shoot_weapon(main4.player)
        
        if not running:
            break
            
        # Logique du jeu principale
        if main4.game_state == main4.STATE_GAME:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                main4.player.move_left()
            if keys[pygame.K_RIGHT]:
                main4.player.move_right()
            
            # Mise à jour et affichage du jeu
            current_time = pygame.time.get_ticks()
            elapsed = current_time - main4.round_start_time
            time_remaining = max(0, (main4.ROUND_DURATION - elapsed) // 1000)
            
            if not main4.game_over:
                if current_time - main4.last_spawn_time > main4.difficulty_levels[main4.current_difficulty]["spawn_delay"]:
                    main4.spawn_object()
                    main4.last_spawn_time = current_time
                
                main4.move_objects()
                main4.move_weapons()
                main4.check_collisions(main4.player)
                main4.check_ship_collision(main4.player)
            
            # Affichage
            main4.screen.blit(main4.background_images[main4.current_difficulty], (0, 0))
            for obj in main4.objects:
                obj.draw()
            main4.player.draw()
            for w in main4.weapons:
                w.draw()
            main4.draw_score(time_remaining)
            
        pygame.display.flip()
        clock.tick(60)
    
    # Nettoyage avant de revenir au menu
    pygame.display.set_mode((800, 600))

if __name__ == "__main__":
    start_game() 