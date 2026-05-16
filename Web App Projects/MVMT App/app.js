const storageKey = "mvmt-state-v1";

const classData = [
  {
    id: "cls-1",
    title: "Sunrise House Foundation",
    studio: "Northside Loft • 1.2 mi",
    level: "Beginner",
    cost: 24,
    length: 60,
    distance: 1.2,
    format: "In person",
    tags: ["House", "Morning"],
    instructor: "Nia Summers",
    seats: 12,
  },
  {
    id: "cls-2",
    title: "Afro Fusion Lab",
    studio: "Pulse Studio • 2.8 mi",
    level: "Intermediate",
    cost: 38,
    length: 75,
    distance: 2.8,
    format: "Hybrid",
    tags: ["Afro", "Cardio"],
    instructor: "Darren Cole",
    seats: 14,
  },
  {
    id: "cls-3",
    title: "Heels Choreo Intensive",
    studio: "Velvet Room • 4.1 mi",
    level: "Advanced",
    cost: 52,
    length: 90,
    distance: 4.1,
    format: "In person",
    tags: ["Heels", "Performance"],
    instructor: "Mina Ortega",
    seats: 10,
  },
  {
    id: "cls-4",
    title: "Contemporary Flow",
    studio: "Glass Hall • 0.9 mi",
    level: "All levels",
    cost: 30,
    length: 60,
    distance: 0.9,
    format: "Online",
    tags: ["Contemporary", "Floorwork"],
    instructor: "Lina Park",
    seats: 16,
  },
  {
    id: "cls-5",
    title: "Jazz Funk Sprint",
    studio: "Uptown Works • 3.6 mi",
    level: "Intermediate",
    cost: 28,
    length: 45,
    distance: 3.6,
    format: "In person",
    tags: ["Jazz Funk", "Fast pace"],
    instructor: "Avery Stone",
    seats: 18,
  },
  {
    id: "cls-6",
    title: "K-pop Performance Team",
    studio: "Beat House • 5.0 mi",
    level: "Beginner",
    cost: 22,
    length: 60,
    distance: 5.0,
    format: "Hybrid",
    tags: ["K-pop", "Team"],
    instructor: "Jae Kim",
    seats: 20,
  },
];

const gigData = [
  {
    id: "gig-1",
    title: "Music video backup dancers",
    location: "Downtown warehouse shoot",
    type: "Commercial",
    pay: "$350/day",
    copy: "Looking for dancers with strong musicality, sharp lines, and availability this weekend.",
    deadline: "Apply by Fri 6pm",
  },
  {
    id: "gig-2",
    title: "Brand launch performance",
    location: "Riverside event hall",
    type: "Event",
    pay: "$600 flat",
    copy: "Live performance set for a product launch with a polished street-meets-jazz aesthetic.",
    deadline: "Apply by Thu 11am",
  },
  {
    id: "gig-3",
    title: "Tour rehearsal swing-in",
    location: "North rehearsal campus",
    type: "Tour",
    pay: "$45/hr",
    copy: "Short-term rehearsal cover needed for an established touring company.",
    deadline: "Apply by Mon 9am",
  },
];

const instructorData = [
  {
    id: "inst-1",
    name: "Lola Lace",
    specialty: "Burlesque",
    copy: "10 years of choreography experience. Teaches classes rooted in dramatic flair and stage presence.",
    credit: "10+ years of teaching",
  },
  {
    id: "inst-2",
    name: "Rodrigo & Yari",
    specialty: "Salsa",
    copy: "Learn bachata and salsa from an international duo with polished social dance technique.",
    credit: "International acclaim",
  },
  {
    id: "inst-3",
    name: "Tony Rivera",
    specialty: "Hip Hop",
    copy: "Breakdown-focused classes that build confidence, musicality, and freestyle control.",
    credit: "Commercial and tour work",
  },
  {
    id: "inst-4",
    name: "Kira Yang",
    specialty: "Ballet",
    copy: "Intermediate ballet teacher with 12 years of classical experience and performance credits.",
    credit: "12 years of experience",
  },
];

