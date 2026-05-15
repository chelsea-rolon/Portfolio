# Karaoke Sign Up

This project is a FastAPI app for Broadway karaoke sign-ups with a public sign-up page and an admin page.

- `app.py` serves the API and static files.
- `karaoke_signup.html` is the public sign-up interface.
- `admin.html` is the admin view for managing sign-ups and the share link.
- `karaoke playlist/` stores general karaoke tracks, and `performer songs/` stores performer-specific media.

Run locally from this folder with `python -m uvicorn app:app --host 127.0.0.1 --port 8000`.