"""
player.py - Nave del jugador, control de movimiento, sistema de disparo y estados de mejora.
Gestiona vidas, puntos de vida (HP), escudo de energía, invulnerabilidad y propulsores.
"""

import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SPEED, PLAYER_MAX_HEALTH,
    PLAYER_START_LIVES, PLAYER_FIRE_COOLDOWN, COLOR_CYAN, COLOR_WHITE,
    COLOR_YELLOW, COLOR_PURPLE, POWERUP_DURATION
)
from bullet import Bullet


class Player:
    """Representa la nave controlada por el usuario."""
    def __init__(self):
        self.width = 44
        self.height = 48
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 90
        self.rect = pygame.Rect(int(self.x - self.width / 2), int(self.y - self.height / 2), self.width, self.height)
        
        self.speed = PLAYER_SPEED
        self.max_hp = PLAYER_MAX_HEALTH
        self.hp = self.max_hp
        self.lives = PLAYER_START_LIVES
        
        self.last_shot_time = 0
        self.fire_cooldown = PLAYER_FIRE_COOLDOWN
        
        # Efectos y Power-ups activos
        self.powerups = {
            'RAPID_FIRE': 0,
            'TRIPLE_SHOT': 0,
            'SHIELD': 0
        }
        
        # Invulnerabilidad tras recibir impacto o renacer
        self.invulnerable_until = 0

    def apply_powerup(self, p_type: str):
        """Activa una mejora o restaura vida según el tipo recogido."""
        now = pygame.time.get_ticks()
        if p_type == 'HEALTH':
            self.hp = min(self.max_hp, self.hp + 35)
        elif p_type in self.powerups:
            self.powerups[p_type] = now + POWERUP_DURATION

    def is_powerup_active(self, p_type: str) -> bool:
        """Comprueba si un power-up temporal sigue vigente."""
        return pygame.time.get_ticks() < self.powerups.get(p_type, 0)

    def is_invulnerable(self) -> bool:
        """Determina si la nave está en periodo de gracia invulnerable."""
        return pygame.time.get_ticks() < self.invulnerable_until

    def take_damage(self, amount: int) -> bool:
        """
        Aplica daño al jugador considerando el escudo y la invulnerabilidad.
        Retorna True si el jugador pierde una vida.
        """
        if self.is_invulnerable():
            return False

        # Si el escudo de energía está activo, absorbe el impacto y se extingue
        if self.is_powerup_active('SHIELD'):
            self.powerups['SHIELD'] = 0
            self.invulnerable_until = pygame.time.get_ticks() + 1000
            return False

        self.hp -= amount
        if self.hp <= 0:
            self.lives -= 1
            self.hp = self.max_hp
            self.x = SCREEN_WIDTH // 2
            self.y = SCREEN_HEIGHT - 90
            self.invulnerable_until = pygame.time.get_ticks() + 2500  # 2.5 seg invulnerable
            return True
        else:
            self.invulnerable_until = pygame.time.get_ticks() + 800  # parpadeo breve
            return False

    def shoot(self) -> list:
        """Dispara proyectiles según los potenciadores activos."""
        now = pygame.time.get_ticks()
        current_cooldown = self.fire_cooldown // 2 if self.is_powerup_active('RAPID_FIRE') else self.fire_cooldown

        if now - self.last_shot_time < current_cooldown:
            return []

        self.last_shot_time = now
        bullets = []

        if self.is_powerup_active('TRIPLE_SHOT'):
            # Disparo en abanico de tres rayos
            bullets.append(Bullet(self.rect.centerx, self.rect.top, 0, -11, is_player=True))
            bullets.append(Bullet(self.rect.left + 4, self.rect.top + 6, -2.5, -10, is_player=True))
            bullets.append(Bullet(self.rect.right - 4, self.rect.top + 6, 2.5, -10, is_player=True))
        else:
            # Disparo dual estándar frontal
            bullets.append(Bullet(self.rect.left + 8, self.rect.top, 0, -11, is_player=True))
            bullets.append(Bullet(self.rect.right - 8, self.rect.top, 0, -11, is_player=True))

        return bullets

    def update(self, keys, particle_system=None):
        """Actualiza la posición del jugador en base a las teclas presionadas."""
        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed

        self.x += dx
        self.y += dy

        # Delimitar al área jugable visible
        self.x = max(self.width // 2, min(SCREEN_WIDTH - self.width // 2, self.x))
        self.y = max(self.height // 2, min(SCREEN_HEIGHT - self.height // 2, self.y))

        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

        # Generar partículas de fuego/propulsión
        if particle_system:
            particle_system.add_spark(self.rect.centerx - 8, self.rect.bottom - 4, COLOR_CYAN, count=1)
            particle_system.add_spark(self.rect.centerx + 8, self.rect.bottom - 4, COLOR_CYAN, count=1)

    def draw(self, surface: pygame.Surface):
        """Renderiza la nave del jugador con detalles aerodinámicos y efectos visuales."""
        # Parpadeo cuando es invulnerable
        if self.is_invulnerable() and (pygame.time.get_ticks() // 100) % 2 == 0:
            return

        cx, cy = self.rect.centerx, self.rect.centery
        w, h = self.width, self.height

        # Polígono estilizado de la nave aliada
        hull_pts = [
            (cx, cy - h // 2),                  # Punta delantera
            (cx + w // 6, cy - h // 6),
            (cx + w // 2, cy + h // 3),         # Punta ala derecha
            (cx + w // 3, cy + h // 2),         # Alerón derecho
            (cx + w // 6, cy + h // 3),         # Motor derecho
            (cx, cy + h // 4),                  # Centro trasero
            (cx - w // 6, cy + h // 3),         # Motor izquierdo
            (cx - w // 3, cy + h // 2),         # Alerón izquierdo
            (cx - w // 2, cy + h // 3),         # Punta ala izquierda
            (cx - w // 6, cy - h // 6)
        ]

        pygame.draw.polygon(surface, (40, 50, 75), hull_pts)
        pygame.draw.polygon(surface, COLOR_CYAN, hull_pts, width=2)

        # Cabina de mando (Cockpit resplandeciente)
        cockpit_rect = pygame.Rect(cx - 4, cy - h // 4, 8, 14)
        pygame.draw.ellipse(surface, COLOR_WHITE, cockpit_rect)

        # Efecto visual de Escudo de Energía
        if self.is_powerup_active('SHIELD'):
            shield_surf = pygame.Surface((w + 30, h + 30), pygame.SRCALPHA)
            pygame.draw.ellipse(
                shield_surf,
                (140, 70, 255, 110),
                (0, 0, w + 30, h + 30)
            )
            pygame.draw.ellipse(
                shield_surf,
                COLOR_PURPLE,
                (0, 0, w + 30, h + 30),
                width=2
            )
            surface.blit(shield_surf, (cx - (w + 30) // 2, cy - (h + 30) // 2))
