// app.js

// ----------------------------------------------------
// Local Offline / Rate-Limit Fallback Cache Data
// ----------------------------------------------------
const FALLBACK_PROFILE = {
  login: "MY-o-o",
  name: "MY-o-o",
  avatar_url: "https://avatars.githubusercontent.com/u/210262304?v=4",
  bio: "A versatile software developer skilled in backend systems (Python, C#) and responsive, modern frontends (JavaScript, HTML, CSS).",
  public_repos: 7,
  followers: 0,
  public_gists: 0,
  html_url: "https://github.com/MY-o-o"
};

const FALLBACK_REPOS = [
  {
    id: 1247317087,
    name: "RestaurantBooking",
    html_url: "https://github.com/MY-o-o/RestaurantBooking",
    description: "Django-based restaurant reservation booking application deployed on Railway. Built with clean Python code, sqlite3/postgresql database, and responsive frontend.",
    language: "Python",
    stargazers_count: 0,
    forks_count: 0,
    homepage: "https://restaurant-booking.up.railway.app/",
    pushed_at: "2026-06-05T13:50:44Z"
  },
  {
    id: 1068030692,
    name: "eShop",
    html_url: "https://github.com/MY-o-o/eShop",
    description: "E-Commerce web platform featuring modular shopping flow, cart updates, and product search integrations.",
    language: "JavaScript",
    stargazers_count: 0,
    forks_count: 0,
    homepage: null,
    pushed_at: "2026-06-04T18:07:27Z"
  },
  {
    id: 1037622622,
    name: "FreshHarvestBox",
    html_url: "https://github.com/MY-o-o/FreshHarvestBox",
    description: "Responsive subscription landing page and ordering grid for fresh organic agricultural product delivery.",
    language: "CSS",
    stargazers_count: 0,
    forks_count: 0,
    homepage: null,
    pushed_at: "2026-06-04T18:06:22Z"
  },
  {
    id: 1037874453,
    name: "DictionariesApp",
    html_url: "https://github.com/MY-o-o/DictionariesApp",
    description: "Desktop viewer app implementing local word indexing, keyword dictionary searches, and database schema mappings.",
    language: "C#",
    stargazers_count: 0,
    forks_count: 0,
    homepage: null,
    pushed_at: "2026-06-04T18:21:03Z"
  },
  {
    id: 1038557224,
    name: "WpfAppCalculator",
    html_url: "https://github.com/MY-o-o/WpfAppCalculator",
    description: "Interactive desktop calculator utility written using Windows Presentation Foundation (WPF) with full operational bindings.",
    language: "C#",
    stargazers_count: 0,
    forks_count: 0,
    homepage: null,
    pushed_at: "2026-06-04T18:20:21Z"
  },
  {
    id: 1038620051,
    name: "QuizApp",
    html_url: "https://github.com/MY-o-o/QuizApp",
    description: "Interactive multi-choice evaluation testing application utilizing C# backend algorithms.",
    language: "C#",
    stargazers_count: 0,
    forks_count: 0,
    homepage: null,
    pushed_at: "2026-06-04T18:10:15Z"
  },
  {
    id: 1038586237,
    name: "UniversityDbEditor",
    html_url: "https://github.com/MY-o-o/UniversityDbEditor",
    description: "C# desktop administration dashboard tool for inserting, modifying, and tracking university courses and enrollment tables.",
    language: "C#",
    stargazers_count: 0,
    forks_count: 0,
    homepage: null,
    pushed_at: "2026-06-04T18:10:56Z"
  }
];

const FALLBACK_EVENTS = [
  {
    type: "PushEvent",
    repo: { name: "MY-o-o/RestaurantBooking" },
    payload: { ref: "refs/heads/master" },
    created_at: "2026-06-05T13:50:44Z"
  },
  {
    type: "PushEvent",
    repo: { name: "MY-o-o/RestaurantBooking" },
    payload: { ref: "refs/heads/master" },
    created_at: "2026-06-05T13:38:26Z"
  },
  {
    type: "PushEvent",
    repo: { name: "MY-o-o/RestaurantBooking" },
    payload: { ref: "refs/heads/master" },
    created_at: "2026-06-05T13:22:51Z"
  },
  {
    type: "CreateEvent",
    repo: { name: "MY-o-o/RestaurantBooking" },
    payload: { ref_type: "repository" },
    created_at: "2026-05-23T06:43:50Z"
  }
];

