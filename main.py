"""
main.py - Punto de entrada principal para ejecutar Galaxy Striker.
Inicializa el entorno de Pygame, la ventana principal, el reloj de cuadros
por segundo (FPS) y el ciclo principal de eventos del juego.
"""

import sys
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from game import Game


def main():
    # Inicialización de Pygame
    pygame.init()
    pygame.display.set_caption(TITLE)
    
    # Crear la superficie de ventana principal
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    
    # Instancia del administrador general del juego
    game = Game(screen)
    
    running = True
    while running:
        # 1. Manejo de eventos del sistema (teclado, cerrar ventana)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)
                
        # 2. Actualización de física y lógica de juego
        game.update()
        
        # 3. Renderizado gráfico de pantalla
        game.draw()
        
        # 4. Actualizar pantalla y mantener tasa fija de FPS
        pygame.display.flip()
        clock.tick(FPS)
        
    # Salida limpia del programa
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
