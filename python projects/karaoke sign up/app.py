from __future__ import annotations

import asyncio
import json
import os
import socket
from datetime import datetime, UTC
from pathlib import Path
from threading import Lock
from typing import Any

import qrcode
import qrcode.image.svg
from fastapi import FastAPI, HTTPException, Query, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
SONGS_PATH = BASE_DIR / "songs.json"
SIGNUPS_PATH = BASE_DIR / "signups.json"
COMPLETED_SIGNUPS_PATH = BASE_DIR / "completed_signups.json"
PLAYLIST_DIR = BASE_DIR / "karaoke playlist"
PERFORMER_DIR = BASE_DIR / "performer songs"
HTML_PATH = BASE_DIR / "karaoke_signup.html"
ADMIN_HTML_PATH = BASE_DIR / "admin.html"
DEFAULT_ADMIN_CODE = os.getenv("KARAOKE_ADMIN_CODE", "1013")

app = FastAPI(title="Clairvoya Broadway Karaoke Sign Up")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if PLAYLIST_DIR.exists():
    app.mount("/karaoke playlist", StaticFiles(directory=PLAYLIST_DIR), name="karaoke-playlist")
if PERFORMER_DIR.exists():
    app.mount("/performer songs", StaticFiles(directory=PERFORMER_DIR), name="performer-songs")

state_lock = Lock()


class SignupRequest(BaseModel):
    name: str = Field(min_length=1)
    song: str = Field(min_length=1)
    list: str = Field(min_length=1)


class ResetRequest(BaseModel):
    code: str = Field(min_length=1)


class RemoveSignupRequest(BaseModel):
    code: str = Field(min_length=1)
    song: str = Field(min_length=1)


class CompleteSignupRequest(BaseModel):
    code: str = Field(min_length=1)
    song: str = Field(min_length=1)


class ConnectionManager:
    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clients.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._clients.discard(websocket)

    async def broadcast_json(self, payload: dict[str, Any]) -> None:
        stale_clients: list[WebSocket] = []
        for client in list(self._clients):
            try:
                await client.send_json(payload)
            except Exception:
                stale_clients.append(client)

        for client in stale_clients:
            self.disconnect(client)


manager = ConnectionManager()


def ensure_signups_file() -> None:
    if not SIGNUPS_PATH.exists():
        SIGNUPS_PATH.write_text("[]\n", encoding="utf-8")
    if not COMPLETED_SIGNUPS_PATH.exists():
        COMPLETED_SIGNUPS_PATH.write_text("[]\n", encoding="utf-8")


def load_song_config() -> dict[str, Any]:
    if not SONGS_PATH.exists():
        raise HTTPException(status_code=500, detail="songs.json not found.")

    try:
        return json.loads(SONGS_PATH.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"songs.json is invalid: {exc.msg}") from exc


def load_signups() -> list[dict[str, str]]:
    ensure_signups_file()
    try:
        data = json.loads(SIGNUPS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"signups.json is invalid: {exc.msg}") from exc

    if not isinstance(data, list):
        raise HTTPException(status_code=500, detail="signups.json must contain a list.")
    return data


def save_signups(signups: list[dict[str, str]]) -> None:
    SIGNUPS_PATH.write_text(json.dumps(signups, indent=2), encoding="utf-8")


def load_completed_signups() -> list[dict[str, str]]:
    ensure_signups_file()
    try:
        data = json.loads(COMPLETED_SIGNUPS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"completed_signups.json is invalid: {exc.msg}") from exc

    if not isinstance(data, list):
        raise HTTPException(status_code=500, detail="completed_signups.json must contain a list.")
    return data


def save_completed_signups(signups: list[dict[str, str]]) -> None:
    COMPLETED_SIGNUPS_PATH.write_text(json.dumps(signups, indent=2), encoding="utf-8")


def get_lan_ip() -> str:
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("8.8.8.8", 80))
        return str(probe.getsockname()[0])
    except OSError:
        return "127.0.0.1"
    finally:
        probe.close()