// GitHub API Base URL
const GITHUB_USERNAME = "MY-o-o";
const API_BASE = `https://api.github.com/users/${GITHUB_USERNAME}`;

// ----------------------------------------------------
// DOM Elements Setup
// ----------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initMobileNav();
  setDynamicGreeting();
  loadPortfolioData();
  bindContactForm();
});

// ----------------------------------------------------
// Theme Toggle Logic
// ----------------------------------------------------
function initTheme() {
  const themeToggle = document.getElementById("theme-toggle");
  const storedTheme = localStorage.getItem("portfolio-theme");
  
  // Default is dark mode. If stored theme is light, apply it.
  if (storedTheme === "light") {
    document.body.classList.add("light-theme");
  } else {
    document.body.classList.remove("light-theme");
  }
  
  // Refresh Lucide icons in case theme icon needs redraw
  lucide.createIcons();

  themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("light-theme");
    const activeTheme = document.body.classList.contains("light-theme") ? "light" : "dark";
    localStorage.setItem("portfolio-theme", activeTheme);
    lucide.createIcons();
  });
}

// ----------------------------------------------------
// Mobile Navigation Logic
// ----------------------------------------------------
function initMobileNav() {
  const burgerBtn = document.getElementById("mobile-menu-btn");
  const navLinks = document.getElementById("nav-links");

  burgerBtn.addEventListener("click", () => {
    navLinks.classList.toggle("active");
    // Change menu icon from burger to close icon
    const icon = burgerBtn.querySelector("i");
    if (navLinks.classList.contains("active")) {
      icon.setAttribute("data-lucide", "x");
    } else {
      icon.setAttribute("data-lucide", "menu");
    }
    lucide.createIcons();
  });

  // Close nav menu when links are clicked on mobile
  navLinks.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", () => {
      navLinks.classList.remove("active");
      const icon = burgerBtn.querySelector("i");
      icon.setAttribute("data-lucide", "menu");
      lucide.createIcons();
    });
  });
}

// ----------------------------------------------------
// Greeting Logic Based on Time of Day
// ----------------------------------------------------
function setDynamicGreeting() {
  const greetingEl = document.getElementById("hero-greeting");
  const currentHour = new Date().getHours();
  let text = "👋 Hello World, I'm";

  if (currentHour < 12) {
    text = "🌅 Good Morning, I'm";
  } else if (currentHour < 18) {
    text = "☀️ Good Afternoon, I'm";
  } else {
    text = "🌌 Good Evening, I'm";
  }

  greetingEl.innerHTML = text;
}

// ----------------------------------------------------
// Portfolio Data Initialization & Fetch
// ----------------------------------------------------
async function loadPortfolioData() {
  let cacheUsed = false;
  
  // 1. Fetch Profile Info
  let profile = FALLBACK_PROFILE;
  try {
    const profileRes = await fetch(API_BASE);
    if (profileRes.ok) {
      profile = await profileRes.json();
    } else {
      cacheUsed = true;
      if (profileRes.status === 403) console.warn("Rate limited! Using cache.");
    }
  } catch (err) {
    cacheUsed = true;
    console.error("Failed to fetch profile: ", err);
  }
  renderProfile(profile);

  // 2. Fetch Repositories
  let repos = FALLBACK_REPOS;
  try {
    const reposRes = await fetch(`${API_BASE}/repos`);
    if (reposRes.ok) {
      repos = await reposRes.json();
    } else {
      cacheUsed = true;
    }
  } catch (err) {
    cacheUsed = true;
    console.error("Failed to fetch repos: ", err);
  }
  renderReposAndLanguages(repos);

  // 3. Fetch Events / Activities
  let events = FALLBACK_EVENTS;
  try {
    const eventsRes = await fetch(`${API_BASE}/events`);
    if (eventsRes.ok) {
      events = await eventsRes.json();
    } else {
      cacheUsed = true;
    }
  } catch (err) {
    cacheUsed = true;
    console.error("Failed to fetch events: ", err);
  }
  renderTimeline(events);

  // Show cache banner warning if fallback was used
  if (cacheUsed) {
    document.getElementById("cache-banner").classList.add("visible");
  }
}

