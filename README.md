# 🚀 Galaxy Striker - Retro Space Shooter en Python (Pygame)

Un videojuego clásico de disparos espacial en 2D (*Shoot 'em up*) con gráficos vectoriales procedurales, efectos de partículas, sistema de oleadas, jefes finales (*Boss*), potenciadores (*Power-ups*) y efectos de sonido generados por síntesis procedural sin depender de archivos de audio externos.

---

## 📁 Estructura del Proyecto y Explicación por Archivo

El proyecto está diseñado bajo una arquitectura limpia y modularizada para facilitar su lectura, mantenimiento y extensión:

```
space_shooter/
│
├── index.html           # Versión Web jugable directamente en navegador / GitHub Pages
├── main.py              # Punto de entrada (compatible con escritorio y Pygbag/WASM)
├── config.py            # Constantes, configuraciones y balance del juego
├── game.py              # Máquina de estados, oleadas, HUD y colisiones
├── player.py            # Nave del jugador, movimiento, vidas y escudos
├── enemy.py             # Inteligencia artificial de enemigos y Jefe Titán
├── bullet.py            # Proyectiles láser y detección de impactos
├── powerup.py           # Potenciadores y cápsulas recolectables
├── particles.py         # Fondo de estrellas (paralaje) y explosiones
├── sounds.py            # Síntesis procedural de efectos de sonido
├── requirements.txt     # Dependencias del proyecto (pygame)
├── .github/workflows/
│   └── deploy.yml       # Automatización para compilar y desplegar en GitHub Pages
└── README.md            # Documentación completa del proyecto
```

---

### 🔍 ¿Qué incluye y qué hace cada archivo de código?

### 1. `main.py`
- **Función:** Es el punto de inicio (*entry point*) de la aplicación.
- **Qué hace:**
  - Inicializa los subsistemas de Pygame con `pygame.init()`.
  - Configura la ventana principal a $800 \times 700$ píxeles y define el título de la ventana.
  - Inicia el reloj de refresco (`pygame.time.Clock`) fijado a 60 FPS estables.
  - Ejecuta el bucle de eventos (`while running`), delegando eventos a la clase `Game`.
  - Finaliza la ejecución de forma limpia al presionar la cruz de cerrar ventana (`pygame.QUIT`).

### 2. `config.py`
- **Función:** Archivo de configuración centralizada y parámetros globales.
- **Qué hace:**
  - Define las dimensiones de la pantalla (`SCREEN_WIDTH`, `SCREEN_HEIGHT`) y los FPS.
  - Contiene la paleta cromática en formato RGB (`COLOR_CYAN`, `COLOR_RED`, `COLOR_PURPLE`, etc.).
  - Configura las estadísticas del jugador (velocidad: 6 px/frame, vida máxima: 100 HP, vidas iniciales: 3, cadencia de tiro: 180 ms).
  - Almacena el diccionario `ENEMY_CONFIGS` con la vida, velocidad, puntuación y cadencia de cada tipo de enemigo (*Scout*, *Fighter*, *Cruiser* y *Boss*).
  - Configura los datos de los power-ups y su duración temporal (8 segundos).

### 3. `game.py`
- **Función:** Administrador global del flujo y la jugabilidad del videojuego.
- **Qué hace:**
  - Implementa la máquina de estados con 3 fases: `MENU` (inicio), `PLAYING` (en juego) y `GAMEOVER` (pantalla final con récord).
  - Gestiona el **Sistema de Oleadas Progresivas**: en cada oleada aumenta la cantidad de enemigos y su variedad. En la oleada 5 y sus múltiplos, invoca un **Jefe Titán**.
  - Administra el **Sistema de Colisiones**:
    - *Balas del jugador vs Enemigos*: resta salud, genera chispas y calcula la probabilidad (22%) de soltar un power-up al ser destruidos.
    - *Balas enemigas vs Jugador*: resta puntos de vida (HP) o destruye el escudo si está activo.
    - *Choques directos*: daño por embestida.
    - *Jugador vs Power-ups*: activa mejoras y reproduce el sonido correspondiente.
  - Dibuja el **HUD (Interfaz de Usuario)** superior: barra de salud con gradiente de color, contador de puntos, oleada actual, íconos de vidas restantes y cronómetros de mejoras activas.

### 4. `player.py`
- **Función:** Modela la nave controlada por el usuario.
- **Qué hace:**
  - Procesa las entradas del teclado tanto con flechas de dirección como con las teclas `W`, `A`, `S`, `D`.
  - Restringe la posición de la nave para que nunca abandone los límites de la pantalla.
  - Genera automáticamente partículas de propulsión en los motores izquierdo y derecho.
  - Controla la cadencia de tiro y la variación entre **Disparo Frontal Doble** o **Disparo Triple en Abanico** si la mejora está activa.
  - Gestiona el estado de **Invulnerabilidad Temporal** tras recibir daño o perder una vida, mostrando un parpadeo visual.
  - Renderiza el **Escudo de Energía** semitransparente con canal alfa cuando está activo.

### 5. `enemy.py`
- **Función:** Define los comportamientos, patrones de vuelo y ataques de los enemigos.
- **Qué hace:**
  - **Scout (Explorador):** Nave ágil y rápida con movimiento oscilatorio senoidal que dispara proyectiles rectos.
  - **Fighter (Caza Estelar):** Nave de combate que rastrea horizontalmente la posición del jugador y dispara lásers dobles.
  - **Cruiser (Crucero Pesado):** Nave acorazada de alto blindaje que dispara ráfagas triples en abanico.
  - **Boss (Jefe Titán):** Nave nodriza de gran tamaño con barra de vida dedicada, patrullaje horizontal y ráfaga cuádruple de alta energía.
  - Incluye efecto de *Hit Flash* (la nave parpadea en color blanco puro momentáneamente al ser impactada).

### 6. `bullet.py`
- **Función:** Modela todos los proyectiles láser en pantalla.
- **Qué hace:**
  - Calcula la trayectoria y el vector de velocidad $(v_x, v_y)$.
  - Renderiza proyectiles con **halo resplandeciente** exterior y un núcleo blanco de alta energía para simular lásers arcade.
  - Comprueba si el proyectil ha salido del marco de la pantalla para liberarlo de la memoria.

### 7. `powerup.py`
- **Función:** Cápsulas de mejora caídas por los enemigos al ser destruidos.
- **Qué hace:**
  - Desciende con un movimiento suave de flotación vertical y rotación armónica.
  - Dibuja una cápsula con halo pulsante e íconos identificativos:
    - **`[+]` Salud:** Restaura 35 puntos de vida (HP).
    - **`[R]` Fuego Rápido:** Reduce el tiempo entre disparos a la mitad.
    - **`[3]` Disparo Triple:** Permite disparar 3 rayos simultáneos en abanico.
    - **`[S]` Escudo de Energía:** Crea un campo de fuerza que absorbe el siguiente impacto letal.

### 8. `particles.py`
- **Función:** Motor de efectos visuales y ambientación espacial.
- **Qué hace:**
  - **Paralaje Estelar (`Star`):** Genera 90 estrellas en 3 capas de profundidad que se mueven a distintas velocidades y brillos para crear sensación de velocidad en el cosmos.
  - **Explosiones (`Particle`):** Emite nubes radiales de fragmentos incandescentes (amarillo, naranja, rojo, blanco) con decaimiento de tamaño y transparencia alfa gradual.
  - **Chispas:** Producidas en los motores de la nave y en los impactos de bala.

### 9. `sounds.py`
- **Función:** Generador de audio procedural retro sintetizado matemáticamente.
- **Qué hace:**
  - Utiliza funciones trigonométricas y modulación de frecuencias para construir las ondas sonoras en memoria (`bytearray`) y empaquetarlas en `pygame.mixer.Sound`.
  - Sonidos incluidos:
    - Disparo láser (barrido de 880 Hz a 220 Hz).
    - Explosiones e impactos (ruido blanco modulado y frecuencias graves).
    - Recogida de mejoras (arpegio brillante ascendente).
    - Game Over (cadencia descendente).
  - **A prueba de fallos:** Si la computadora no cuenta con dispositivo de audio o controladores disponibles, el juego silencia el audio automáticamente sin interrumpir la ejecución ni generar excepciones.

### 10. `requirements.txt`
- Lista de requisitos para instalar mediante `pip` (`pygame>=2.5.0`).

---

## 🎮 Controles del Videojuego

| Acción | Teclas |
| :--- | :--- |
| **Mover Nave** | `W`, `A`, `S`, `D` o Flechas de Dirección (`↑`, `←`, `↓`, `→`) |
| **Disparar Láser** | Barra Espaciadora (`ESPACIO`) |
| **Iniciar / Reiniciar Partida** | `ESPACIO` o `ENTER` |
| **Regresar al Menú** | `ESCAPE` (en pantalla de Game Over) |

---

## 🌐 Cómo Jugar en el Navegador Web (GitHub Pages)

El proyecto incluye dos métodos para jugarse en línea sin instalar nada en tu computadora:

### Método Instantáneo con GitHub Pages (Recomendado):
1. Sube los archivos a tu repositorio de GitHub.
2. En tu repositorio de GitHub, haz clic en **Settings** (Configuración) > **Pages** (en el menú lateral izquierdo).
3. En **Build and deployment** > **Source**, selecciona **Deploy from a branch**.
4. Elige la rama `main` (o `master`) y la carpeta `/ (root)`, luego pulsa **Save**.
5. En 1 minuto, GitHub te dará un enlace público:
   `https://<tu-usuario>.github.io/<tu-repositorio>/`
   *(¡Ábrelo en tu navegador y juega directamente con `index.html`!)*

### Método Local Inmediato:
- También puedes hacer **doble clic directamente en el archivo `index.html`** en tu computadora para abrirlo en Chrome, Edge o Firefox y jugar sin instalar Python.

---

## 🛠️ Instalación y Ejecución de la Versión Python (Escritorio)

### 1. Requisitos Previos
Tener instalado **Python 3.8 o superior** (descargable desde [python.org](https://www.python.org/downloads/)).

### 2. Clonar o acceder a la carpeta del proyecto
Abre una terminal o consola de comandos en el directorio del juego:
```bash
cd space_shooter
```

### 3. Instalar la librería Pygame
Ejecuta el siguiente comando para instalar Pygame:
```bash
pip install -r requirements.txt
```
*(O de manera directa: `pip install pygame`)*

### 4. Iniciar el juego
```bash
python main.py
```

---

## ⭐ Características Técnicas Destacadas
- **Cero dependencias de archivos externos:** No requiere descargar imágenes PNG ni archivos de audio WAV/MP3 externos; todos los gráficos son vectores generados por código y los sonidos son sintetizados en memoria.
- **Tasa fija de refresco a 60 FPS:** Movimiento suave y consistente de proyectiles y partículas.
- **Diseño orientado a objetos:** Código modular, estructurado, limpio y documentado con comentarios en español.
