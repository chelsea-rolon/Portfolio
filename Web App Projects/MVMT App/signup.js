const storageKey = "mvmt-state-v1";

function loadState() {
  try {
    return JSON.parse(localStorage.getItem(storageKey)) || {};
  } catch {
    return {};
  }
}

function saveState(nextState) {
  localStorage.setItem(storageKey, JSON.stringify(nextState));
}

const form = document.getElementById("signup-form");
const homeJump = document.querySelector('[data-action="go-home"]');

if (homeJump) {
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

if (form) {
  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const email = String(formData.get("email") || "").trim();
    const password = String(formData.get("password") || "");
    const role = String(formData.get("role") || "dancer");
    const hasStrongPassword = /[A-Z]/.test(password) && /\d/.test(password) && /[^A-Za-z0-9]/.test(password) && password.length >= 8;

    if (!email || !hasStrongPassword) {
      return;
    }

    const current = loadState();
    const updated = {
      ...current,
      name: String(formData.get("name") || email.split("@")[0] || ""),
      role: role === "instructor" ? "instructor" : "dancer",
      view: "home",
    };

    saveState(updated);
    window.location.href = "index.html";
  });
}
