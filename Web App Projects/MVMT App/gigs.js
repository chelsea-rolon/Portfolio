const storageKey = "mvmt-state-v1";

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

function renderGigs() {
  const gigList = document.getElementById("gig-list");
  const gigCardTemplate = document.getElementById("gig-card-template");
  gigList.innerHTML = "";

  gigData.forEach((item) => {
    const node = gigCardTemplate.content.cloneNode(true);
    node.querySelector(".project-type").textContent = item.type;
    node.querySelector(".title").textContent = item.title;
    node.querySelector(".pay").textContent = item.pay;
    node.querySelector(".gig-location").textContent = item.location;
    node.querySelector(".gig-copy").textContent = item.copy;
    node.querySelector(".deadline").textContent = item.deadline;

    node.querySelector(".apply-button").addEventListener("click", () => {
      const state = loadState();
      const bookings = Array.isArray(state.bookings) ? state.bookings : [];
      bookings.unshift({
        title: `Applied: ${item.title}`,
        meta: `${item.location} · ${item.pay}`,
      });
      saveState({ ...state, bookings });
      window.location.href = "profile.html";
    });

    gigList.appendChild(node);
  });
}

function bindQuickApply() {
  const form = document.getElementById("gig-apply-form");
  const toast = document.getElementById("gig-toast");
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const name = String(formData.get("name") || "Someone");
    toast.textContent = `Application sent for ${name}. The gig board will move this to your bookings.`;
    form.reset();
    setTimeout(() => {
      toast.textContent = "";
    }, 4000);
  });
}

wireHomeLink();
renderGigs();
bindQuickApply();