const initialState = {
  role: null,
  name: "",
  view: "home",
  filters: {
    query: "",
    radius: 5,
    level: "All levels",
    cost: 60,
    length: "Any",
    onlineOnly: false,
  },
  bookings: [
    {
      title: "Booked: Contemporary Flow",
      meta: "Tomorrow at 6:30 PM · Glass Hall",
    },
    {
      title: "Applied: Brand launch performance",
      meta: "Awaiting review · Riverside event hall",
    },
  ],
  videos: [
    { name: "stage-combo-reel.mov", meta: "Uploaded today · 1.8 GB" },
    { name: "rehearsal-snippet.mp4", meta: "Uploaded yesterday · 320 MB" },
  ],
  savedClasses: ["cls-4"],
  instructorClasses: 2,
};

const testimonialData = [
  {
    quote: "I found my weekly groove in two days. The class filters are spot on.",
    name: "Camille R.",
    detail: "Beginner dancer",
  },
  {
    quote: "Booked a last-minute class and left with a new crew to train with.",
    name: "Jordan T.",
    detail: "Hip hop student",
  },
  {
    quote: "As an instructor, I filled my weekend workshop faster than expected.",
    name: "Mina O.",
    detail: "Guest instructor",
  },
];

let testimonialRotationId = null;

const dom = {
  nav: document.getElementById("primary-nav"),
  signupForm: document.getElementById("signup-form"),
  homeSearchForm: document.getElementById("home-search-form"),
  homeSearchInput: document.getElementById("home-search-input"),
  views: Array.from(document.querySelectorAll(".view")),
  navTabs: Array.from(document.querySelectorAll(".nav-tab")),
  heroMetrics: document.getElementById("hero-metrics"),
  featuredClasses: document.getElementById("featured-classes"),
  featuredInstructors: document.getElementById("featured-instructors"),
  searchInput: document.getElementById("search-input"),
  radiusSelect: document.getElementById("radius-select"),
  levelSelect: document.getElementById("level-select"),
  costInput: document.getElementById("cost-input"),
  costValue: document.getElementById("cost-value"),
  lengthSelect: document.getElementById("length-select"),
  onlineOnly: document.getElementById("online-only"),
  resetFilters: document.getElementById("reset-filters"),
  classResults: document.getElementById("class-results"),
  resultsCount: document.getElementById("results-count"),
  resultsTags: document.getElementById("results-tags"),
  activeFilterPills: document.getElementById("active-filter-pills"),
  gigList: document.getElementById("gig-list"),
  gigApplyForm: document.getElementById("gig-apply-form"),
  gigToast: document.getElementById("gig-toast"),
  bookedCount: document.getElementById("booked-count"),
  videoCount: document.getElementById("video-count"),
  instructorCount: document.getElementById("instructor-count"),
  profileLabel: document.getElementById("profile-label"),
  profileHeading: document.getElementById("profile-heading"),
  profileStats: document.getElementById("profile-stats"),
  profileActions: document.getElementById("profile-actions"),
  instructorStats: document.getElementById("instructor-stats"),
  bookingList: document.getElementById("booking-list"),
  videoUpload: document.getElementById("video-upload"),
  videoList: document.getElementById("video-list"),
  classUploadForm: document.getElementById("class-upload-form"),
  uploadLevel: document.getElementById("upload-level"),
  uploadLength: document.getElementById("upload-length"),
};

const classCardTemplate = document.getElementById("class-card-template");
const gigCardTemplate = document.getElementById("gig-card-template");
const homeClassCardTemplate = document.getElementById("home-class-card-template");
const instructorCardTemplate = document.getElementById("instructor-card-template");
const videoItemTemplate = document.getElementById("video-item-template");

