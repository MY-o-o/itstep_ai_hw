import {
  Component,
  ElementRef,
  ViewChild,
  OnInit,
  OnDestroy,
  HostListener,
  signal,
  NgZone,
} from '@angular/core';

const CANVAS_W = 800;
const CANVAS_H = 500;
const PADDLE_W = 12;
const PADDLE_H = 90;
const BALL_SIZE = 12;
const PLAYER_X = 20;
const PC_X = CANVAS_W - PLAYER_X - PADDLE_W;
const PADDLE_SPEED = 6;
const BALL_INIT_SPEED = 5;
const BALL_MAX_SPEED = 14;
const PC_DIFFICULTY = 0.78; // 0-1: fraction of max tracking speed

interface GameState {
  playerY: number;
  pcY: number;
  ballX: number;
  ballY: number;
  ballVx: number;
  ballVy: number;
  playerScore: number;
  pcScore: number;
  phase: 'idle' | 'playing' | 'paused' | 'over';
  winner: 'player' | 'pc' | null;
}

@Component({
  selector: 'app-root',
  standalone: true,
  template: `
    <div class="game-wrapper">
      <h1 class="title">PONG</h1>

      <div class="scoreboard">
        <span class="score player-score">{{ state().playerScore }}</span>
        <span class="divider">:</span>
        <span class="score pc-score">{{ state().pcScore }}</span>
      </div>

      <div class="labels">
        <span>YOU</span>
        <span>PC</span>
      </div>

      <div class="canvas-container">
        <canvas #gameCanvas [width]="W" [height]="H"></canvas>

        @if (state().phase === 'idle') {
          <div class="overlay">
            <p>Use <kbd>W</kbd> / <kbd>S</kbd> or <kbd>↑</kbd> / <kbd>↓</kbd> to move</p>
            <button (click)="startGame()">START GAME</button>
          </div>
        }

        @if (state().phase === 'paused') {
          <div class="overlay">
            <p>PAUSED</p>
            <button (click)="resumeGame()">RESUME</button>
          </div>
        }

        @if (state().phase === 'over') {
          <div class="overlay">
            <p class="winner-text">
              {{ state().winner === 'player' ? 'YOU WIN!' : 'PC WINS!' }}
            </p>
            <button (click)="startGame()">PLAY AGAIN</button>
          </div>
        }
      </div>

      <div class="controls-hint">
        @if (state().phase === 'playing') {
          <span>Press <kbd>P</kbd> to pause</span>
        }
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      background: #0a0a0a;
    }

    .game-wrapper {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      user-select: none;
    }

    .title {
      color: #fff;
      font-family: 'Courier New', monospace;
      font-size: 2.5rem;
      letter-spacing: 0.4em;
      margin: 0 0 4px;
    }

    .scoreboard {
      display: flex;
      gap: 24px;
      align-items: center;
    }

    .score {
      font-family: 'Courier New', monospace;
      font-size: 3rem;
      font-weight: bold;
      color: #fff;
      min-width: 60px;
      text-align: center;
    }

    .divider {
      font-family: 'Courier New', monospace;
      font-size: 2.5rem;
      color: #555;
    }

    .labels {
      display: flex;
      width: 800px;
      justify-content: space-between;
      padding: 0 30px;
      box-sizing: border-box;
      color: #888;
      font-family: 'Courier New', monospace;
      font-size: 0.8rem;
      letter-spacing: 0.2em;
    }

    .canvas-container {
      position: relative;
    }

    canvas {
      display: block;
      background: #111;
      border: 2px solid #333;
    }

    .overlay {
      position: absolute;
      inset: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 20px;
      background: rgba(0, 0, 0, 0.75);
    }

    .overlay p {
      color: #fff;
      font-family: 'Courier New', monospace;
      font-size: 1.2rem;
      text-align: center;
      margin: 0;
    }

    .overlay kbd {
      background: #333;
      border: 1px solid #666;
      border-radius: 4px;
      padding: 2px 6px;
      font-size: 0.95em;
    }

    .winner-text {
      font-size: 2.5rem !important;
      font-weight: bold;
      color: #4cff91 !important;
    }

    button {
      background: transparent;
      border: 2px solid #fff;
      color: #fff;
      font-family: 'Courier New', monospace;
      font-size: 1rem;
      letter-spacing: 0.15em;
      padding: 10px 32px;
      cursor: pointer;
      transition: background 0.15s, color 0.15s;
    }

    button:hover {
      background: #fff;
      color: #000;
    }

    .controls-hint {
      height: 24px;
      color: #555;
      font-family: 'Courier New', monospace;
      font-size: 0.8rem;
    }

    .controls-hint kbd {
      background: #222;
      border: 1px solid #444;
      border-radius: 3px;
      padding: 1px 5px;
    }
  `],
})
export class App implements OnInit, OnDestroy {
  @ViewChild('gameCanvas', { static: true }) canvasRef!: ElementRef<HTMLCanvasElement>;

