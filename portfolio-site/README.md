# Portfolio Site for GitHub Pages

This folder contains your GitHub Pages portfolio website.

## Quick Edit Checklist

Before publishing, update the following in `index.html`:

- Replace each `GitHub Link` and `Live Demo` placeholder (`href="#"`) with real links.
- Replace contact placeholders (GitHub, LinkedIn, email).
- Optional: edit project descriptions or add/remove cards.

## Resume Setup

1. Add your resume PDF to:

   `assets/resume/Chelsea_Rolon_Resume.pdf`

2. Keep the same filename, or update the resume button path in `index.html`.

## Deploy to GitHub Pages

### Option A: Deploy this folder as a separate repo (recommended)

1. Create a new GitHub repository, for example: `portfolio`.
2. Upload only the contents of this folder (`index.html`, `styles.css`, `script.js`, `assets/`).
3. In GitHub repo settings, open **Pages**.
4. Under **Build and deployment**:
   - Source: **Deploy from a branch**
   - Branch: `main`
   - Folder: `/ (root)`
5. Save. Your site will be published in about 1 to 5 minutes.

### Option B: Keep it in this monorepo

1. Push this workspace repo to GitHub.
2. In GitHub **Pages** settings, select:
   - Source: **Deploy from a branch**
   - Branch: `main`
   - Folder: `/portfolio-site`

If GitHub does not allow a custom folder directly, move this folder to `/docs` and set Pages folder to `/docs`.

## Local Preview

From the `portfolio-site` folder, open `index.html` directly or run a static server.
