"""
sounds.py - Generador de efectos de sonido procedurales y retro.
Crea ondas sonoras en memoria sin requerir archivos de audio externos (.wav/.mp3),
con soporte de fallback seguro si el sistema de sonido del equipo no está disponible.
"""

import math
import struct
import pygame


class SoundManager:
    """Gestiona los sonidos del juego mediante síntesis de ondas o silenciamiento seguro."""
    def __init__(self):
        self.enabled = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.enabled = True
            self.sounds = {
                'laser': self._generate_laser_sound(),
                'explosion': self._generate_noise_sound(duration=0.35, freq_factor=0.6),
                'hit': self._generate_noise_sound(duration=0.08, freq_factor=1.2),
                'powerup': self._generate_chime_sound(),
                'game_over': self._generate_game_over_sound()
            }
        except Exception:
            # Si el hardware de audio no está disponible, el juego continuará sin sonido
            self.enabled = False
            self.sounds = {}

    def _generate_laser_sound(self) -> pygame.mixer.Sound:
        """Sintetiza un sonido de disparo láser de frecuencia descendente."""
        sample_rate = 22050
        duration = 0.12
        num_samples = int(sample_rate * duration)
        buf = bytearray()

        for i in range(num_samples):
            t = float(i) / sample_rate
            # Frecuencia cae de 880Hz a 220Hz
            freq = 880.0 - (660.0 * (i / num_samples))
            val = int(math.sin(2.0 * math.pi * freq * t) * 16000 * (1.0 - (i / num_samples)))
            buf.extend(struct.pack('<h', max(-32767, min(32767, val))))

        return pygame.mixer.Sound(buffer=bytes(buf))

    def _generate_noise_sound(self, duration: float = 0.25, freq_factor: float = 1.0) -> pygame.mixer.Sound:
        """Sintetiza un sonido de explosión o impacto mediante modulación rugosa."""
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        buf = bytearray()
        import random

        val = 0
        for i in range(num_samples):
            decay = (1.0 - (i / num_samples)) ** 2
            noise = random.uniform(-1.0, 1.0)
            low_freq = math.sin(2.0 * math.pi * 65.0 * freq_factor * (i / sample_rate))
            combined = (noise * 0.7 + low_freq * 0.3) * decay
            sample_val = int(combined * 20000)
            buf.extend(struct.pack('<h', max(-32767, min(32767, sample_val))))

        return pygame.mixer.Sound(buffer=bytes(buf))

    def _generate_chime_sound(self) -> pygame.mixer.Sound:
        """Sintetiza un arpegio ascendente brillante para recolectar mejoras."""
        sample_rate = 22050
        duration = 0.25
        num_samples = int(sample_rate * duration)
        buf = bytearray()

        for i in range(num_samples):
            t = float(i) / sample_rate
            phase = i / num_samples
            freq = 523.25 if phase < 0.33 else (659.25 if phase < 0.66 else 783.99)
            val = int(math.sin(2.0 * math.pi * freq * t) * 18000 * (1.0 - phase))
            buf.extend(struct.pack('<h', max(-32767, min(32767, val))))

        return pygame.mixer.Sound(buffer=bytes(buf))

    def _generate_game_over_sound(self) -> pygame.mixer.Sound:
        """Sintetiza una tonalidad triste y descendente para el Game Over."""
        sample_rate = 22050
        duration = 0.6
        num_samples = int(sample_rate * duration)
        buf = bytearray()

        for i in range(num_samples):
            t = float(i) / sample_rate
            phase = i / num_samples
            freq = 340.0 - (200.0 * phase)
            val = int(math.sin(2.0 * math.pi * freq * t) * 15000 * (1.0 - phase))
            buf.extend(struct.pack('<h', max(-32767, min(32767, val))))

        return pygame.mixer.Sound(buffer=bytes(buf))

    def play(self, sound_name: str):
        """Reproduce un efecto de sonido si el mixer está activo."""
        if not self.enabled:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            snd.play()