  readonly W = CANVAS_W;
  readonly H = CANVAS_H;

  state = signal<GameState>(this.initState());

  private ctx!: CanvasRenderingContext2D;
  private animId = 0;
  private keys = new Set<string>();
  private readonly WIN_SCORE = 7;

  constructor(private zone: NgZone) {}

  ngOnInit() {
    this.ctx = this.canvasRef.nativeElement.getContext('2d')!;
    this.render();
  }

  ngOnDestroy() {
    cancelAnimationFrame(this.animId);
  }

  @HostListener('window:keydown', ['$event'])
  onKeyDown(e: KeyboardEvent) {
    this.keys.add(e.key);
    if (e.key === 'p' || e.key === 'P') {
      if (this.state().phase === 'playing') this.pauseGame();
      else if (this.state().phase === 'paused') this.resumeGame();
    }
    // prevent arrow keys scrolling page
    if (['ArrowUp', 'ArrowDown'].includes(e.key)) e.preventDefault();
  }

  @HostListener('window:keyup', ['$event'])
  onKeyUp(e: KeyboardEvent) {
    this.keys.delete(e.key);
  }

  startGame() {
    this.state.set(this.initState());
    this.state.update(s => ({ ...s, phase: 'playing' }));
    cancelAnimationFrame(this.animId);
    this.zone.runOutsideAngular(() => this.loop());
  }

  pauseGame() {
    this.state.update(s => ({ ...s, phase: 'paused' }));
    cancelAnimationFrame(this.animId);
  }

  resumeGame() {
    this.state.update(s => ({ ...s, phase: 'playing' }));
    this.zone.runOutsideAngular(() => this.loop());
  }

  private initState(): GameState {
    return {
      playerY: (CANVAS_H - PADDLE_H) / 2,
      pcY: (CANVAS_H - PADDLE_H) / 2,
      ...this.resetBall(),
      playerScore: 0,
      pcScore: 0,
      phase: 'idle',
      winner: null,
    };
  }

  private resetBall() {
    const angle = (Math.random() * 60 - 30) * (Math.PI / 180);
    const dir = Math.random() < 0.5 ? 1 : -1;
    return {
      ballX: CANVAS_W / 2 - BALL_SIZE / 2,
      ballY: CANVAS_H / 2 - BALL_SIZE / 2,
      ballVx: Math.cos(angle) * BALL_INIT_SPEED * dir,
      ballVy: Math.sin(angle) * BALL_INIT_SPEED,
    };
  }

  private loop() {
    this.update();
    this.render();
    if (this.state().phase === 'playing') {
      this.animId = requestAnimationFrame(() => this.loop());
    }
  }

