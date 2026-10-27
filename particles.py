"""
particles.py - Sistema de partículas y fondo estrellado con efecto de paralaje.
Gestiona las estrellas del espacio exterior, estelas de propulsión de las naves y
las explosiones generadas en impactos y destrucciones.
"""

import random
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_YELLOW, COLOR_ORANGE, COLOR_RED, COLOR_CYAN


class Star:
    """Representa una estrella individual para el fondo en capas (paralaje)."""
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.5, 2.5)
        self.size = 1 if self.speed < 1.2 else (2 if self.speed < 2.0 else 3)
        self.brightness = random.randint(140, 255)
        self.twinkle_speed = random.uniform(1.0, 3.0)

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
            self.brightness = random.randint(140, 255)

    def draw(self, surface: pygame.Surface):
        color = (self.brightness, self.brightness, self.brightness)
        if self.size == 1:
            surface.set_at((int(self.x), int(self.y)), color)
        else:
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


class Particle:
    """Partícula efímera para efectos de explosiones o estelas."""
    def __init__(self, x: float, y: float, vx: float, vy: float, color, size: float, life: int):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_life = life
        self.life = life

    def update(self) -> bool:
        """Actualiza la posición y decae la vida. Retorna False cuando expira."""
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= 1
        return self.life > 0

    def draw(self, surface: pygame.Surface):
        if self.life <= 0:
            return
        alpha = int((self.life / self.max_life) * 255)
        current_size = max(1.0, self.size * (self.life / self.max_life))
        
        # Superficie con canal alfa para dibujar la partícula con transparencia gradual
        surf = pygame.Surface((int(current_size * 2 + 2), int(current_size * 2 + 2)), pygame.SRCALPHA)
        c = (self.color[0], self.color[1], self.color[2], min(255, max(0, alpha)))
        pygame.draw.circle(surf, c, (surf.get_width() // 2, surf.get_height() // 2), int(current_size))
        surface.blit(surf, (self.x - surf.get_width() // 2, self.y - surf.get_height() // 2))


class ParticleSystem:
    """Administrador centralizado de estrellas y partículas."""
    def __init__(self, num_stars: int = 90):
        self.stars = [Star() for _ in range(num_stars)]
        self.particles = []

    def add_explosion(self, x: float, y: float, count: int = 24, colors=None, speed_mult: float = 1.0):
        """Genera una explosión radial de partículas."""
        if colors is None:
            colors = [COLOR_YELLOW, COLOR_ORANGE, COLOR_RED, COLOR_WHITE]

        for _ in range(count):
            angle = random.uniform(0, 6.28318)
            speed = random.uniform(1.5, 5.0) * speed_mult
            vx = speed * random.uniform(0.7, 1.3) * (1 if random.random() > 0.5 else -1)
            vy = speed * random.uniform(0.7, 1.3) * (1 if random.random() > 0.5 else -1)
            color = random.choice(colors)
            size = random.uniform(2.5, 5.5)
            life = random.randint(18, 38)
            self.particles.append(Particle(x, y, vx, vy, color, size, life))

    def add_spark(self, x: float, y: float, color=COLOR_CYAN, count: int = 6):
        """Genera chispas pequeñas para impactos o propulsores."""
        for _ in range(count):
            vx = random.uniform(-1.5, 1.5)
            vy = random.uniform(2.0, 5.0)
            size = random.uniform(1.5, 3.0)
            life = random.randint(8, 16)
            self.particles.append(Particle(x, y, vx, vy, color, size, life))

    def update(self):
        for star in self.stars:
            star.update()
        self.particles = [p for p in self.particles if p.update()]

    def draw_background(self, surface: pygame.Surface):
        for star in self.stars:
            star.draw(surface)

    def draw_particles(self, surface: pygame.Surface):
        for p in self.particles:
            p.draw(surface)
