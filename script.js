document.addEventListener('DOMContentLoaded', async () => {
  const setText = (selector, value) => {
    const el = document.querySelector(selector);
    if (el) el.textContent = value;
  };

  document.title = 'OrchardCraft | From Orchard to Table';
  const metaDescription = document.querySelector('meta[name="description"]');
  if (metaDescription) {
    metaDescription.setAttribute(
      'content',
      'OrchardCraft is a premium apple producer and processor combining sustainable farming with modern quality control, cold-chain logistics, and certified exports.'
    );
  }

  setText('.logo-icon', 'O');
  setText('.hero-eyebrow', 'Family grown, export ready');
  const heroHeadline = document.querySelector('.hero-headline');
  if (heroHeadline) {
    heroHeadline.innerHTML = 'From Orchard to Table<br><em>with traceable quality in every crate</em>';
  }
  setText('.hero-sub', 'Sustainable farming, careful grading, and cold-chain logistics come together in one focused promise: apples that arrive crisp, safe, and consistent.');
  setText('#process .section-eyebrow', 'How we work');
  setText('#process .section-sub', 'Every apple that leaves our facility passes through four clear stages of care. Each step is designed to protect flavour, appearance, and shelf life.');
  setText('#products .section-eyebrow', 'What we grow');
  setText('#products .section-sub', 'Six distinct varieties selected for freshness, juice production, and export-grade consistency. Filter by use case to find the right fit.');
  setText('#sustainability .section-eyebrow', 'Our responsibility');
  setText('#sustainability .sustainability-intro', 'We treat the land as a partner, not a resource. Every decision, from irrigation to packaging, is weighed against its environmental cost.');
  setText('#certifications .section-eyebrow', 'Independently verified');
  setText('#certifications .section-sub', 'Our standards are audited, not implied. Every certification here represents a third-party review of our processes.');
  setText('#testimonials .section-eyebrow', 'Trusted worldwide');
  setText('.quality-guarantee', 'Every apple that carries our name is fully traceable, from the tree it grew on to the moment it reaches you. That is our guarantee to every partner and every consumer.');
  setText('.footer-tagline', 'Family roots. Industrial precision. Global reach.');

  const header = document.getElementById('site-header');
  const hamburger = document.getElementById('hamburger');
  const navList = document.getElementById('nav-list');

  const onScroll = () => {
    header?.classList.toggle('scrolled', window.scrollY > 60);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  hamburger?.addEventListener('click', () => {
    const isOpen = navList.classList.toggle('open');
    hamburger.classList.toggle('open');
    hamburger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });

  navList?.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      navList.classList.remove('open');
      hamburger.classList.remove('open');
      hamburger.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    });
  });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && navList?.classList.contains('open')) {
      navList.classList.remove('open');
      hamburger.classList.remove('open');
      hamburger.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }
  });

  const heroBg = document.getElementById('hero-bg');
  if (heroBg && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    window.addEventListener('scroll', () => {
      heroBg.style.transform = `scale(1.06) translateY(${window.scrollY * 0.25}px)`;
    }, { passive: true });
  }

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

  const statNumbers = document.querySelectorAll('.stat-number');
  const easeOutQuart = t => 1 - Math.pow(1 - t, 4);
  const animateCounter = (el) => {
    const target = parseInt(el.getAttribute('data-target'), 10);
    const duration = 1800;
    const startTime = performance.now();
    const tick = (now) => {
      const progress = Math.min((now - startTime) / duration, 1);
      el.textContent = Math.round(easeOutQuart(progress) * target).toLocaleString('en-US');
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

  const DEFAULT_PRODUCTS = [
    { name: 'Red Delicious', category: 'fresh', taste: 'Sweet & crisp with a classic rich flavour', uses: 'Fresh eating, premium fruit bowls, retail display', season: 'September - November', image: 'assets/apple_placeholder.png' },
    { name: 'Golden Gala', category: 'fresh', taste: 'Mildly sweet, honeyed, very low acidity', uses: 'Snacking, salads, baking, school programmes', season: 'July - September', image: 'assets/apple_placeholder.png' },
    { name: 'Fuji', category: 'fresh', taste: 'Very sweet, dense, subtly aromatic', uses: 'Fresh market, premium gift packs, export', season: 'October - December', image: 'assets/apple_placeholder.png' },
    { name: 'Granny Smith', category: 'export', taste: 'Sharply tart, firm, refreshingly acidic', uses: 'Export, pie filling, cheese pairings', season: 'October - January', image: 'assets/apple_placeholder.png' },
    { name: 'Pink Lady', category: 'export', taste: 'Sweet-tart, crisp, slightly effervescent', uses: 'Premium export, luxury retail display', season: 'November - March', image: 'assets/apple_placeholder.png' },
    { name: 'Braeburn', category: 'juice', taste: 'Perfect sweet-tart balance, warm spice notes', uses: 'Juice blends, cider, premium drinking apples', season: 'October - February', image: 'assets/apple_placeholder.png' },
  ];

  const CATEGORY_LABELS = {
    fresh: 'Fresh Market',
    juice: 'Juice Production',
    export: 'Export Grade',
  };

  const productGrid = document.getElementById('product-grid');
  let productSource = DEFAULT_PRODUCTS;

  const loadProducts = async () => {
    try {
      const response = await fetch('data/products.json', { cache: 'no-store' });
      if (!response.ok) throw new Error('Unable to load product data');
      const data = await response.json();
      if (Array.isArray(data) && data.length) return data;
    } catch (error) {
      console.warn('Using fallback product data.', error);
    }
    return DEFAULT_PRODUCTS;
  };

  const createProductCard = (product) => {
    const card = document.createElement('div');
    card.className = 'product-card';
    card.setAttribute('role', 'listitem');
    const catClass = `cat-${product.category}`;
    const catLabel = CATEGORY_LABELS[product.category] || product.category;
    const image = product.image || 'assets/apple_placeholder.png';

    card.innerHTML = `
      <div class="product-card-img-wrap">
        <img class="product-card-img" src="${image}" alt="${product.name}" loading="lazy" />
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

  const renderProducts = (filter) => {
    const filtered = filter === 'all' ? productSource : productSource.filter(p => p.category === filter);
    productGrid.style.opacity = '0';
    productGrid.style.transform = 'translateY(12px)';
    setTimeout(() => {
      productGrid.innerHTML = '';
      filtered.forEach(p => productGrid.appendChild(createProductCard(p)));
      productGrid.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      productGrid.style.opacity = '1';
      productGrid.style.transform = 'translateY(0)';
    }, 160);
  };

  productSource = await loadProducts();
  renderProducts('all');

  const filterBtns = document.querySelectorAll('.filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      renderProducts(btn.dataset.filter);
    });
  });

  const certBadges = document.querySelectorAll('.cert-badge');
  const certDetailBox = document.getElementById('cert-detail-box');
  const certDetailTxt = document.getElementById('cert-detail-text');
  const defaultTxt = 'Hover over a badge to learn what each certification means for your supply chain.';
  const badgeImages = {
    'ISO 22000': 'assets/badges/iso22000.svg',
    'HACCP': 'assets/badges/haccp.svg',
    'GlobalGAP': 'assets/badges/globalgap.svg',
    'Organic Certified': 'assets/badges/organic.svg',
  };

  certBadges.forEach(badge => {
    const inner = badge.querySelector('.cert-badge-inner');
    const label = badge.getAttribute('data-label');
    if (inner && !inner.querySelector('img')) {
      const img = document.createElement('img');
      img.src = badgeImages[label] || badgeImages['ISO 22000'];
      img.alt = '';
      img.setAttribute('aria-hidden', 'true');
      img.className = 'cert-badge-art';
      inner.insertBefore(img, inner.firstChild);
    }

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

  const partnerLogos = document.getElementById('partner-logos');
  if (partnerLogos) {
    partnerLogos.innerHTML = `
      <img src="assets/partners/supermarket1.svg" alt="FreshMart" class="partner-logo-item" />
      <img src="assets/partners/supermarket2.svg" alt="JuiceWorld" class="partner-logo-item" />
      <img src="assets/partners/export1.svg" alt="EuroFruits" class="partner-logo-item" />
    `;
  }

  const contactForm = document.getElementById('contact-form');
  const contactSuccess = document.getElementById('form-success');
  if (contactForm) {
    contactForm.addEventListener('submit', e => {
      e.preventDefault();
      const submit = document.getElementById('contact-submit');
      submit.disabled = true;
      submit.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Sending...';
      setTimeout(() => {
        contactForm.reset();
        submit.disabled = false;
        submit.innerHTML = 'Send Message <i class="fa-solid fa-paper-plane"></i>';
        contactSuccess.hidden = false;
        setTimeout(() => { contactSuccess.hidden = true; }, 6000);
      }, 1200);
    });
  }

  const newsletterForm = document.getElementById('newsletter-form');
  const newsletterSuccess = document.getElementById('newsletter-success');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', e => {
      e.preventDefault();
      const submit = document.getElementById('newsletter-submit');
      submit.disabled = true;
      submit.textContent = '...';
      setTimeout(() => {
        newsletterForm.reset();
        submit.disabled = false;
        submit.textContent = 'Subscribe';
        newsletterSuccess.hidden = false;
        setTimeout(() => { newsletterSuccess.hidden = true; }, 5000);
      }, 900);
    });
  }

  const sections = document.querySelectorAll('section[id], footer[id]');
  const navLinks = document.querySelectorAll('.nav-link');
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