const loadState = () => {
  try {
    const stored = JSON.parse(localStorage.getItem(storageKey));
    if (!stored) return structuredClone(initialState);
    return {
      ...structuredClone(initialState),
      ...stored,
      filters: { ...initialState.filters, ...(stored.filters || {}) },
    };
  } catch {
    return structuredClone(initialState);
  }
};

const state = loadState();

function saveState() {
  localStorage.setItem(storageKey, JSON.stringify({
    role: state.role,
    name: state.name,
    view: state.view,
    filters: state.filters,
    bookings: state.bookings,
    videos: state.videos,
    savedClasses: state.savedClasses,
    instructorClasses: state.instructorClasses,
  }));
}

function formatCost(value) {
  return `$${value}`;
}

function isInstructor() {
  return state.role === "instructor";
}

function hasRole() {
  return Boolean(state.role);
}

function applyRoleVisibility() {
  if (dom.nav) {
    dom.nav.classList.remove("nav-hidden");
  }

  const showInstructorView = isInstructor();
  const instructorView = document.getElementById("view-instructor");
  if (instructorView) {
    instructorView.classList.toggle("hidden", !showInstructorView);
  }

  if (dom.profileLabel && dom.profileHeading) {
    dom.profileLabel.textContent = isInstructor() ? "Instructor profile" : "Dancer profile";
    dom.profileHeading.textContent = isInstructor()
      ? "Manage your bookings, videos, and class listings."
      : "Manage your bookings and upload videos.";
  }
}

function setView(view) {
  if (view === "profile") {
    if (!hasRole()) {
      window.location.href = "signup.html";
      return;
    }
    window.location.href = "profile.html";
    return;
  }
  if (view === "gigs") {
    window.location.href = "gigs.html";
    return;
  }
  if (view === "instructor") {
    if (!hasRole()) {
      window.location.href = "signup.html";
      return;
    }
    if (!isInstructor()) {
      window.location.href = "profile.html";
      return;
    }
    window.location.href = "instructor.html";
    return;
  }
  if (view === "signup") {
    window.location.href = "signup.html";
    return;
  }
  if (!hasRole() && (view === "profile" || view === "instructor")) {
    view = "signup";
  }
  if (view === "instructor" && !isInstructor()) {
    view = "profile";
  }
  state.view = view;
  document.body.dataset.view = view;
  dom.navTabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.view === view));
  dom.views.forEach((panel) => panel.classList.toggle("active", panel.id === `view-${view}`));
  applyRoleVisibility();
  saveState();
}

function populateSelectors() {
  if (!dom.levelSelect || !dom.uploadLevel || !dom.lengthSelect || !dom.uploadLength || !dom.radiusSelect) {
    return;
  }

  const levels = ["All levels", "Beginner", "Intermediate", "Advanced"];
  const lengths = ["Any", "45 min", "60 min", "75 min", "90 min"];
  const uploadLengths = [45, 60, 75, 90];
  const radius = [1, 2, 3, 5, 10];

  dom.levelSelect.innerHTML = levels.map((level) => `<option value="${level}">${level}</option>`).join("");
  dom.uploadLevel.innerHTML = levels.filter((level) => level !== "All levels").map((level) => `<option value="${level}">${level}</option>`).join("");
  dom.lengthSelect.innerHTML = lengths.map((length) => `<option value="${length}">${length}</option>`).join("");
  dom.uploadLength.innerHTML = uploadLengths.map((length) => `<option value="${length}">${length} min</option>`).join("");
  dom.radiusSelect.innerHTML = radius.map((distance) => `<option value="${distance}">${distance} mi</option>`).join("");

  dom.searchInput.value = state.filters.query;
  dom.radiusSelect.value = String(state.filters.radius);
  dom.levelSelect.value = state.filters.level;
  dom.costInput.value = String(state.filters.cost);
  dom.costValue.textContent = formatCost(state.filters.cost);
  dom.lengthSelect.value = state.filters.length;
  dom.onlineOnly.checked = state.filters.onlineOnly;
}