  private update() {
    const s = this.state();

    // Player movement
    let playerY = s.playerY;
    if (this.keys.has('w') || this.keys.has('W') || this.keys.has('ArrowUp')) {
      playerY = Math.max(0, playerY - PADDLE_SPEED);
    }
    if (this.keys.has('s') || this.keys.has('S') || this.keys.has('ArrowDown')) {
      playerY = Math.min(CANVAS_H - PADDLE_H, playerY + PADDLE_SPEED);
    }

    // PC AI: track ball with limited speed
    const pcCenter = s.pcY + PADDLE_H / 2;
    const ballCenter = s.ballY + BALL_SIZE / 2;
    const diff = ballCenter - pcCenter;
    const maxMove = PADDLE_SPEED * PC_DIFFICULTY;
    let pcY = s.pcY + Math.sign(diff) * Math.min(Math.abs(diff), maxMove);
    pcY = Math.max(0, Math.min(CANVAS_H - PADDLE_H, pcY));

    // Ball movement
    let { ballX, ballVx, ballY, ballVy } = s;
    ballX += ballVx;
    ballY += ballVy;

    // Top / bottom wall bounce
    if (ballY <= 0) { ballY = 0; ballVy = Math.abs(ballVy); }
    if (ballY + BALL_SIZE >= CANVAS_H) { ballY = CANVAS_H - BALL_SIZE; ballVy = -Math.abs(ballVy); }

    // Player paddle collision
    if (
      ballX <= PLAYER_X + PADDLE_W &&
      ballX >= PLAYER_X &&
      ballY + BALL_SIZE >= playerY &&
      ballY <= playerY + PADDLE_H &&
      ballVx < 0
    ) {
      ballX = PLAYER_X + PADDLE_W;
      ballVx = Math.min(Math.abs(ballVx) * 1.05, BALL_MAX_SPEED);
      const hit = (ballY + BALL_SIZE / 2 - (playerY + PADDLE_H / 2)) / (PADDLE_H / 2);
      ballVy = hit * 7;
    }

    // PC paddle collision
    if (
      ballX + BALL_SIZE >= PC_X &&
      ballX + BALL_SIZE <= PC_X + PADDLE_W &&
      ballY + BALL_SIZE >= pcY &&
      ballY <= pcY + PADDLE_H &&
      ballVx > 0
    ) {
      ballX = PC_X - BALL_SIZE;
      ballVx = -Math.min(Math.abs(ballVx) * 1.05, BALL_MAX_SPEED);
      const hit = (ballY + BALL_SIZE / 2 - (pcY + PADDLE_H / 2)) / (PADDLE_H / 2);
      ballVy = hit * 7;
    }

    // Scoring
    let { playerScore, pcScore } = s;
    let scored = false;
    if (ballX + BALL_SIZE < 0) { pcScore++; scored = true; }
    if (ballX > CANVAS_W) { playerScore++; scored = true; }

    if (scored) {
      const reset = this.resetBall();
      const winner = playerScore >= this.WIN_SCORE ? 'player'
                   : pcScore >= this.WIN_SCORE ? 'pc' : null;
      this.zone.run(() => {
        this.state.set({
          playerY, pcY, playerScore, pcScore,
          winner,
          phase: winner ? 'over' : 'playing',
          ...reset,
        });
      });
      if (winner) cancelAnimationFrame(this.animId);
      return;
    }

    this.state.set({ ...s, playerY, pcY, ballX, ballY, ballVx, ballVy, playerScore, pcScore });
  }

  private render() {
    const s = this.state();
    const ctx = this.ctx;

    // Background
    ctx.fillStyle = '#111';
    ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);

    // Center dashed line
    ctx.setLineDash([10, 14]);
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(CANVAS_W / 2, 0);
    ctx.lineTo(CANVAS_W / 2, CANVAS_H);
    ctx.stroke();
    ctx.setLineDash([]);

    // Paddles
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    this.roundRect(ctx, PLAYER_X, s.playerY, PADDLE_W, PADDLE_H, 4);
    ctx.fill();

    ctx.fillStyle = '#ff4444';
    ctx.beginPath();
    this.roundRect(ctx, PC_X, s.pcY, PADDLE_W, PADDLE_H, 4);
    ctx.fill();

    // Ball
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.roundRect(s.ballX, s.ballY, BALL_SIZE, BALL_SIZE, 3);
    ctx.fill();
  }

  private roundRect(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
    ctx.roundRect(x, y, w, h, r);
  }
}
