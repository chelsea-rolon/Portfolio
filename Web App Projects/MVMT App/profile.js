const storageKey = "mvmt-state-v1";

function loadState() {
  try {
    return JSON.parse(localStorage.getItem(storageKey)) || {};
  } catch {
    return {};
  }
}

function saveState(state) {
  localStorage.setItem(storageKey, JSON.stringify(state));
}

function wireHomeLink() {
  const homeJump = document.querySelector('[data-action="go-home"]');
  if (!homeJump) return;
  homeJump.addEventListener("click", () => {
    window.location.href = "index.html";
  });
  homeJump.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      window.location.href = "index.html";
    }
  });
}

function renderProfile() {
  const state = loadState();
  if (!state.role) {
    window.location.href = "signup.html";
    return;
  }

  const bookings = Array.isArray(state.bookings) ? state.bookings : [];
  const videos = Array.isArray(state.videos) ? state.videos : [];
  const savedClasses = Array.isArray(state.savedClasses) ? state.savedClasses : [];

  const bookedCount = bookings.filter((entry) => String(entry.title || "").startsWith("Booked:")).length;
  const instructorClasses = Number(state.instructorClasses || 0);

  const bookedCountNode = document.getElementById("booked-count");
  const videoCountNode = document.getElementById("video-count");
  const instructorCountNode = document.getElementById("instructor-count");
  const profileLabel = document.getElementById("profile-label");
  const profileHeading = document.getElementById("profile-heading");
  const profileName = document.getElementById("profile-name");
  const profileStats = document.getElementById("profile-stats");
  const profileActions = document.getElementById("profile-actions");
  const bookingList = document.getElementById("booking-list");
  const videoList = document.getElementById("video-list");
  const videoTemplate = document.getElementById("video-item-template");

  bookedCountNode.textContent = String(bookedCount);
  videoCountNode.textContent = String(videos.length);
  instructorCountNode.textContent = String(instructorClasses);

  profileLabel.textContent = state.role === "instructor" ? "Instructor profile" : "Dancer profile";
  profileHeading.textContent = state.role === "instructor"
    ? "Manage your bookings, videos, and class listings."
    : "Manage your bookings and upload videos.";
  profileName.textContent = state.name || "Maya Vale";

  profileStats.innerHTML = [
    { label: "Saved classes", value: String(savedClasses.length) },
    { label: "Bookings", value: String(bookings.length) },
    { label: "Preferred radius", value: `${Number(state.filters?.radius || 5)} mi` },
    { label: "Skill level", value: String(state.filters?.level || "All levels") },
  ].map((item) => `<div class="detail"><strong>${item.value}</strong><span>${item.label}</span></div>`).join("");

  if (state.role === "instructor") {
    profileActions.innerHTML = '<a class="secondary-button full-width" href="instructor.html">Open instructor dashboard</a>';
  } else {
    profileActions.innerHTML = '<p class="support-copy">Your dancer profile keeps bookings and videos in one place.</p>';
  }

  bookingList.innerHTML = "";
  if (!bookings.length) {
    bookingList.innerHTML = '<div class="empty-state">Your bookings and applications will appear here.</div>';
  } else {
    bookings.forEach((entry) => {
      const row = document.createElement("div");
      row.className = "timeline-item";
      row.innerHTML = `<div><strong>${entry.title || "Untitled"}</strong><p>${entry.meta || ""}</p></div><span class="chip soft">Active</span>`;
      bookingList.appendChild(row);
    });
  }

  videoList.innerHTML = "";
  if (!videos.length) {
    videoList.innerHTML = '<div class="empty-state">Upload a video to build out your profile.</div>';
  } else {
    videos.forEach((video) => {
      const node = videoTemplate.content.cloneNode(true);
      node.querySelector(".video-name").textContent = video.name || "Untitled video";
      node.querySelector(".video-meta").textContent = video.meta || "Uploaded recently";
      videoList.appendChild(node);
    });
  }

  const videoUpload = document.getElementById("video-upload");
  videoUpload.addEventListener("change", (event) => {
    const files = Array.from(event.target.files || []);
    files.forEach((file) => {
      videos.unshift({
        name: file.name,
        meta: `Uploaded now · ${(file.size / (1024 * 1024)).toFixed(1)} MB`,
      });
    });
    event.target.value = "";
    saveState({ ...state, videos });
    renderProfile();
  });
}

wireHomeLink();
renderProfile();
