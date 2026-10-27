"""
game.py - Administrador del bucle del juego, estados, colisiones y oleadas.
Coordina todas las entidades (jugador, enemigos, proyectiles, partículas, mejoras y sonidos).
"""

import random
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_WHITE, COLOR_GRAY,
    COLOR_CYAN, COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_PURPLE,
    POWERUP_TYPES
)
from player import Player
from enemy import Enemy
from powerup import PowerUp
from particles import ParticleSystem
from sounds import SoundManager


class Game:
    """Clase principal que contiene el flujo de lógica y estados de la partida."""
    STATE_MENU = "MENU"
    STATE_PLAYING = "PLAYING"
    STATE_GAMEOVER = "GAMEOVER"

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.state = self.STATE_MENU
        
        # Fuentes tipográficas
        self.font_small = pygame.font.SysFont("Consolas, Courier, monospace", 16)
        self.font_mid = pygame.font.SysFont("Consolas, Courier, monospace", 22, bold=True)
        self.font_large = pygame.font.SysFont("Consolas, Courier, monospace", 42, bold=True)
        self.font_powerup = pygame.font.SysFont("Arial, sans-serif", 14, bold=True)
        
        self.sound = SoundManager()
        self.particles = ParticleSystem()
        
        self.score = 0
        self.high_score = 0
        self.wave = 1
        self.enemies_remaining_to_spawn = 0
        self.last_enemy_spawn = 0
        self.wave_announcement_until = 0
        
        # Listas de entidades activas
        self.player = None
        self.player_bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.powerups = []
        
        self.reset_game()

    def reset_game(self):
        """Reinicia los valores y prepara una nueva partida."""
        self.player = Player()
        self.player_bullets.clear()
        self.enemy_bullets.clear()
        self.enemies.clear()
        self.powerups.clear()
        self.score = 0
        self.wave = 1
        self._start_wave(1)

    def _start_wave(self, wave_num: int):
        """Inicia una nueva oleada de enemigos con dificultad progresiva."""
        self.wave = wave_num
        self.wave_announcement_until = pygame.time.get_ticks() + 2500
        
        # En la oleada 5 o múltiplos de 5, aparece un Jefe Titan
        if wave_num % 5 == 0:
            self.enemies_remaining_to_spawn = 0
            boss = Enemy(SCREEN_WIDTH // 2, -100, enemy_type='boss')
            self.enemies.append(boss)
        else:
            self.enemies_remaining_to_spawn = 8 + wave_num * 4

    def handle_event(self, event: pygame.event.Event):
        """Maneja los eventos de teclado e interacción según el estado."""
        if event.type == pygame.KEYDOWN:
            if self.state == self.STATE_MENU:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.state = self.STATE_PLAYING
                    self.reset_game()
            elif self.state == self.STATE_GAMEOVER:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.state = self.STATE_PLAYING
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = self.STATE_MENU

    def update(self):
        """Actualiza la física, las colisiones y las entidades."""
        # Las estrellas del fondo se actualizan en cualquier pantalla
        self.particles.update()

        if self.state != self.STATE_PLAYING:
            return

        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        # 1. Actualizar jugador y disparos del jugador
        self.player.update(keys, self.particles)
        if keys[pygame.K_SPACE]:
            new_bullets = self.player.shoot()
            if new_bullets:
                self.player_bullets.extend(new_bullets)
                self.sound.play('laser')

        # 2. Generar enemigos periódicamente durante la oleada
        spawn_delay = max(400, 1600 - (self.wave * 120))
        if self.enemies_remaining_to_spawn > 0 and now - self.last_enemy_spawn >= spawn_delay:
            self.last_enemy_spawn = now
            self.enemies_remaining_to_spawn -= 1
            
            # Selección de tipo de enemigo según avance
            types = ['scout']
            if self.wave >= 2:
                types.append('fighter')
            if self.wave >= 3:
                types.append('cruiser')
            chosen_type = random.choice(types)
            spawn_x = random.randint(50, SCREEN_WIDTH - 50)
            self.enemies.append(Enemy(spawn_x, -40, chosen_type))

        # 3. Comprobar si la oleada ha sido eliminada
        if self.enemies_remaining_to_spawn == 0 and len(self.enemies) == 0:
            self._start_wave(self.wave + 1)

        # 4. Actualizar proyectiles del jugador
        self.player_bullets = [b for b in self.player_bullets if b.update()]

        # 5. Actualizar enemigos y sus disparos
        for enemy in self.enemies:
            fired = enemy.update(self.player.x)
            if fired:
                self.enemy_bullets.extend(fired)
        self.enemies = [e for e in self.enemies if not e.is_out_of_bounds()]

        # 6. Actualizar proyectiles enemigos
        self.enemy_bullets = [b for b in self.enemy_bullets if b.update()]

        # 7. Actualizar potenciadores
        self.powerups = [p for p in self.powerups if p.update()]

        # 8. Comprobar colisiones
        self._handle_collisions()

        # 9. Verificar fin de la partida
        if self.player.lives <= 0:
            self.state = self.STATE_GAMEOVER
            if self.score > self.high_score:
                self.high_score = self.score
            self.sound.play('game_over')

    def _handle_collisions(self):
        """Detección y resolución de impactos entre todas las entidades."""
        # A) Balas del jugador vs Enemigos
        for bullet in list(self.player_bullets):
            for enemy in list(self.enemies):
                if bullet.rect.colliderect(enemy.rect):
                    if bullet in self.player_bullets:
                        self.player_bullets.remove(bullet)
                    
                    self.particles.add_spark(bullet.x, bullet.y, COLOR_WHITE, count=4)
                    is_destroyed = enemy.take_damage(bullet.damage)
                    self.sound.play('hit')

                    if is_destroyed:
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                        self.score += enemy.score_value
                        self.sound.play('explosion')
                        self.particles.add_explosion(enemy.rect.centerx, enemy.rect.centery, count=28)
                        
                        # Probabilidad de soltar Power-up (22%)
                        if random.random() < 0.22:
                            p_type = random.choice(list(POWERUP_TYPES.keys()))
                            self.powerups.append(PowerUp(enemy.rect.centerx, enemy.rect.centery, p_type))
                    break

        # B) Balas enemigas vs Jugador
        for bullet in list(self.enemy_bullets):
            if bullet.rect.colliderect(self.player.rect):
                self.enemy_bullets.remove(bullet)
                self.particles.add_spark(bullet.x, bullet.y, COLOR_RED, count=6)
                lost_life = self.player.take_damage(bullet.damage)
                self.sound.play('hit')
                if lost_life:
                    self.particles.add_explosion(self.player.x, self.player.y, count=35, speed_mult=1.5)
                    self.sound.play('explosion')

        # C) Naves enemigas vs Jugador (Choque frontal)
        for enemy in list(self.enemies):
            if enemy.rect.colliderect(self.player.rect):
                lost_life = self.player.take_damage(40)
                self.particles.add_explosion(enemy.rect.centerx, enemy.rect.centery, count=20)
                self.sound.play('explosion')
                if lost_life:
                    self.particles.add_explosion(self.player.x, self.player.y, count=35, speed_mult=1.5)
                # El enemigo menor es destruido en la colisión
                if enemy.type != 'boss':
                    self.enemies.remove(enemy)

        # D) Jugador vs Potenciadores
        for powerup in list(self.powerups):
            if powerup.rect.colliderect(self.player.rect):
                self.player.apply_powerup(powerup.type)
                self.sound.play('powerup')
                self.particles.add_spark(powerup.x, powerup.y, powerup.info['color'], count=12)
                self.powerups.remove(powerup)

    def draw(self):
        """Renderiza la escena completa según el estado actual."""
        self.screen.fill(COLOR_BG)
        self.particles.draw_background(self.screen)

        if self.state == self.STATE_MENU:
            self._draw_menu()
        elif self.state == self.STATE_PLAYING:
            self._draw_gameplay()
        elif self.state == self.STATE_GAMEOVER:
            self._draw_gameover()

    def _draw_gameplay(self):
        """Renderiza las entidades y la interfaz de usuario en partida."""
        # Dibujar entidades
        for powerup in self.powerups:
            powerup.draw(self.screen, self.font_powerup)

        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)

        for bullet in self.player_bullets:
            bullet.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        self.player.draw(self.screen)
        self.particles.draw_particles(self.screen)

        # Anuncio de Oleada al inicio
        now = pygame.time.get_ticks()
        if now < self.wave_announcement_until:
            label = "¡OLEADA FINAL - JEFE TITÁN!" if self.wave % 5 == 0 else f"--- OLEADA {self.wave} ---"
            color = COLOR_YELLOW if self.wave % 5 == 0 else COLOR_CYAN
            wave_surf = self.font_large.render(label, True, color)
            self.screen.blit(wave_surf, wave_surf.get_rect(center=(SCREEN_WIDTH // 2, 220)))

        # Dibujar HUD (Interfaz Superior)
        self._draw_hud()

    def _draw_hud(self):
        """Dibuja barras de vida, puntuación, número de vidas y mejoras activas."""
        # Panel translúcido superior
        hud_bar = pygame.Surface((SCREEN_WIDTH, 48), pygame.SRCALPHA)
        hud_bar.fill((15, 15, 30, 200))
        self.screen.blit(hud_bar, (0, 0))
        pygame.draw.line(self.screen, (40, 40, 70), (0, 48), (SCREEN_WIDTH, 48), 1)

        # Puntuación
        score_surf = self.font_mid.render(f"PUNTOS: {self.score:06d}", True, COLOR_WHITE)
        self.screen.blit(score_surf, (20, 12))

        # Oleada
        wave_surf = self.font_mid.render(f"OLEADA: {self.wave}", True, COLOR_CYAN)
        self.screen.blit(wave_surf, (SCREEN_WIDTH // 2 - wave_surf.get_width() // 2, 12))

        # Barra de Vida (HP)
        hp_x = SCREEN_WIDTH - 220
        hp_y = 16
        bar_w = 120
        bar_h = 16
        pct = max(0, self.player.hp / self.player.max_hp)
        hp_color = COLOR_GREEN if pct > 0.5 else (COLOR_YELLOW if pct > 0.25 else COLOR_RED)
        
        pygame.draw.rect(self.screen, (50, 50, 60), (hp_x, hp_y, bar_w, bar_h), border_radius=4)
        pygame.draw.rect(self.screen, hp_color, (hp_x, hp_y, int(bar_w * pct), bar_h), border_radius=4)
        pygame.draw.rect(self.screen, COLOR_WHITE, (hp_x, hp_y, bar_w, bar_h), width=1, border_radius=4)
        
        hp_label = self.font_small.render("HP", True, COLOR_WHITE)
        self.screen.blit(hp_label, (hp_x - 30, hp_y))

        # Vidas restantes (íconos pequeños)
        for i in range(self.player.lives):
            lx = SCREEN_WIDTH - 50 + (i * 14)
            ly = hp_y + 8
            pts = [(lx, ly - 7), (lx - 5, ly + 7), (lx + 5, ly + 7)]
            pygame.draw.polygon(self.screen, COLOR_CYAN, pts)

        # Indicadores de mejoras activas en la esquina inferior izquierda
        now = pygame.time.get_ticks()
        active_y = SCREEN_HEIGHT - 35
        for p_name, duration_end in self.player.powerups.items():
            if now < duration_end:
                remaining_sec = max(0, (duration_end - now) // 1000)
                cfg = POWERUP_TYPES.get(p_name, {})
                color = cfg.get('color', COLOR_WHITE)
                p_text = f"[{p_name[:3]}: {remaining_sec}s]"
                surf = self.font_small.render(p_text, True, color)
                self.screen.blit(surf, (20, active_y))
                active_y -= 22

    def _draw_menu(self):
        """Dibuja el menú principal de inicio con instrucciones y controles."""
        title_surf = self.font_large.render("GALAXY STRIKER", True, COLOR_CYAN)
        sub_surf = self.font_mid.render("Retro Space Shooter en Pygame", True, COLOR_WHITE)
        prompt_surf = self.font_mid.render("[ Presiona ESPACIO o ENTER para jugar ]", True, COLOR_YELLOW)
        
        self.screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 170)))
        self.screen.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 220)))
        
        # Panel con instrucciones de control
        panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 220, 270, 440, 240)
        pygame.draw.rect(self.screen, (20, 20, 40), panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_CYAN, panel_rect, width=2, border_radius=10)

        lines = [
            ("CONTROLES", COLOR_YELLOW),
            ("Flechas o W / A / S / D : Mover la nave", COLOR_WHITE),
            ("Barra Espaciadora : Disparar láser", COLOR_WHITE),
            ("", COLOR_WHITE),
            ("MEJORAS (POWER-UPS)", COLOR_YELLOW),
            ("[+] Salud    [R] Fuego Rápido", COLOR_GREEN),
            ("[3] Disparo Triple    [S] Escudo", COLOR_PURPLE)
        ]
        
        for i, (text, col) in enumerate(lines):
            line_surf = self.font_small.render(text, True, col)
            self.screen.blit(line_surf, (panel_rect.x + 30, panel_rect.y + 20 + i * 26))

        # Parpadeo del botón de inicio
        if (pygame.time.get_ticks() // 400) % 2 == 0:
            self.screen.blit(prompt_surf, prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, 560)))

    def _draw_gameover(self):
        """Pantalla de Game Over con resumen de puntuación."""
        go_surf = self.font_large.render("FIN DEL JUEGO", True, COLOR_RED)
        score_surf = self.font_mid.render(f"Puntuación Obtenida: {self.score}", True, COLOR_WHITE)
        high_surf = self.font_mid.render(f"Récord Actual: {self.high_score}", True, COLOR_YELLOW)
        wave_surf = self.font_small.render(f"Alcanzaste la Oleada {self.wave}", True, COLOR_CYAN)
        prompt_surf = self.font_mid.render("Presiona ESPACIO para reiniciar o ESC para volver", True, COLOR_GREEN)

        self.screen.blit(go_surf, go_surf.get_rect(center=(SCREEN_WIDTH // 2, 200)))
        self.screen.blit(score_surf, score_surf.get_rect(center=(SCREEN_WIDTH // 2, 280)))
        self.screen.blit(high_surf, high_surf.get_rect(center=(SCREEN_WIDTH // 2, 320)))
        self.screen.blit(wave_surf, wave_surf.get_rect(center=(SCREEN_WIDTH // 2, 360)))

        if (pygame.time.get_ticks() // 400) % 2 == 0:
            self.screen.blit(prompt_surf, prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, 460)))
