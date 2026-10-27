"""
powerup.py - Objetos coleccionables y potenciadores caídos por enemigos derrotados.
Incluye curación, disparo triple, fuego rápido y escudo de energía temporal.
"""

import math
import pygame
from config import SCREEN_HEIGHT, POWERUP_SPEED, POWERUP_TYPES, COLOR_WHITE


class PowerUp:
    """Representa una cápsula de mejora que cae hacia la parte inferior."""
    def __init__(self, x: float, y: float, powerup_type: str):
        self.x = x
        self.y = y
        self.type = powerup_type
        self.info = POWERUP_TYPES.get(powerup_type, POWERUP_TYPES['HEALTH'])
        self.speed = POWERUP_SPEED
        self.size = 26
        self.rect = pygame.Rect(int(self.x - self.size // 2), int(self.y - self.size // 2), self.size, self.size)
        self.bob_angle = 0.0

    def update(self) -> bool:
        """Actualiza la posición del power-up. Retorna False si se sale de la pantalla."""
        self.y += self.speed
        self.bob_angle += 0.08
        self.rect.centery = int(self.y + math.sin(self.bob_angle) * 3)
        self.rect.centerx = int(self.x)

        if self.y > SCREEN_HEIGHT + 30:
            return False
        return True

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Renderiza una cápsula flotante con icono distintivo y brillo pulsante."""
        color = self.info['color']
        pulse = int(abs(math.sin(self.bob_angle)) * 6)
        
        # Halo exterior brillante
        halo_surf = pygame.Surface((self.size + 14 + pulse, self.size + 14 + pulse), pygame.SRCALPHA)
        pygame.draw.circle(
            halo_surf,
            (color[0], color[1], color[2], 75),
            (halo_surf.get_width() // 2, halo_surf.get_height() // 2),
            (self.size // 2) + 3 + pulse // 2
        )
        surface.blit(halo_surf, (self.rect.centerx - halo_surf.get_width() // 2, self.rect.centery - halo_surf.get_height() // 2))

        # Contenedor de la cápsula
        pygame.draw.circle(surface, (20, 20, 35), self.rect.center, self.size // 2)
        pygame.draw.circle(surface, color, self.rect.center, self.size // 2, width=2)

        # Letra o símbolo distintivo
        text_surf = font.render(self.info['symbol'], True, COLOR_WHITE)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))