function getFilteredClasses() {
  const { query, radius, level, cost, length, onlineOnly } = state.filters;
  const search = query.trim().toLowerCase();

  return classData.filter((item) => {
    const matchesSearch = !search || [item.title, item.studio, item.tags.join(" "), item.instructor].join(" ").toLowerCase().includes(search);
    const matchesRadius = item.distance <= radius;
    const matchesLevel = level === "All levels" || item.level === level;
    const matchesCost = item.cost <= cost;
    const matchesLength = length === "Any" || `${item.length} min` === length;
    const matchesFormat = !onlineOnly || item.format !== "In person";
    return matchesSearch && matchesRadius && matchesLevel && matchesCost && matchesLength && matchesFormat;
  });
}

function renderClassCard(item) {
  const node = classCardTemplate.content.cloneNode(true);
  node.querySelector(".distance").textContent = `${item.distance.toFixed(1)} mi away`;
  node.querySelector(".title").textContent = item.title;
  node.querySelector(".level").textContent = item.level;
  node.querySelector(".studio").textContent = `${item.instructor} · ${item.studio.replace(/ • .+$/, "")}`;

  const meta = node.querySelector(".result-meta");
  const metaValues = [
    `${formatCost(item.cost)} per class`,
    `${item.length} min`,
    item.format,
    `${item.seats} seats`,
  ];
  meta.innerHTML = metaValues.map((value) => `<span class="meta-pill">${value}</span>`).join("");

  const bookButton = node.querySelector(".book-button");
  const saveButton = node.querySelector(".save-button");
  bookButton.textContent = state.bookings.some((entry) => entry.title.includes(item.title)) ? "Booked" : "Book class";
  bookButton.disabled = state.bookings.some((entry) => entry.title.includes(item.title));
  saveButton.textContent = state.savedClasses.includes(item.id) ? "Saved" : "Save";

  bookButton.addEventListener("click", () => {
    state.bookings.unshift({
      title: `Booked: ${item.title}`,
      meta: `${item.studio.replace(/ • .+$/, "")} · ${item.length} min · ${item.level}`,
    });
    saveState();
    renderAll();
    setView("profile");
  });

  saveButton.addEventListener("click", () => {
    if (state.savedClasses.includes(item.id)) {
      state.savedClasses = state.savedClasses.filter((id) => id !== item.id);
      saveButton.textContent = "Save";
    } else {
      state.savedClasses.unshift(item.id);
      saveButton.textContent = "Saved";
    }
    saveState();
    renderProfileSummary();
  });

  return node;
}

function renderHomeClassCard(item, index) {
  const node = homeClassCardTemplate.content.cloneNode(true);
  const thumb = node.querySelector(".feature-thumb");
  const art = [
    "linear-gradient(135deg, rgba(255, 83, 133, 0.95), rgba(31, 21, 52, 0.92))",
    "linear-gradient(135deg, rgba(75, 160, 255, 0.92), rgba(10, 10, 10, 0.96))",
    "linear-gradient(135deg, rgba(240, 152, 94, 0.96), rgba(22, 22, 22, 0.95))",
    "linear-gradient(135deg, rgba(165, 111, 255, 0.94), rgba(18, 18, 18, 0.96))",
  ][index % 4];
  thumb.style.background = art;
  node.querySelector(".feature-type").textContent = `${item.level} · ${item.length} min`;
  node.querySelector(".feature-title").textContent = item.title;
  node.querySelector(".feature-copy").textContent = `${item.instructor} · ${item.studio.replace(/ • .+$/, "")}`;
  node.querySelector(".feature-meta").textContent = `${formatCost(item.cost)} · ${item.format}`;

  node.querySelector(".feature-button").addEventListener("click", () => {
    state.filters.query = item.title;
    dom.searchInput.value = item.title;
    saveState();
    renderClassResults();
    setView("classes");
  });

  return node;
}

