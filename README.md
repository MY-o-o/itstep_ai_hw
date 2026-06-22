# Neon Snake

A self-contained Snake game built with HTML5 Canvas and vanilla JavaScript. No build step or dependencies — open and play.

## Quick start

Open `snake.html` in any modern browser:

```bash
# Windows
start snake.html

# macOS
open snake.html

# Linux
xdg-open snake.html
```

## Controls

| Input | Action |
|-------|--------|
| Arrow keys / W A S D | Move |
| Swipe (mobile) | Change direction |
| P or ⏸ button | Pause / resume |

You cannot reverse direction instantly (e.g. right → left).

## Features

- Grid-based movement with growing snake and increasing speed
- Score tracking and high score saved in `localStorage`
- Start, pause, and game-over screens
- Responsive canvas for desktop and mobile
- Particle effects, glowing food, and synthesized sound effects

## Tech

- Single HTML file (`snake.html`) with embedded CSS and JavaScript
- Game loop via `requestAnimationFrame` with frame-rate-independent timing
- Web Audio API for eat and game-over sounds (no external audio files)
