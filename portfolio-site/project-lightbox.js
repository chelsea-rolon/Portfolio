document.addEventListener("DOMContentLoaded", () => {
  const shots = document.querySelectorAll(".project-shot");
  if (!shots.length) {
    return;
  }

  const overlay = document.createElement("div");
  overlay.className = "project-lightbox";
  overlay.innerHTML = `
    <div class="project-lightbox-dialog" role="dialog" aria-modal="true" aria-label="Image preview">
      <button class="project-lightbox-close" type="button" aria-label="Close image preview">&times;</button>
      <img class="project-lightbox-image" alt="" />
    </div>
  `;
  document.body.appendChild(overlay);

  const closeButton = overlay.querySelector(".project-lightbox-close");
  const previewImage = overlay.querySelector(".project-lightbox-image");

  const closeLightbox = () => {
    overlay.classList.remove("is-open");
    document.body.classList.remove("project-lightbox-open");
    previewImage.src = "";
    previewImage.alt = "";
  };

  const openLightbox = (image) => {
    previewImage.src = image.src;
    previewImage.alt = image.alt || "Project screenshot preview";
    overlay.classList.add("is-open");
    document.body.classList.add("project-lightbox-open");
    closeButton.focus();
  };

  shots.forEach((image) => {
    image.addEventListener("click", () => openLightbox(image));
    image.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openLightbox(image);
      }
    });
    image.setAttribute("tabindex", "0");
    image.setAttribute("role", "button");
    image.setAttribute("aria-label", `${image.alt || "Project screenshot"}. Open larger image`);
  });

  closeButton.addEventListener("click", closeLightbox);
  overlay.addEventListener("click", (event) => {
    if (event.target === overlay) {
      closeLightbox();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && overlay.classList.contains("is-open")) {
      closeLightbox();
    }
  });
});