function renderInstructorCard(item, index) {
  const node = instructorCardTemplate.content.cloneNode(true);
  const thumb = node.querySelector(".instructor-thumb");
  const art = [
    "linear-gradient(135deg, rgba(255, 196, 102, 0.96), rgba(25, 16, 16, 0.94))",
    "linear-gradient(135deg, rgba(242, 104, 173, 0.94), rgba(16, 16, 16, 0.94))",
    "linear-gradient(135deg, rgba(73, 182, 164, 0.96), rgba(15, 15, 15, 0.94))",
    "linear-gradient(135deg, rgba(155, 123, 255, 0.94), rgba(15, 15, 15, 0.94))",
  ][index % 4];
  thumb.style.background = art;
  node.querySelector(".feature-type").textContent = item.specialty;
  node.querySelector(".feature-title").textContent = item.name;
  node.querySelector(".feature-copy").textContent = item.copy;
  node.querySelector(".feature-meta").textContent = item.credit;

  node.querySelector(".feature-button").addEventListener("click", () => {
    setView(hasRole() ? "profile" : "signup");
  });

  return node;
}

function renderGigCard(item) {
  const node = gigCardTemplate.content.cloneNode(true);
  node.querySelector(".project-type").textContent = item.type;
  node.querySelector(".title").textContent = item.title;
  node.querySelector(".pay").textContent = item.pay;
  node.querySelector(".gig-location").textContent = item.location;
  node.querySelector(".gig-copy").textContent = item.copy;
  node.querySelector(".deadline").textContent = item.deadline;

  node.querySelector(".apply-button").addEventListener("click", () => {
    state.bookings.unshift({
      title: `Applied: ${item.title}`,
      meta: `${item.location} · ${item.pay}`,
    });
    saveState();
    renderAll();
    setView("profile");
  });

  return node;
}

function renderHeroTestimonials() {
  if (!dom.heroMetrics) {
    return;
  }

  dom.heroMetrics.innerHTML = `
    <section class="testimonial-carousel" aria-label="Member testimonials">
      <div class="testimonial-track">
        ${testimonialData.map((item, index) => `
          <article class="testimonial-slide${index === 0 ? " is-active" : ""}" data-index="${index}">
            <p class="testimonial-quote">"${item.quote}"</p>
            <p class="testimonial-author">${item.name}</p>
            <p class="testimonial-role">${item.detail}</p>
          </article>
        `).join("")}
      </div>
      <div class="testimonial-controls">
        <button class="testimonial-nav" type="button" data-action="prev" aria-label="Previous testimonial">&larr;</button>
        <div class="testimonial-dots" role="tablist" aria-label="Testimonial slides">
          ${testimonialData.map((_, index) => `
            <button class="testimonial-dot${index === 0 ? " is-active" : ""}" type="button" role="tab" data-index="${index}" aria-label="Show testimonial ${index + 1}" aria-selected="${index === 0 ? "true" : "false"}"></button>
          `).join("")}
        </div>
        <button class="testimonial-nav" type="button" data-action="next" aria-label="Next testimonial">&rarr;</button>
      </div>
    </section>
  `;

  const track = dom.heroMetrics.querySelector(".testimonial-track");
  const slides = Array.from(dom.heroMetrics.querySelectorAll(".testimonial-slide"));
  const dots = Array.from(dom.heroMetrics.querySelectorAll(".testimonial-dot"));
  const previousButton = dom.heroMetrics.querySelector('[data-action="prev"]');
  const nextButton = dom.heroMetrics.querySelector('[data-action="next"]');
  let activeIndex = 0;

  const setActiveSlide = (nextIndex) => {
    activeIndex = (nextIndex + slides.length) % slides.length;
    if (track) {
      track.style.transform = `translateX(-${activeIndex * 100}%)`;
    }
    slides.forEach((slide, index) => {
      const isActive = index === activeIndex;
      slide.classList.toggle("is-active", isActive);
    });
    dots.forEach((dot, index) => {
      const isActive = index === activeIndex;
      dot.classList.toggle("is-active", isActive);
      dot.setAttribute("aria-selected", isActive ? "true" : "false");
    });
  };

  const startRotation = () => {
    if (testimonialRotationId) {
      clearInterval(testimonialRotationId);
    }
    testimonialRotationId = setInterval(() => {
      setActiveSlide(activeIndex + 1);
    }, 5500);
  };

  previousButton?.addEventListener("click", () => {
    setActiveSlide(activeIndex - 1);
    startRotation();
  });

  nextButton?.addEventListener("click", () => {
    setActiveSlide(activeIndex + 1);
    startRotation();
  });

  dots.forEach((dot) => {
    dot.addEventListener("click", () => {
      setActiveSlide(Number(dot.dataset.index));
      startRotation();
    });
  });

  dom.heroMetrics.addEventListener("mouseenter", () => {
    if (testimonialRotationId) {
      clearInterval(testimonialRotationId);
      testimonialRotationId = null;
    }
  });

  dom.heroMetrics.addEventListener("mouseleave", () => {
    startRotation();
  });

  setActiveSlide(0);
  startRotation();
}

