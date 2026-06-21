/* ═══════════════════════════════════════════════
   OrchardCraft — Main Script
   ═══════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  /* ──────────────────────────────────────────────
     1. NAVIGATION — scroll behaviour + hamburger
  ────────────────────────────────────────────── */
  const header    = document.getElementById('site-header');
  const hamburger = document.getElementById('hamburger');
  const navList   = document.getElementById('nav-list');

  // Sticky header styles on scroll
  const onScroll = () => {
    if (window.scrollY > 60) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll(); // run once on load

  // Hamburger toggle
  hamburger.addEventListener('click', () => {
    const isOpen = navList.classList.toggle('open');
    hamburger.classList.toggle('open');
    hamburger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });

  // Close mobile menu when a nav link is clicked
  navList.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      navList.classList.remove('open');
      hamburger.classList.remove('open');
      hamburger.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    });
  });

  // Close on Escape
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && navList.classList.contains('open')) {
      navList.classList.remove('open');
      hamburger.classList.remove('open');
      hamburger.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }
  });

  /* ──────────────────────────────────────────────
     2. HERO PARALLAX
  ────────────────────────────────────────────── */
  const heroBg = document.getElementById('hero-bg');
  if (heroBg && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      heroBg.style.transform = `scale(1.06) translateY(${y * 0.25}px)`;
    }, { passive: true });
  }

  /* ──────────────────────────────────────────────
     3. INTERSECTION OBSERVER — scroll animations (AOS-lite)
  ────────────────────────────────────────────── */
  const aosElements = document.querySelectorAll('[data-aos]');
  const aosObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('aos-animate');
        aosObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  aosElements.forEach(el => aosObserver.observe(el));

  /* ──────────────────────────────────────────────
     4. STATS COUNTER ANIMATION
  ────────────────────────────────────────────── */
  const statNumbers = document.querySelectorAll('.stat-number');

  const easeOutQuart = t => 1 - Math.pow(1 - t, 4);

  const animateCounter = (el) => {
    const target    = parseInt(el.getAttribute('data-target'), 10);
    const duration  = 1800; // ms
    const startTime = performance.now();

    const tick = (now) => {
      const elapsed  = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const value    = Math.round(easeOutQuart(progress) * target);
      el.textContent = value.toLocaleString('en-US');
      if (progress < 1) requestAnimationFrame(tick);
    };

    requestAnimationFrame(tick);
  };

  const counterObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  statNumbers.forEach(el => counterObserver.observe(el));

  /* ──────────────────────────────────────────────
     5. PRODUCT DATA + RENDER
  ────────────────────────────────────────────── */
  const PRODUCTS = [
    {
      name:     'Red Delicious',
      category: 'fresh',
      taste:    'Sweet & crisp with a classic rich flavour',
      uses:     'Fresh eating, premium fruit bowls, retail display',
      season:   '🍂 September – November',
    },
    {
      name:     'Golden Gala',
      category: 'fresh',
      taste:    'Mildly sweet, honeyed, very low acidity',
      uses:     'Snacking, salads, baking, school programmes',
      season:   '☀️ July – September',
    },
    {
      name:     'Fuji',
      category: 'fresh',
      taste:    'Very sweet, dense, subtly aromatic',
      uses:     'Fresh market, premium gift packs, export',
      season:   '🍂 October – December',
    },
    {
      name:     'Granny Smith',
      category: 'export',
      taste:    'Sharply tart, firm, refreshingly acidic',
      uses:     'Export, pie filling, cheese pairings',
      season:   '❄️ October – January',
    },
    {
      name:     'Pink Lady',
      category: 'export',
      taste:    'Sweet-tart, crisp, slightly effervescent',
      uses:     'Premium export, luxury retail display',
      season:   '❄️ November – March',
    },
    {
      name:     'Braeburn',
      category: 'juice',
      taste:    'Perfect sweet-tart balance, warm spice notes',
      uses:     'Juice blends, cider, premium drinking apples',
      season:   '🍂 October – February',
    },
  ];

  const CATEGORY_LABELS = {
    fresh:  'Fresh Market',
    juice:  'Juice Production',
    export: 'Export Grade',
  };

  // Apple emoji colors for CSS gradient backgrounds (since we only have one placeholder image)
  const APPLE_GRADIENTS = {
    fresh:  ['linear-gradient(135deg,#d32f2f 0%,#ef5350 50%,#ffcdd2 100%)',
             'linear-gradient(135deg,#c62828 0%,#ef5350 50%,#e57373 100%)',
             'linear-gradient(135deg,#b71c1c 0%,#d32f2f 50%,#f48fb1 100%)'],
    export: ['linear-gradient(135deg,#2e7d32 0%,#4caf50 50%,#c8e6c9 100%)',
             'linear-gradient(135deg,#1b5e20 0%,#388e3c 50%,#a5d6a7 100%)'],
    juice:  ['linear-gradient(135deg,#e65100 0%,#ff9800 50%,#ffe0b2 100%)'],
  };

  const getGradient = (category, index) => {
    const arr = APPLE_GRADIENTS[category] || APPLE_GRADIENTS['fresh'];
    return arr[index % arr.length];
  };

  const createProductCard = (product, catIndex) => {
    const card    = document.createElement('div');
    card.className = 'product-card';
    card.setAttribute('role', 'listitem');

    const catClass = `cat-${product.category}`;
    const catLabel = CATEGORY_LABELS[product.category] || product.category;
    const gradient = getGradient(product.category, catIndex);

    card.innerHTML = `
      <div class="product-card-img-wrap" style="height:220px;overflow:hidden;border-radius:inherit;border-bottom-left-radius:0;border-bottom-right-radius:0;">
        <div style="width:100%;height:100%;background:${gradient};display:flex;align-items:center;justify-content:center;font-size:5rem;">🍎</div>
      </div>
      <div class="product-card-body">
        <span class="product-card-category ${catClass}">${catLabel}</span>
        <h3 class="product-card-name">${product.name}</h3>
        <p class="product-card-taste">${product.taste}</p>
        <p class="product-card-season">${product.season}</p>
      </div>
      <div class="product-card-overlay" aria-hidden="true">
        <span class="overlay-label">Best Used For</span>
        <p class="overlay-uses">${product.uses}</p>
        <p class="overlay-season">${product.season}</p>
      </div>`;

    return card;
  };

  const productGrid = document.getElementById('product-grid');
  let currentFilter = 'all';

  const renderProducts = (filter) => {
    currentFilter = filter;
    const filtered = filter === 'all'
      ? PRODUCTS
      : PRODUCTS.filter(p => p.category === filter);

    // Fade out → update → fade in
    productGrid.style.opacity = '0';
    productGrid.style.transform = 'translateY(12px)';

    setTimeout(() => {
      productGrid.innerHTML = '';
      filtered.forEach((p, i) => productGrid.appendChild(createProductCard(p, i)));
      productGrid.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      productGrid.style.opacity = '1';
      productGrid.style.transform = 'translateY(0)';
    }, 200);
  };

  // Initial render
  renderProducts('all');

  // Filter buttons
  const filterBtns = document.querySelectorAll('.filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => { b.classList.remove('active'); b.setAttribute('aria-selected','false'); });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      renderProducts(btn.dataset.filter);
    });
  });

  /* ──────────────────────────────────────────────
     6. CERTIFICATION BADGE HOVER DESCRIPTIONS
  ────────────────────────────────────────────── */
  const certBadges    = document.querySelectorAll('.cert-badge');
  const certDetailBox = document.getElementById('cert-detail-box');
  const certDetailTxt = document.getElementById('cert-detail-text');
  const defaultTxt    = 'Hover over a badge to learn what each certification means for your supply chain.';

  certBadges.forEach(badge => {
    badge.addEventListener('mouseenter', () => {
      const desc = badge.getAttribute('data-desc');
      const name = badge.getAttribute('data-label');
      certDetailTxt.textContent = `${name}: ${desc}`;
      certDetailBox.style.borderColor = 'var(--green)';
    });
    badge.addEventListener('mouseleave', () => {
      certDetailTxt.textContent = defaultTxt;
      certDetailBox.style.borderColor = '';
    });
    badge.addEventListener('focus', () => {
      certDetailTxt.textContent = badge.getAttribute('data-desc');
    });
  });

  /* ──────────────────────────────────────────────
     7. FORM HANDLING
  ────────────────────────────────────────────── */
  const contactForm    = document.getElementById('contact-form');
  const contactSuccess = document.getElementById('form-success');

  if (contactForm) {
    contactForm.addEventListener('submit', e => {
      e.preventDefault();
      const submit = document.getElementById('contact-submit');
      submit.disabled = true;
      submit.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Sending…';

      // Simulate async request
      setTimeout(() => {
        contactForm.reset();
        submit.disabled = false;
        submit.innerHTML = 'Send Message <i class="fa-solid fa-paper-plane"></i>';
        contactSuccess.hidden = false;
        setTimeout(() => { contactSuccess.hidden = true; }, 6000);
      }, 1200);
    });
  }

  const newsletterForm    = document.getElementById('newsletter-form');
  const newsletterSuccess = document.getElementById('newsletter-success');

  if (newsletterForm) {
    newsletterForm.addEventListener('submit', e => {
      e.preventDefault();
      const submit = document.getElementById('newsletter-submit');
      submit.disabled = true;
      submit.textContent = '…';

      setTimeout(() => {
        newsletterForm.reset();
        submit.disabled = false;
        submit.textContent = 'Subscribe';
        newsletterSuccess.hidden = false;
        setTimeout(() => { newsletterSuccess.hidden = true; }, 5000);
      }, 900);
    });
  }

  /* ──────────────────────────────────────────────
     8. ACTIVE NAV LINK — highlight section in view
  ────────────────────────────────────────────── */
  const sections  = document.querySelectorAll('section[id], footer[id]');
  const navLinks  = document.querySelectorAll('.nav-link');

  const navHighlightObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        navLinks.forEach(link => {
          link.classList.remove('active-nav');
          if (link.getAttribute('href') === `#${entry.target.id}`) {
            link.classList.add('active-nav');
          }
        });
      }
    });
  }, { threshold: 0.4 });

  sections.forEach(s => navHighlightObserver.observe(s));

});
