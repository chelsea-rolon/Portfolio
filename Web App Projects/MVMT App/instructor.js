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

function renderInstructorPage() {
  const state = loadState();
  if (!state.role) {
    window.location.href = "signup.html";
    return;
  }

  const shell = document.getElementById("instructor-shell");
  const stats = document.getElementById("instructor-stats");

  if (state.role !== "instructor") {
    shell.innerHTML = `
      <section class="card">
        <p class="section-label">Access restricted</p>
        <h3>Instructor account required</h3>
        <p class="support-copy">This page is only available to instructor profiles.</p>
        <a class="primary-button" href="profile.html">Go to your profile</a>
      </section>
    `;
    return;
  }

  const savedClasses = Array.isArray(state.savedClasses) ? state.savedClasses.length : 0;
  const instructorClasses = Number(state.instructorClasses || 0);

  stats.innerHTML = [
    { label: "Account type", value: "Instructor" },
    { label: "Published classes", value: String(instructorClasses) },
    { label: "Access", value: "Class publishing enabled" },
    { label: "Saved classes", value: String(savedClasses) },
  ].map((item) => `<div class="detail"><strong>${item.value}</strong><span>${item.label}</span></div>`).join("");

  const uploadForm = document.getElementById("class-upload-form");
  uploadForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(uploadForm);

    const next = {
      ...state,
      instructorClasses: instructorClasses + 1,
      bookings: Array.isArray(state.bookings) ? state.bookings : [],
    };

    const title = String(formData.get("title") || "New class");
    next.bookings.unshift({
      title: `Published: ${title}`,
      meta: "Your class is now live in the class board.",
    });

    saveState(next);
    uploadForm.reset();
    window.location.href = "index.html";
  });
}

wireHomeLink();
renderInstructorPage();
