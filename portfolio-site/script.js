const filterButtons = document.querySelectorAll(".chip");
const cards = document.querySelectorAll(".project-card");

function setActiveFilter(button) {
  filterButtons.forEach((item) => item.classList.remove("is-active"));
  button.classList.add("is-active");
}

function applyFilter(filterName) {
  cards.forEach((card) => {
    const tags = card.dataset.tags || "";
    const isVisible = filterName === "all" || tags.includes(filterName);
    card.style.display = isVisible ? "flex" : "none";
  });
}

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const filterName = button.dataset.filter;
    setActiveFilter(button);
    applyFilter(filterName);
  });
});
