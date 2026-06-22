/**
 * FlowState Landing Page — Enhanced Interactions
 * Vanilla JS, GPU-accelerated transforms only where possible.
 * Sections map to Figma component groups for handoff.
 */

(function () {
  'use strict';

  /* ── Config (tweak via CSS vars where possible) ── */
  const CONFIG = {
    magneticRadius: 20,
    magneticStrength: 0.35,
    cursorLag: 0.12,
    carouselInterval: 5000,
    particleCount: 40,
    particleCountMobile: 15,
    confettiCount: 60,
    typingPhrases: ['you@company.com', 'name@work.com', 'hello@flowstate.app'],
    typingSpeed: 80,
    typingPause: 2000,
  };

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isMobile = window.matchMedia('(max-width: 768px)').matches;
  const isTouch = window.matchMedia('(pointer: coarse)').matches;

  /* ══════════════════════════════════════════
     THEME — data-theme + localStorage
     ══════════════════════════════════════════ */
  const Theme = {
    init() {
      const saved = localStorage.getItem('flowstate-theme');
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const theme = saved || (prefersDark ? 'dark' : 'light');
      document.documentElement.setAttribute('data-theme', theme);

      document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
        btn.addEventListener('click', () => this.toggle());
        btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
      });
    },
    toggle() {
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('flowstate-theme', next);
      document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
        btn.setAttribute('aria-label', next === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
      });
    },
  };

  /* ══════════════════════════════════════════
     PAGE LOADER — skeleton fade-out
     ══════════════════════════════════════════ */
  const Loader = {
    init() {
      const loader = document.getElementById('page-loader');
      if (!loader) return;
      window.addEventListener('load', () => {
        setTimeout(() => loader.classList.add('hidden'), reducedMotion ? 0 : 400);
      });
    },
  };

  /* ══════════════════════════════════════════
     CUSTOM CURSOR — dot + ring trail
     ══════════════════════════════════════════ */
  const Cursor = {
    dot: null,
    ring: null,
    mouse: { x: 0, y: 0 },
    dotPos: { x: 0, y: 0 },
    ringPos: { x: 0, y: 0 },

    init() {
      if (reducedMotion || isMobile || isTouch) {
        document.body.classList.add('no-custom-cursor');
        return;
      }
      this.dot = document.querySelector('.cursor-dot');
      this.ring = document.querySelector('.cursor-ring');
      if (!this.dot || !this.ring) return;

      document.body.classList.add('has-custom-cursor');
      document.addEventListener('mousemove', (e) => {
        this.mouse.x = e.clientX;
        this.mouse.y = e.clientY;
      });
      document.querySelectorAll('a, button, [role="button"], input, .feature-card').forEach((el) => {
        el.addEventListener('mouseenter', () => this.ring.classList.add('active'));
        el.addEventListener('mouseleave', () => this.ring.classList.remove('active'));
      });
      this.tick();
    },
    tick() {
      const lag = CONFIG.cursorLag;
      this.dotPos.x += (this.mouse.x - this.dotPos.x) * (1 - lag * 0.5);
      this.dotPos.y += (this.mouse.y - this.dotPos.y) * (1 - lag * 0.5);
      this.ringPos.x += (this.mouse.x - this.ringPos.x) * (1 - lag);
      this.ringPos.y += (this.mouse.y - this.ringPos.y) * (1 - lag);
      this.dot.style.transform = `translate(${this.dotPos.x}px, ${this.dotPos.y}px) translate(-50%, -50%)`;
      this.ring.style.transform = `translate(${this.ringPos.x}px, ${this.ringPos.y}px) translate(-50%, -50%)`;
      requestAnimationFrame(() => this.tick());
    },
  };

  /* ══════════════════════════════════════════
     SMOOTH SCROLL — Lenis (CDN) with native fallback
     ══════════════════════════════════════════ */
  const SmoothScroll = {
    init() {
      if (reducedMotion || typeof Lenis === 'undefined') return;
      const lenis = new Lenis({ duration: 1.1, smoothWheel: true });
      function raf(time) {
        lenis.raf(time);
        requestAnimationFrame(raf);
      }
      requestAnimationFrame(raf);
      document.querySelectorAll('a[href^="#"]').forEach((a) => {
        a.addEventListener('click', (e) => {
          const id = a.getAttribute('href');
          if (id === '#') return;
          const target = document.querySelector(id);
          if (target) {
            e.preventDefault();
            lenis.scrollTo(target, { offset: -72 });
          }
        });
      });
    },
  };

  /* ══════════════════════════════════════════
     HERO — word reveal stagger
     ══════════════════════════════════════════ */
  const HeroWords = {
    init() {
      if (reducedMotion) {
        document.querySelectorAll('.hero__word').forEach((w) => w.classList.add('visible'));
        return;
      }
      requestAnimationFrame(() => {
        document.querySelectorAll('.hero__word').forEach((w) => w.classList.add('visible'));
      });
    },
  };

  /* ══════════════════════════════════════════
     MAGNETIC BUTTONS — cursor pull within radius
     ══════════════════════════════════════════ */
  const MagneticButtons = {
    init() {
      if (reducedMotion || isTouch) return;
      document.querySelectorAll('.btn--magnetic').forEach((btn) => {
        btn.addEventListener('mousemove', (e) => {
          const rect = btn.getBoundingClientRect();
          const cx = rect.left + rect.width / 2;
          const cy = rect.top + rect.height / 2;
          const dx = e.clientX - cx;
          const dy = e.clientY - cy;
          const dist = Math.hypot(dx, dy);
          if (dist < CONFIG.magneticRadius * 3) {
            const pull = Math.min(dist, CONFIG.magneticRadius * 3) / (CONFIG.magneticRadius * 3);
            btn.style.transform = `translate(${dx * CONFIG.magneticStrength * pull}px, ${dy * CONFIG.magneticStrength * pull}px) scale(1.02)`;
          }
        });
        btn.addEventListener('mouseleave', () => {
          btn.style.transform = '';
        });
      });
    },
  };

  /* ══════════════════════════════════════════
     SCROLL REVEAL — IntersectionObserver
     ══════════════════════════════════════════ */
  const ScrollReveal = {
    init() {
      const els = document.querySelectorAll('.reveal, .stagger, .feature-card, .pricing-card');
      if (reducedMotion) {
        els.forEach((el) => {
          el.classList.add('visible', 'in-view');
        });
        return;
      }
      const obs = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add('visible', 'in-view');
              obs.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.12, rootMargin: '0px 0px -48px 0px' }
      );
      els.forEach((el) => obs.observe(el));
    },
  };

  /* ══════════════════════════════════════════
     FEATURE CARDS — 3D tilt on mousemove
     ══════════════════════════════════════════ */
  const FeatureTilt = {
    init() {
      if (reducedMotion || isTouch || isMobile) return;
      document.querySelectorAll('.feature-card').forEach((card) => {
        const inner = card.querySelector('.feature-card__inner');
        if (!inner) return;
        card.addEventListener('mousemove', (e) => {
          const rect = card.getBoundingClientRect();
          const x = (e.clientX - rect.left) / rect.width - 0.5;
          const y = (e.clientY - rect.top) / rect.height - 0.5;
          const tiltX = -y * 8;
          const tiltY = x * 8;
          inner.style.transform = `translateY(-8px) rotateX(${tiltX}deg) rotateY(${tiltY}deg)`;
        });
        card.addEventListener('mouseleave', () => {
          inner.style.transform = '';
        });
      });
    },
  };

  /* ══════════════════════════════════════════
     TIMELINE — SVG draw + step activation + count-up
     ══════════════════════════════════════════ */
  const Timeline = {
    path: null,
    pathLength: 0,
    steps: [],

    init() {
      this.path = document.querySelector('.timeline__svg path');
      this.steps = [...document.querySelectorAll('.timeline__step')];
      if (!this.path) return;

      this.pathLength = this.path.getTotalLength();
      this.path.style.strokeDasharray = this.pathLength;
      this.path.style.strokeDashoffset = this.pathLength;

      this.steps.forEach((step, i) => {
        const circle = step.querySelector('.timeline__circle');
        if (circle) {
          circle.dataset.target = String(i + 1);
          if (!reducedMotion) circle.textContent = '0';
        }
      });

      if (reducedMotion) {
        this.path.style.strokeDashoffset = '0';
        this.steps.forEach((s, i) => {
          s.classList.add('active');
          const c = s.querySelector('.timeline__circle');
          if (c) c.textContent = String(i + 1);
        });
        return;
      }

      window.addEventListener('scroll', () => this.onScroll(), { passive: true });
      this.onScroll();
    },

    onScroll() {
      const section = document.querySelector('.how-it-works');
      if (!section || !this.path) return;
      const rect = section.getBoundingClientRect();
      const vh = window.innerHeight;
      const start = vh * 0.85;
      const end = vh * 0.2;
      const progress = Math.max(0, Math.min(1, (start - rect.top) / (rect.height + start - end)));
      this.path.style.strokeDashoffset = this.pathLength * (1 - progress);

      this.steps.forEach((step, i) => {
        const threshold = (i + 1) / this.steps.length;
        if (progress >= threshold * 0.6) {
          step.classList.add('active');
          this.countUp(step.querySelector('.timeline__circle'), i + 1);
        }
      });
    },

    countUp(el, target) {
      if (!el || el.dataset.done === '1') return;
      el.dataset.done = '1';
      if (reducedMotion) {
        el.textContent = String(target);
        return;
      }
      let current = 0;
      const step = () => {
        current++;
        el.textContent = String(current);
        if (current < target) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    },
  };

  /* ══════════════════════════════════════════
     PRICING — monthly/yearly toggle + slot digits
     ══════════════════════════════════════════ */
  const Pricing = {
    yearly: false,
    prices: {
      free: { monthly: 0, yearly: 0 },
      pro: { monthly: 9, yearly: 7 },
      team: { monthly: 19, yearly: 15 },
    },

    init() {
      const toggle = document.querySelector('.pricing__toggle');
      const labels = document.querySelectorAll('.pricing__toggle-label');
      if (!toggle) return;

      toggle.addEventListener('click', () => {
        this.yearly = !this.yearly;
        toggle.setAttribute('aria-checked', this.yearly ? 'true' : 'false');
        labels[0]?.classList.toggle('active', !this.yearly);
        labels[1]?.classList.toggle('active', this.yearly);
        this.updatePrices();
      });

      document.querySelectorAll('.price-digits').forEach((el) => {
        el.dataset.value = el.textContent.trim();
      });
      this.updatePrices();
    },

    updatePrices() {
      Object.keys(this.prices).forEach((key) => {
        const digitsEl = document.querySelector(`.price-digits[data-key="${key}"]`);
        if (!digitsEl) return;
        const val = this.yearly ? this.prices[key].yearly : this.prices[key].monthly;
        this.animateDigits(digitsEl, val);
      });
    },

    animateDigits(el, target) {
      const current = parseInt(el.dataset.value || el.textContent || '0', 10);
      if (current === target) return;
      el.dataset.value = String(target);

      if (reducedMotion) {
        el.textContent = String(target);
        return;
      }

      /* Slot-style morph: fade out, swap digit, spring back */
      el.style.transition = 'transform 0.35s cubic-bezier(0.34,1.56,0.64,1), opacity 0.2s ease';
      el.style.transform = 'translateY(-100%)';
      el.style.opacity = '0';
      setTimeout(() => {
        el.textContent = String(target);
        el.style.transform = 'translateY(100%)';
        requestAnimationFrame(() => {
          el.style.transform = 'translateY(0)';
          el.style.opacity = '1';
        });
      }, 200);
    },
  };

  /* ══════════════════════════════════════════
     TESTIMONIALS — 3D cube carousel
     ══════════════════════════════════════════ */
  const Carousel = {
    index: 0,
    total: 0,
    timer: null,
    scene: null,

    init() {
      this.scene = document.querySelector('.carousel__scene');
      const cards = document.querySelectorAll('.carousel__scene .testimonial-card');
      this.total = cards.length;
      if (!this.scene || this.total === 0) return;

      cards.forEach((card, i) => {
        const angle = (360 / this.total) * i;
        card.style.transform = `rotateY(${angle}deg) translateZ(280px)`;
      });

      document.querySelectorAll('.carousel__dot').forEach((dot, i) => {
        dot.addEventListener('click', () => this.goTo(i));
      });

      if (!reducedMotion) {
        this.timer = setInterval(() => this.next(), CONFIG.carouselInterval);
        this.scene.closest('.carousel')?.addEventListener('mouseenter', () => clearInterval(this.timer));
        this.scene.closest('.carousel')?.addEventListener('mouseleave', () => {
          this.timer = setInterval(() => this.next(), CONFIG.carouselInterval);
        });
      }
      this.goTo(0);
    },

    goTo(i) {
      this.index = i;
      const angle = -(360 / this.total) * i;
      this.scene.style.transform = `rotateY(${angle}deg)`;
      document.querySelectorAll('.carousel__dot').forEach((d, j) => d.classList.toggle('active', j === i));
    },

    next() {
      this.goTo((this.index + 1) % this.total);
    },
  };

  /* ══════════════════════════════════════════
     FAQ — spring accordion (one open)
     ══════════════════════════════════════════ */
  const FAQ = {
    init() {
      document.querySelectorAll('.faq__item').forEach((item) => {
        const btn = item.querySelector('.faq__question');
        btn?.addEventListener('click', () => {
          const wasOpen = item.classList.contains('open');
          document.querySelectorAll('.faq__item').forEach((i) => i.classList.remove('open'));
          if (!wasOpen) item.classList.add('open');
        });
      });
    },
  };

  /* ══════════════════════════════════════════
     CTA — typing placeholder + confetti submit
     ══════════════════════════════════════════ */
  const CTA = {
    init() {
      this.initTyping();
      this.initSubmit();
    },

    initTyping() {
      const el = document.querySelector('.final-cta__typing');
      const input = document.querySelector('.final-cta__input');
      if (!el || reducedMotion) {
        if (el) el.textContent = 'Enter your email';
        return;
      }

      let phraseIdx = 0;
      let charIdx = 0;
      let deleting = false;

      const tick = () => {
        if (input && document.activeElement === input) {
          setTimeout(tick, 500);
          return;
        }
        const phrase = CONFIG.typingPhrases[phraseIdx];
        if (!deleting) {
          el.textContent = phrase.slice(0, charIdx + 1);
          charIdx++;
          if (charIdx === phrase.length) {
            deleting = true;
            setTimeout(tick, CONFIG.typingPause);
            return;
          }
          setTimeout(tick, CONFIG.typingSpeed);
        } else {
          el.textContent = phrase.slice(0, charIdx - 1);
          charIdx--;
          if (charIdx === 0) {
            deleting = false;
            phraseIdx = (phraseIdx + 1) % CONFIG.typingPhrases.length;
            setTimeout(tick, 400);
            return;
          }
          setTimeout(tick, CONFIG.typingSpeed * 0.6);
        }
      };
      tick();
    },

    initSubmit() {
      const form = document.querySelector('.final-cta__form');
      const btn = form?.querySelector('button[type="submit"]');
      if (!form || !btn) return;

      form.addEventListener('submit', (e) => {
        e.preventDefault();
        if (btn.classList.contains('btn--success')) return;

        btn.classList.add('btn--success');
        btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>';
        Confetti.burst(form.getBoundingClientRect());

        setTimeout(() => {
          btn.classList.remove('btn--success');
          btn.textContent = 'Start free';
          form.reset();
        }, 3000);
      });
    },
  };

  /* ══════════════════════════════════════════
     PARTICLES — constellation in final CTA
     ══════════════════════════════════════════ */
  const Particles = {
    canvas: null,
    ctx: null,
    points: [],
    mouse: { x: -9999, y: -9999 },

    init() {
      this.canvas = document.querySelector('.final-cta__canvas');
      if (!this.canvas || reducedMotion) return;

      this.ctx = this.canvas.getContext('2d');
      const count = isMobile ? CONFIG.particleCountMobile : CONFIG.particleCount;
      this.resize();
      for (let i = 0; i < count; i++) {
        this.points.push({
          x: Math.random() * this.canvas.width,
          y: Math.random() * this.canvas.height,
          vx: (Math.random() - 0.5) * 0.3,
          vy: (Math.random() - 0.5) * 0.3,
        });
      }

      const section = this.canvas.closest('.final-cta__inner');
      section?.addEventListener('mousemove', (e) => {
        const rect = this.canvas.getBoundingClientRect();
        this.mouse.x = e.clientX - rect.left;
        this.mouse.y = e.clientY - rect.top;
      });
      section?.addEventListener('mouseleave', () => {
        this.mouse.x = -9999;
        this.mouse.y = -9999;
      });

      window.addEventListener('resize', () => this.resize());
      this.loop();
    },

    resize() {
      if (!this.canvas) return;
      const rect = this.canvas.parentElement.getBoundingClientRect();
      this.canvas.width = rect.width;
      this.canvas.height = rect.height;
    },

    loop() {
      if (!this.ctx) return;
      const { ctx, canvas, points, mouse } = this;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      points.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

        const dx = mouse.x - p.x;
        const dy = mouse.y - p.y;
        const dist = Math.hypot(dx, dy);
        if (dist < 120) {
          p.x -= dx * 0.02;
          p.y -= dy * 0.02;
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, 2, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255,255,255,0.5)';
        ctx.fill();
      });

      for (let i = 0; i < points.length; i++) {
        for (let j = i + 1; j < points.length; j++) {
          const d = Math.hypot(points[i].x - points[j].x, points[i].y - points[j].y);
          if (d < 100) {
            ctx.beginPath();
            ctx.moveTo(points[i].x, points[i].y);
            ctx.lineTo(points[j].x, points[j].y);
            ctx.strokeStyle = `rgba(255,255,255,${0.15 * (1 - d / 100)})`;
            ctx.stroke();
          }
        }
      }
      requestAnimationFrame(() => this.loop());
    },
  };

  /* ══════════════════════════════════════════
     CONFETTI — burst on form submit
     ══════════════════════════════════════════ */
  const Confetti = {
    canvas: null,
    ctx: null,
    pieces: [],

    init() {
      this.canvas = document.querySelector('.confetti-canvas');
      if (!this.canvas) return;
      this.ctx = this.canvas.getContext('2d');
      this.resize();
      window.addEventListener('resize', () => this.resize());
    },

    resize() {
      if (!this.canvas) return;
      this.canvas.width = window.innerWidth;
      this.canvas.height = window.innerHeight;
    },

    burst(rect) {
      if (!this.ctx || reducedMotion) return;
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      const colors = ['#818CF8', '#C4B5FD', '#FBBF24', '#34D399', '#F472B6'];

      this.pieces = [];
      for (let i = 0; i < CONFIG.confettiCount; i++) {
        this.pieces.push({
          x: cx,
          y: cy,
          vx: (Math.random() - 0.5) * 14,
          vy: Math.random() * -12 - 4,
          color: colors[i % colors.length],
          size: Math.random() * 6 + 4,
          rot: Math.random() * 360,
          vr: (Math.random() - 0.5) * 10,
          life: 1,
        });
      }
      this.animate();
    },

    animate() {
      if (!this.ctx) return;
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      let alive = false;

      this.pieces.forEach((p) => {
        if (p.life <= 0) return;
        alive = true;
        p.x += p.vx;
        p.y += p.vy;
        p.vy += 0.35;
        p.rot += p.vr;
        p.life -= 0.012;

        this.ctx.save();
        this.ctx.translate(p.x, p.y);
        this.ctx.rotate((p.rot * Math.PI) / 180);
        this.ctx.globalAlpha = p.life;
        this.ctx.fillStyle = p.color;
        this.ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
        this.ctx.restore();
      });

      if (alive) requestAnimationFrame(() => this.animate());
      else this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    },
  };

  /* ══════════════════════════════════════════
     MOBILE NAV
     ══════════════════════════════════════════ */
  const MobileNav = {
    init() {
      const hamburger = document.querySelector('.hamburger');
      const mobileNav = document.querySelector('.mobile-nav');
      if (!hamburger || !mobileNav) return;

      hamburger.addEventListener('click', () => {
        const open = hamburger.getAttribute('aria-expanded') === 'true';
        hamburger.setAttribute('aria-expanded', !open);
        mobileNav.classList.toggle('open');
        document.body.style.overflow = open ? '' : 'hidden';
      });

      mobileNav.querySelectorAll('a').forEach((link) => {
        link.addEventListener('click', () => {
          hamburger.setAttribute('aria-expanded', 'false');
          mobileNav.classList.remove('open');
          document.body.style.overflow = '';
        });
      });
    },
  };

  /* ══════════════════════════════════════════
     BOOT
     ══════════════════════════════════════════ */
  document.addEventListener('DOMContentLoaded', () => {
    Theme.init();
    Loader.init();
    Cursor.init();
    HeroWords.init();
    MagneticButtons.init();
    ScrollReveal.init();
    FeatureTilt.init();
    Timeline.init();
    Pricing.init();
    Carousel.init();
    FAQ.init();
    CTA.init();
    Particles.init();
    Confetti.init();
    MobileNav.init();
    SmoothScroll.init();
  });
})();