def resolve_share_url(request: Request) -> str:
    scheme = request.url.scheme or "http"
    port = request.url.port or (443 if scheme == "https" else 80)
    host = request.url.hostname or get_lan_ip()

    if host in {"127.0.0.1", "localhost", "0.0.0.0"}:
        host = get_lan_ip()

    default_port = (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    port_part = "" if default_port else f":{port}"
    return f"{scheme}://{host}{port_part}/"


def is_valid_admin_code(code: str) -> bool:
    value = code.strip()
    if not value:
        return False

    # Keep legacy compatibility so existing sessions/devices still work.
    accepted_codes = {DEFAULT_ADMIN_CODE, "1013", "karaoke-admin"}
    return value in accepted_codes


def build_state(share_url: str | None = None) -> dict[str, Any]:
    config = load_song_config()
    performer_songs = list(config.get("performerSongs", []))
    other_songs = list(config.get("otherSongs", []))
    song_videos = dict(config.get("songVideos", {}))
    signups = load_signups()
    completed_signups = load_completed_signups()

    taken_songs = {item.get("song", "") for item in signups}
    available_performer = [song for song in performer_songs if song not in taken_songs]
    available_other = [song for song in other_songs if song not in taken_songs]

    return {
        "performerSongs": available_performer,
        "otherSongs": available_other,
        "songVideos": song_videos,
        "signups": signups,
        "completedSignups": completed_signups,
        "shareUrl": share_url or "",
    }


@app.get("/")
def read_index() -> FileResponse:
    return FileResponse(
        HTML_PATH,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@app.get("/admin")
def read_admin() -> FileResponse:
    return FileResponse(
        ADMIN_HTML_PATH,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@app.get("/api/state")
def get_state(request: Request) -> dict[str, Any]:
    with state_lock:
        return build_state(resolve_share_url(request))


@app.get("/api/qr")
def get_qr_code(request: Request, text: str | None = Query(default=None)) -> Response:
    payload = text or resolve_share_url(request)
    image = qrcode.make(payload, image_factory=qrcode.image.svg.SvgPathImage)
    svg_bytes = image.to_string()
    return Response(content=svg_bytes, media_type="image/svg+xml")


@app.post("/api/signup")
async def create_signup(payload: SignupRequest, request: Request) -> dict[str, str]:
    with state_lock:
        config = load_song_config()
        performer_songs = set(config.get("performerSongs", []))
        other_songs = set(config.get("otherSongs", []))
        allowed_songs = performer_songs | other_songs

        song_name = payload.song.strip()
        user_name = payload.name.strip()
        list_name = payload.list.strip()

        if song_name not in allowed_songs:
            raise HTTPException(status_code=400, detail="Selected song is not in the playlist.")

        if song_name in performer_songs:
            expected_list = "Performer Songs"
        else:
            expected_list = "Other Songs"

        if list_name != expected_list:
            raise HTTPException(status_code=400, detail="Selected song does not match the chosen list.")

        signups = load_signups()
        if any(item.get("song") == song_name for item in signups):
            raise HTTPException(status_code=409, detail="That song was already selected from another device.")

        new_signup = {
            "name": user_name,
            "song": song_name,
            "list": expected_list,
            "videoPath": str(config.get("songVideos", {}).get(song_name, "")),
        }
        signups.append(new_signup)
        save_signups(signups)

    await manager.broadcast_json({"type": "state", "payload": build_state(resolve_share_url(request))})
    return new_signup


@app.post("/api/reset")
async def reset_signups(payload: ResetRequest, request: Request) -> dict[str, str]:
    if not is_valid_admin_code(payload.code):
        raise HTTPException(status_code=403, detail="Invalid admin code.")

    with state_lock:
        save_signups([])
        save_completed_signups([])

    await manager.broadcast_json({"type": "state", "payload": build_state(resolve_share_url(request))})
    return {"status": "reset"}


@app.post("/api/complete-signup")
async def complete_signup(payload: CompleteSignupRequest, request: Request) -> dict[str, str]:
    if not is_valid_admin_code(payload.code):
        raise HTTPException(status_code=403, detail="Invalid admin code.")

    song_name = payload.song.strip()
    with state_lock:
        signups = load_signups()
        matching_signup = next((item for item in signups if item.get("song") == song_name), None)
        if matching_signup is None:
            raise HTTPException(status_code=404, detail="Signup not found.")

        updated_signups = [item for item in signups if item.get("song") != song_name]
        completed_signups = load_completed_signups()
        completed_signups.append({
            **matching_signup,
            "completedAt": datetime.now(UTC).isoformat(),
        })

        save_signups(updated_signups)
        save_completed_signups(completed_signups)

    await manager.broadcast_json({"type": "state", "payload": build_state(resolve_share_url(request))})
    return {"status": "completed", "song": song_name}


@app.post("/api/remove-signup")
async def remove_signup(payload: RemoveSignupRequest, request: Request) -> dict[str, str]:
    if not is_valid_admin_code(payload.code):
        raise HTTPException(status_code=403, detail="Invalid admin code.")

    song_name = payload.song.strip()
    with state_lock:
        signups = load_signups()
        updated_signups = [item for item in signups if item.get("song") != song_name]
        if len(updated_signups) == len(signups):
            raise HTTPException(status_code=404, detail="Signup not found.")
        save_signups(updated_signups)

    await manager.broadcast_json({"type": "state", "payload": build_state(resolve_share_url(request))})
    return {"status": "removed", "song": song_name}


@app.websocket("/ws")
async def websocket_state(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        with state_lock:
            await websocket.send_json({"type": "state", "payload": build_state()})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
