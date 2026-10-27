"""
bullet.py - Manejo de proyectiles del jugador y de los enemigos.
Contiene la física, el renderizado vectorial brillante y la detección de límites de pantalla.
"""

import math
import pygame
from config import SCREEN_HEIGHT, COLOR_CYAN, COLOR_RED, COLOR_YELLOW, COLOR_WHITE


class Bullet:
    """Clase base y funcional para proyectiles disparados."""
    def __init__(self, x: float, y: float, vx: float, vy: float, is_player: bool = True, damage: int = 25, color=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.is_player = is_player
        self.damage = damage
        self.width = 4 if not is_player else 5
        self.height = 14 if not is_player else 16
        
        if color:
            self.color = color
        else:
            self.color = COLOR_CYAN if is_player else COLOR_RED
            
        self.rect = pygame.Rect(int(self.x - self.width / 2), int(self.y - self.height / 2), self.width, self.height)

    def update(self) -> bool:
        """Actualiza la posición del proyectil. Retorna False si salió de pantalla."""
        self.x += self.vx
        self.y += self.vy
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

        # Destruir si sale de los límites de la pantalla
        if self.y < -30 or self.y > SCREEN_HEIGHT + 30:
            return False
        return True

    def draw(self, surface: pygame.Surface):
        """Dibuja el proyectil con un efecto de brillo o núcleo resplandeciente."""
        # Halo exterior brillante
        halo_rect = self.rect.inflate(4, 4)
        halo_surface = pygame.Surface((halo_rect.width, halo_rect.height), pygame.SRCALPHA)
        glow_color = (self.color[0], self.color[1], self.color[2], 90)
        pygame.draw.ellipse(halo_surface, glow_color, (0, 0, halo_rect.width, halo_rect.height))
        surface.blit(halo_surface, (halo_rect.x, halo_rect.y))

        # Núcleo del proyectil
        pygame.draw.rect(surface, self.color, self.rect, border_radius=3)
        # Centro blanco de alta energía
        core_rect = pygame.Rect(self.rect.centerx - 1, self.rect.y + 2, 2, self.rect.height - 4)
        pygame.draw.rect(surface, COLOR_WHITE, core_rect)