function renderFeatured() {
  const featured = classData.slice(0, 4);
  dom.featuredClasses.innerHTML = "";
  featured.forEach((item, index) => dom.featuredClasses.appendChild(renderHomeClassCard(item, index)));

  dom.featuredInstructors.innerHTML = "";
  instructorData.forEach((item, index) => dom.featuredInstructors.appendChild(renderInstructorCard(item, index)));

  renderHeroTestimonials();
}

function renderClassResults() {
  const filtered = getFilteredClasses();
  dom.classResults.innerHTML = "";
  dom.resultsCount.textContent = `${filtered.length} class${filtered.length === 1 ? "" : "es"} match your filters`;

  dom.resultsTags.innerHTML = [
    state.filters.radius !== 5 ? `${state.filters.radius} mi radius` : null,
    state.filters.level !== "All levels" ? state.filters.level : null,
    state.filters.length !== "Any" ? state.filters.length : null,
    state.filters.onlineOnly ? "online only" : null,
  ].filter(Boolean).map((value) => `<span class="pill">${value}</span>`).join("") || `<span class="pill">All defaults</span>`;

  dom.activeFilterPills.innerHTML = [
    `Search: ${state.filters.query || "any"}`,
    `Radius: ${state.filters.radius} mi` ,
    `Level: ${state.filters.level}`,
    `Max cost: ${formatCost(state.filters.cost)}`,
    `Length: ${state.filters.length}`,
  ].map((value) => `<span class="pill">${value}</span>`).join("");

  if (!filtered.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "No classes matched. Loosen the filters or widen the radius.";
    dom.classResults.appendChild(empty);
    return;
  }

  filtered.forEach((item) => dom.classResults.appendChild(renderClassCard(item)));
}

function renderGigList() {
  if (!dom.gigList || !gigCardTemplate) {
    return;
  }

  dom.gigList.innerHTML = "";
  gigData.forEach((item) => dom.gigList.appendChild(renderGigCard(item)));
}

