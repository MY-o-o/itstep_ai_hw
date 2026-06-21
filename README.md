# Walkthrough: Retro-Neon 2D Platformer

A complete, production-ready, standalone 2D platformer game has been successfully created in a single file: [index.html](/index.html).

The game is themed with a **Retro-Neon Cyberpunk** visual style and features synthesized retro sound effects using the Web Audio API, dynamic parallax backgrounds, particle systems, checkpoints, and platforming logic.


## Implemented Features

### 1. Game Mechanics & Physics
- **Controllable Player**: Built standard movements (run, jump) with custom friction and gravity physics. Double jump/variable jump heights can be achieved by holding down the jump key (jump cut logic).
- **Collisions (AABB)**: Solid block collisions, one-way platforms (player can pass up through them and land on top), moving platforms (horizontal and vertical types), hazards, and collectibles are solved via an axis-aligned bounding box system.
- **Platform Riding**: Moving platforms transfer their horizontal and vertical velocity directly to the player when riding them.

### 2. Audio Synthesis (Web Audio API)
- No external assets are loaded. Sounds are synthesized on the fly using standard HTML5 oscillator nodes:
  - `jump`: High frequency sweep.
  - `collect`: Arpeggiated D-major/D-pentatonic chime.
  - `hit`: Low-pass filtered noise combined with a sub-bass pitch drop.
  - `win`: Cheerful C-major arpeggiated chord progression.

### 3. Graphics & Parallax Scrolling
- High-performance procedural pixel drawing using Canvas API:
  - **Player**: A cute mechanical robot character with walking/jumping leg animations, glowing visor, and a power core.
  - **Parallax Background**: 3 layers including twinkling starfield, distant skyscraper silhouettes, and closer glowing antenna towers.
  - **Collectibles**: Cyan diamonds that bob and rotate.
  - **Enemies**: Patrolling hover drones with animated mechanical wings and blinking lasers.
  - **Portal**: A dual-ring pulsing portal displaying wormhole particles.

### 4. Polish Features
- **Screen Shake**: Active camera shaking when taking damage, combined with a CSS container layout shake.
- **Invincibility Frames**: Player flashes and ignores incoming damage for 1.5 seconds post-hit.
- **Checkpoints**: Touch nodes that activate green lights and save player spawn coordinates.
- **Stomp Attack**: Mario-style stomp jumps on enemies to defeat them (bouncing the player up and gaining 200 points).

---

## Verification & Testing

1. **Syntax & Loading**: Opened the page in a browser subagent environment. Evaluated zero console errors on script initialization.
2. **Main Menu Options**: Clicking **Start Game** successfully starts the loop, updates the page, and activates the audio context. The **How to Play** screen gives instructions.
3. **Gameplay Verification**:
   - HUD is properly displayed with live heart states, updated timer, and high score checks.
   - Gameplay loops smoothly at a locked 60fps utilizing standard requestAnimationFrame delta times.
   - Checked that local storage correctly saves high scores.