// ----------------------------------------------------
// Render Profile Info
// ----------------------------------------------------
function renderProfile(profile) {
  document.getElementById("hero-name").textContent = profile.name || profile.login;
  
  if (profile.bio) {
    document.getElementById("hero-bio").textContent = profile.bio;
  }
  
  // Set avatar image
  const avatarEl = document.getElementById("hero-avatar");
  avatarEl.src = profile.avatar_url;
  avatarEl.alt = `${profile.name || profile.login}'s GitHub Avatar`;
  
  // Quick stats values
  document.getElementById("stat-repos").textContent = profile.public_repos;
  document.getElementById("stat-followers").textContent = profile.followers;
  document.getElementById("stat-gists").textContent = profile.public_gists || 0;

  // Dynamically map mailto email address if available
  if (profile.email) {
    const contactEmailEl = document.getElementById("contact-email");
    if (contactEmailEl) {
      contactEmailEl.href = `mailto:${profile.email}`;
    }
  }
}

// ----------------------------------------------------
// Render Repos & Compute Languages
// ----------------------------------------------------
function renderReposAndLanguages(repos) {
  const projectsGrid = document.getElementById("projects-grid");
  const languageList = document.getElementById("language-list");
  
  projectsGrid.innerHTML = ""; // Clear skeletons
  languageList.innerHTML = "";

  // Sort repos by pushed date (most recent first)
  repos.sort((a, b) => new Date(b.pushed_at) - new Date(a.pushed_at));

  // Tally Languages
  const languagesCount = {};
  let validLangReposCount = 0;

  repos.forEach(repo => {
    // Generate individual project card
    const card = document.createElement("div");
    card.className = "project-card";

    // Set Language details
    const lang = repo.language || "Other";
    if (repo.language) {
      languagesCount[repo.language] = (languagesCount[repo.language] || 0) + 1;
      validLangReposCount++;
    }

    // Language dot color mapping
    let langDotColor = "#94a3b8"; // Default slate
    if (lang === "C#") langDotColor = "#178600";
    else if (lang === "Python") langDotColor = "#3572A5";
    else if (lang === "JavaScript") langDotColor = "#f1e05a";
    else if (lang === "CSS") langDotColor = "#563d7c";
    else if (lang === "HTML") langDotColor = "#e34c26";

    // Assign appropriate Lucide icon based on language/type
    let folderIcon = "folder";
    if (lang === "C#") folderIcon = "cpu";
    else if (lang === "Python") folderIcon = "terminal";
    else if (lang === "CSS" || lang === "HTML") folderIcon = "layout";
    else if (lang === "JavaScript") folderIcon = "code-2";

    // Build Project description fallback
    const description = repo.description || "No project description provided. View files on GitHub to inspect coding layout.";

    card.innerHTML = `
      <div class="project-header">
        <div class="project-folder-icon">
          <i data-lucide="${folderIcon}"></i>
        </div>
        <div class="project-links">
          <a href="${repo.html_url}" target="_blank" rel="noopener" class="project-link" aria-label="GitHub Repository">
            <i data-lucide="github"></i>
          </a>
          ${repo.homepage ? `
            <a href="${repo.homepage}" target="_blank" rel="noopener" class="project-link" aria-label="Live Website Preview">
              <i data-lucide="external-link"></i>
            </a>
          ` : ""}
        </div>
      </div>
      <h3 class="project-title">${repo.name}</h3>
      <p class="project-desc">${description}</p>
      <div class="project-footer">
        <div class="project-lang">
          <span class="project-lang-dot" style="background-color: ${langDotColor};"></span>
          <span>${lang}</span>
        </div>
        <div class="project-stats">
          <div class="project-stat" title="Stars">
            <i data-lucide="star" style="width: 13px; height: 13px;"></i>
            <span>${repo.stargazers_count}</span>
          </div>
          <div class="project-stat" title="Forks">
            <i data-lucide="git-fork" style="width: 13px; height: 13px;"></i>
            <span>${repo.forks_count}</span>
          </div>
        </div>
      </div>
    `;

    projectsGrid.appendChild(card);
  });

  // Re-run Lucide on new cards
  lucide.createIcons();

  // Draw Languages tally panels
  const langSorted = Object.entries(languagesCount).sort((a, b) => b[1] - a[1]);
  if (langSorted.length === 0) {
    languageList.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem;">No languages detected from repositories.</p>`;
  } else {
    langSorted.forEach(([name, count]) => {
      const percentage = Math.round((count / validLangReposCount) * 100);
      
      const item = document.createElement("div");
      item.className = "language-item";
      item.innerHTML = `
        <div class="language-info">
          <span class="language-name">${name}</span>
          <span>${percentage}%</span>
        </div>
        <div class="language-bar-track">
          <div class="language-bar-fill" style="width: 0%;"></div>
        </div>
      `;
      languageList.appendChild(item);

      // Trigger width fill with delay to animate smoothly
      setTimeout(() => {
        const fillBar = item.querySelector(".language-bar-fill");
        if (fillBar) fillBar.style.width = `${percentage}%`;
      }, 150);
    });
  }
}