function renderProfileSummary() {
  if (!dom.bookedCount || !dom.videoCount || !dom.instructorCount || !dom.profileStats || !dom.bookingList || !dom.videoList || !videoItemTemplate) {
    return;
  }

  dom.bookedCount.textContent = String(state.bookings.filter((entry) => entry.title.startsWith("Booked:")).length);
  dom.videoCount.textContent = String(state.videos.length);
  dom.instructorCount.textContent = String(state.instructorClasses);

  dom.profileStats.innerHTML = [
    { label: "Saved classes", value: String(state.savedClasses.length) },
    { label: "Bookings", value: String(state.bookings.length) },
    { label: "Preferred radius", value: `${state.filters.radius} mi` },
    { label: "Skill level", value: state.filters.level },
  ].map((item) => `<div class="detail"><strong>${item.value}</strong><span>${item.label}</span></div>`).join("");

  if (dom.profileActions) {
    dom.profileActions.innerHTML = isInstructor()
      ? '<button class="secondary-button full-width" id="open-instructor-dashboard" type="button">Open instructor dashboard</button>'
      : '<p class="support-copy">Your dancer profile keeps bookings and videos in one place.</p>';
    const openInstructorDashboard = document.getElementById("open-instructor-dashboard");
    if (openInstructorDashboard) {
      openInstructorDashboard.addEventListener("click", () => setView("instructor"));
    }
  }

  dom.bookingList.innerHTML = "";
  state.bookings.forEach((entry) => {
    const row = document.createElement("div");
    row.className = "timeline-item";
    row.innerHTML = `<div><strong>${entry.title}</strong><p>${entry.meta}</p></div><span class="chip soft">Active</span>`;
    dom.bookingList.appendChild(row);
  });

  if (!state.bookings.length) {
    dom.bookingList.innerHTML = '<div class="empty-state">Your bookings and applications will appear here.</div>';
  }

  dom.videoList.innerHTML = "";
  state.videos.forEach((video) => {
    const node = videoItemTemplate.content.cloneNode(true);
    node.querySelector(".video-name").textContent = video.name;
    node.querySelector(".video-meta").textContent = video.meta;
    dom.videoList.appendChild(node);
  });

  if (!state.videos.length) {
    dom.videoList.innerHTML = '<div class="empty-state">Upload a video to build out your profile.</div>';
  }

  if (dom.instructorStats) {
    dom.instructorStats.innerHTML = [
      { label: "Account type", value: isInstructor() ? "Instructor" : "Dancer" },
      { label: "Published classes", value: String(state.instructorClasses) },
      { label: "Access", value: isInstructor() ? "Class publishing enabled" : "Publishing locked" },
      { label: "Saved classes", value: String(state.savedClasses.length) },
    ].map((item) => `<div class="detail"><strong>${item.value}</strong><span>${item.label}</span></div>`).join("");
  }
}

function renderAll() {
  renderFeatured();
  renderClassResults();
  renderGigList();
  renderProfileSummary();
  if (dom.costValue) {
    dom.costValue.textContent = formatCost(state.filters.cost);
  }
}

