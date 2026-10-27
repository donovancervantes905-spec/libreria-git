"""
enemy.py - Clases y lógicas de comportamiento de los enemigos y el Jefe Final.
Incluye patrones de movimiento, disparo automático y renderizado vectorial de las naves.
"""

import math
import random
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, ENEMY_CONFIGS, COLOR_WHITE, COLOR_RED, COLOR_YELLOW
from bullet import Bullet


class Enemy:
    """Clase general para naves enemigas con diferentes tipos y patrones."""
    def __init__(self, x: float, y: float, enemy_type: str = 'scout'):
        self.type = enemy_type
        cfg = ENEMY_CONFIGS[enemy_type]
        self.x = x
        self.y = y
        self.max_hp = cfg['hp']
        self.hp = self.max_hp
        self.speed = cfg['speed']
        self.score_value = cfg['score']
        self.color = cfg['color']
        self.width, self.height = cfg['size']
        self.shoot_interval = cfg['shoot_interval']
        self.last_shot_time = pygame.time.get_ticks() + random.randint(0, 1000)
        
        self.rect = pygame.Rect(int(self.x - self.width / 2), int(self.y - self.height / 2), self.width, self.height)
        
        # Parámetros para trayectorias trigonométricas
        self.spawn_time = pygame.time.get_ticks()
        self.sine_frequency = random.uniform(0.003, 0.006)
        self.sine_amplitude = random.uniform(30, 80)
        self.base_x = x
        self.hit_flash = 0

    def take_damage(self, amount: int) -> bool:
        """Aplica daño a la nave enemiga. Retorna True si la nave es destruida."""
        self.hp -= amount
        self.hit_flash = 4  # cuadros de parpadeo blanco
        return self.hp <= 0

    def update(self, player_x: float = None) -> list:
        """Actualiza posición y genera disparos si corresponde. Retorna lista de balas."""
        elapsed = pygame.time.get_ticks() - self.spawn_time
        bullets = []

        if self.type == 'scout':
            # Movimiento serpenteante rápido
            self.y += self.speed
            self.x = self.base_x + math.sin(elapsed * self.sine_frequency) * self.sine_amplitude
        elif self.type == 'fighter':
            # Baja y se ajusta levemente en el eje X hacia el jugador
            self.y += self.speed
            if player_x is not None:
                if self.x < player_x:
                    self.x += min(1.2, player_x - self.x)
                elif self.x > player_x:
                    self.x -= min(1.2, self.x - player_x)
        elif self.type == 'cruiser':
            # Avance lento y constante
            self.y += self.speed
        elif self.type == 'boss':
            # El jefe baja hasta una posición superior y patrulla de lado a lado
            if self.y < 120:
                self.y += 1.5
            else:
                self.x += self.speed
                if self.x > SCREEN_WIDTH - 100 or self.x < 100:
                    self.speed = -self.speed

        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

        # Manejo de disparos automáticos
        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= self.shoot_interval and self.y > 0 and self.y < SCREEN_HEIGHT - 80:
            self.last_shot_time = now
            bullets.extend(self._create_bullets(player_x))

        if self.hit_flash > 0:
            self.hit_flash -= 1

        return bullets

    def _create_bullets(self, target_x: float = None) -> list:
        bullets = []
        if self.type == 'scout':
            bullets.append(Bullet(self.rect.centerx, self.rect.bottom, 0, 5, is_player=False))
        elif self.type == 'fighter':
            bullets.append(Bullet(self.rect.left + 5, self.rect.bottom, -0.6, 5.5, is_player=False))
            bullets.append(Bullet(self.rect.right - 5, self.rect.bottom, 0.6, 5.5, is_player=False))
        elif self.type == 'cruiser':
            bullets.append(Bullet(self.rect.centerx, self.rect.bottom, 0, 6, is_player=False, damage=30))
            bullets.append(Bullet(self.rect.left, self.rect.centery, -1.8, 5, is_player=False, damage=20))
            bullets.append(Bullet(self.rect.right, self.rect.centery, 1.8, 5, is_player=False, damage=20))
        elif self.type == 'boss':
            # Ráfaga cuádruple del Boss
            angles = [-2.5, -0.8, 0.8, 2.5]
            for vx in angles:
                bullets.append(Bullet(self.rect.centerx, self.rect.bottom - 10, vx, 6, is_player=False, damage=25, color=COLOR_YELLOW))
        return bullets

    def is_out_of_bounds(self) -> bool:
        """Determina si la nave enemiga salió de la pantalla por abajo."""
        return self.y > SCREEN_HEIGHT + 60

    def draw(self, surface: pygame.Surface):
        """Dibuja la silueta geométrica de la nave enemiga según su tipo."""
        color = COLOR_WHITE if self.hit_flash > 0 else self.color
        cx, cy = self.rect.centerx, self.rect.centery
        w, h = self.width, self.height

        if self.type == 'scout':
            # Forma de flecha afilada invertida
            pts = [(cx, cy + h // 2), (cx - w // 2, cy - h // 2), (cx, cy - h // 4), (cx + w // 2, cy - h // 2)]
            pygame.draw.polygon(surface, color, pts)
            pygame.draw.polygon(surface, COLOR_YELLOW, pts, width=1)
        elif self.type == 'fighter':
            # Forma de caza estelar con alas delta
            pts = [
                (cx, cy + h // 2),
                (cx - w // 2, cy + h // 4),
                (cx - w // 3, cy - h // 2),
                (cx, cy - h // 3),
                (cx + w // 3, cy - h // 2),
                (cx + w // 2, cy + h // 4)
            ]
            pygame.draw.polygon(surface, color, pts)
            pygame.draw.polygon(surface, COLOR_WHITE, pts, width=1)
        elif self.type == 'cruiser':
            # Nave acorazada hexagonal con núcleo
            pts = [
                (cx - w // 4, cy - h // 2),
                (cx + w // 4, cy - h // 2),
                (cx + w // 2, cy),
                (cx + w // 3, cy + h // 2),
                (cx - w // 3, cy + h // 2),
                (cx - w // 2, cy)
            ]
            pygame.draw.polygon(surface, color, pts)
            pygame.draw.circle(surface, COLOR_RED, (cx, cy), 8)
            pygame.draw.polygon(surface, COLOR_WHITE, pts, width=2)
        elif self.type == 'boss':
            # Nave nodriza / Titán imponente
            pts = [
                (cx, cy + h // 2),
                (cx - w // 2, cy),
                (cx - w // 3, cy - h // 2),
                (cx + w // 3, cy - h // 2),
                (cx + w // 2, cy)
            ]
            pygame.draw.polygon(surface, color, pts)
            pygame.draw.polygon(surface, COLOR_WHITE, pts, width=3)
            # Núcleo de energía del Boss
            pygame.draw.circle(surface, COLOR_YELLOW, (cx, cy), 16)
            pygame.draw.circle(surface, COLOR_RED, (cx, cy), 10)
            
            # Barra de vida encima del Boss
            bar_w = 140
            bar_h = 8
            bx = cx - bar_w // 2
            by = self.rect.top - 16
            pct = max(0, self.hp / self.max_hp)
            pygame.draw.rect(surface, (60, 20, 20), (bx, by, bar_w, bar_h))
            pygame.draw.rect(surface, COLOR_RED, (bx, by, int(bar_w * pct), bar_h))
            pygame.draw.rect(surface, COLOR_WHITE, (bx, by, bar_w, bar_h), width=1)