// ----------------------------------------------------
// Render Recent Activity Timeline Log
// ----------------------------------------------------
function renderTimeline(events) {
  const timeline = document.getElementById("timeline");
  timeline.innerHTML = ""; // Clear skeletons

  // Filter for key public interactions, capping at 4 items
  const filteredEvents = events
    .filter(e => ["PushEvent", "CreateEvent", "WatchEvent", "IssuesEvent", "ForkEvent"].includes(e.type))
    .slice(0, 4);

  if (filteredEvents.length === 0) {
    timeline.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem; padding-left: 0.5rem;">No recent public activities logged.</p>`;
    return;
  }

  filteredEvents.forEach(evt => {
    const item = document.createElement("div");
    item.className = "timeline-item";

    const date = formatDate(evt.created_at);
    let title = "Repository interaction";
    let desc = `Engaged with repository at ${evt.repo.name}`;

    if (evt.type === "PushEvent") {
      const commitCount = evt.payload && evt.payload.commits ? evt.payload.commits.length : 1;
      const refName = evt.payload && evt.payload.ref ? evt.payload.ref.replace("refs/heads/", "") : "main";
      title = `Pushed ${commitCount} Commit${commitCount > 1 ? 's' : ''}`;
      desc = `Pushed to branch <code>${refName}</code> of repository <a href="https://github.com/${evt.repo.name}" target="_blank" rel="noopener">${evt.repo.name}</a>`;
    } else if (evt.type === "CreateEvent") {
      const refType = evt.payload && evt.payload.ref_type ? evt.payload.ref_type : "repository";
      title = `Created ${refType.charAt(0).toUpperCase() + refType.slice(1)}`;
      desc = `Created new branch/repo resources in <a href="https://github.com/${evt.repo.name}" target="_blank" rel="noopener">${evt.repo.name}</a>`;
    } else if (evt.type === "WatchEvent") {
      title = "Starred Repository";
      desc = `Added star status to <a href="https://github.com/${evt.repo.name}" target="_blank" rel="noopener">${evt.repo.name}</a>`;
    } else if (evt.type === "ForkEvent") {
      title = "Forked Repository";
      desc = `Forked repository <a href="https://github.com/${evt.repo.name}" target="_blank" rel="noopener">${evt.repo.name}</a>`;
    }

    item.innerHTML = `
      <div class="timeline-date">${date}</div>
      <div class="timeline-title">${title}</div>
      <div class="timeline-desc">${desc}</div>
    `;

    timeline.appendChild(item);
  });
}

// Format Date string helper
function formatDate(dateStr) {
  const opt = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute:'2-digit' };
  return new Date(dateStr).toLocaleDateString(undefined, opt);
}

// ----------------------------------------------------
// Contact Form Submission
// ----------------------------------------------------
function bindContactForm() {
  const form = document.getElementById("contact-form");
  const toast = document.getElementById("toast");

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    // Fetch values
    const name = document.getElementById("form-name").value;
    const email = document.getElementById("form-email").value;
    const message = document.getElementById("form-message").value;

    console.log(`[Form Submitted] Name: ${name}, Email: ${email}, Message: ${message}`);

    // Change button to sending state
    const submitBtn = form.querySelector("button[type='submit']");
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = `<span class="skeleton" style="width: 20px; height: 20px; display: inline-block; border-radius: 50%; vertical-align: middle; margin-right: 8px;"></span> Sending...`;
    submitBtn.disabled = true;

    // Simulate Server request delay
    setTimeout(() => {
      // Show Toast Notification
      toast.classList.add("show");

      // Reset form controls
      form.reset();
      submitBtn.innerHTML = originalText;
      submitBtn.disabled = false;

      // Hide toast after 4 seconds
      setTimeout(() => {
        toast.classList.remove("show");
      }, 4000);
    }, 1200);
  });
}