function bindEvents() {
  dom.navTabs.forEach((tab) => {
    if (!tab.dataset.view) return;
    tab.addEventListener("click", () => setView(tab.dataset.view));
  });

  document.querySelectorAll("[data-action='jump']").forEach((button) => {
    button.addEventListener("click", () => setView(button.dataset.target));
    button.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        setView(button.dataset.target);
      }
    });
  });

  if (dom.searchInput) {
    dom.searchInput.addEventListener("input", (event) => {
      state.filters.query = event.target.value;
      saveState();
      renderClassResults();
    });
  }

  if (dom.radiusSelect) {
    dom.radiusSelect.addEventListener("change", (event) => {
      state.filters.radius = Number(event.target.value);
      saveState();
      renderClassResults();
      renderProfileSummary();
    });
  }

  if (dom.levelSelect) {
    dom.levelSelect.addEventListener("change", (event) => {
      state.filters.level = event.target.value;
      saveState();
      renderClassResults();
      renderProfileSummary();
    });
  }

  if (dom.costInput) {
    dom.costInput.addEventListener("input", (event) => {
      state.filters.cost = Number(event.target.value);
      if (dom.costValue) {
        dom.costValue.textContent = formatCost(state.filters.cost);
      }
      saveState();
      renderClassResults();
    });
  }

  if (dom.lengthSelect) {
    dom.lengthSelect.addEventListener("change", (event) => {
      state.filters.length = event.target.value;
      saveState();
      renderClassResults();
    });
  }

  if (dom.onlineOnly) {
    dom.onlineOnly.addEventListener("change", (event) => {
      state.filters.onlineOnly = event.target.checked;
      saveState();
      renderClassResults();
    });
  }

  if (dom.resetFilters) {
    dom.resetFilters.addEventListener("click", () => {
      state.filters = structuredClone(initialState.filters);
      populateSelectors();
      saveState();
      renderAll();
    });
  }

  if (dom.signupForm) {
    dom.signupForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const formData = new FormData(event.currentTarget);
      const email = String(formData.get("email") || "").trim();
      const password = String(formData.get("password") || "");
      const hasStrongPassword = /[A-Z]/.test(password) && /\d/.test(password) && /[^A-Za-z0-9]/.test(password) && password.length >= 8;

      if (!email || !hasStrongPassword) {
        return;
      }

      state.name = String(formData.get("name") || email.split("@")[0] || "");
      state.role = String(formData.get("role") || "dancer");
      if (state.role !== "instructor") {
        state.role = "dancer";
      }
      saveState();
      renderAll();
      setView("home");
    });
  }

  if (dom.gigApplyForm && dom.gigToast) {
    dom.gigApplyForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const formData = new FormData(event.currentTarget);
      const name = String(formData.get("name") || "Someone");
      dom.gigToast.textContent = `Application sent for ${name}. The gig board will move this to your bookings.`;
      event.currentTarget.reset();
      setTimeout(() => {
        dom.gigToast.textContent = "";
      }, 4000);
    });
  }

  if (dom.videoUpload) {
    dom.videoUpload.addEventListener("change", (event) => {
      const files = Array.from(event.target.files || []);
      files.forEach((file) => {
        state.videos.unshift({
          name: file.name,
          meta: `Uploaded now · ${(file.size / (1024 * 1024)).toFixed(1)} MB`,
        });
      });
      event.target.value = "";
      saveState();
      renderProfileSummary();
    });
  }

  if (dom.classUploadForm && dom.uploadLevel && dom.uploadLength) {
    dom.classUploadForm.addEventListener("submit", (event) => {
      if (!isInstructor()) {
        event.preventDefault();
        setView("profile");
        return;
      }
      event.preventDefault();
      const formData = new FormData(event.currentTarget);
      const newClass = {
        id: `user-${Date.now()}`,
        title: String(formData.get("title")),
        studio: `${String(formData.get("studio"))} · ${Number(formData.get("distance")).toFixed(1)} mi`,
        level: String(formData.get("level")),
        cost: Number(formData.get("cost")),
        length: Number(formData.get("length")),
        distance: Number(formData.get("distance")),
        format: "In person",
        tags: ["Instructor upload"],
        instructor: "You",
        seats: 20,
      };

      classData.unshift(newClass);
      state.instructorClasses += 1;
      event.currentTarget.reset();
      dom.uploadLevel.value = "Beginner";
      dom.uploadLength.value = "60";
      saveState();
      renderAll();
      setView("classes");
    });
  }

  dom.homeSearchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const searchValue = String(dom.homeSearchInput.value || "").trim();
    state.filters.query = searchValue;
    dom.searchInput.value = searchValue;
    saveState();
    renderClassResults();
    setView("classes");
  });
}

function hydrateState() {
  if (dom.costInput) dom.costInput.value = String(state.filters.cost);
  if (dom.radiusSelect) dom.radiusSelect.value = String(state.filters.radius);
  if (dom.levelSelect) dom.levelSelect.value = state.filters.level;
  if (dom.lengthSelect) dom.lengthSelect.value = state.filters.length;
  if (dom.onlineOnly) dom.onlineOnly.checked = state.filters.onlineOnly;
  if (dom.searchInput) dom.searchInput.value = state.filters.query;
}

function hydrateSignup() {
  if (!dom.signupForm) return;
  const roleInput = dom.signupForm.querySelector(`input[name="role"][value="${state.role || "dancer"}"]`);
  if (roleInput) roleInput.checked = true;
  const nameInput = dom.signupForm.querySelector('input[name="name"]');
  if (nameInput && state.name) nameInput.value = state.name;
}

populateSelectors();
hydrateState();
hydrateSignup();
bindEvents();
renderAll();
applyRoleVisibility();
setView("home");
