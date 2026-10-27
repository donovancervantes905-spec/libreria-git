"""
config.py - Configuraciones globales y constantes del videojuego Space Shooter.
Define las dimensiones de la pantalla, la tasa de refresco (FPS), la paleta de colores
y los parámetros de balance del juego.
"""

# Configuración de Ventana
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
FPS = 60
TITLE = "Galaxy Striker - Retro Space Shooter"

# Paleta de Colores (RGB)
COLOR_BG = (10, 10, 24)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (120, 120, 140)
COLOR_CYAN = (0, 240, 255)
COLOR_RED = (255, 60, 80)
COLOR_GREEN = (60, 255, 120)
COLOR_YELLOW = (255, 220, 40)
COLOR_ORANGE = (255, 140, 30)
COLOR_PURPLE = (180, 70, 255)
COLOR_SHIELD = (80, 180, 255, 120)

# Parámetros del Jugador
PLAYER_SPEED = 6
PLAYER_MAX_HEALTH = 100
PLAYER_START_LIVES = 3
PLAYER_FIRE_COOLDOWN = 180  # milisegundos entre disparos base

# Parámetros de Disparos
BULLET_SPEED = 10
ENEMY_BULLET_SPEED = 5

# Parámetros de Power-ups
POWERUP_SPEED = 2.5
POWERUP_DURATION = 8000  # 8 segundos de duración para buffs temporales
POWERUP_TYPES = {
    'HEALTH': {'color': COLOR_GREEN, 'symbol': '+'},
    'RAPID_FIRE': {'color': COLOR_YELLOW, 'symbol': 'R'},
    'TRIPLE_SHOT': {'color': COLOR_CYAN, 'symbol': '3'},
    'SHIELD': {'color': COLOR_PURPLE, 'symbol': 'S'}
}

# Tipos de Enemigos y sus características
ENEMY_CONFIGS = {
    'scout': {
        'hp': 20,
        'speed': 3.5,
        'score': 100,
        'color': COLOR_RED,
        'size': (28, 28),
        'shoot_interval': 2200
    },
    'fighter': {
        'hp': 40,
        'speed': 2.2,
        'score': 200,
        'color': COLOR_ORANGE,
        'size': (36, 36),
        'shoot_interval': 1600
    },
    'cruiser': {
        'hp': 90,
        'speed': 1.2,
        'score': 450,
        'color': COLOR_PURPLE,
        'size': (50, 45),
        'shoot_interval': 1200
    },
    'boss': {
        'hp': 600,
        'speed': 1.5,
        'score': 2500,
        'color': (255, 40, 140),
        'size': (120, 80),
        'shoot_interval': 800
    }
}
