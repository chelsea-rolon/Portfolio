import csv
import json
import tkinter as tk
from pathlib import Path

PS = 24   # screen pixels per grid cell
GW = 50   # grid columns  (1200 px wide — scaled to window)
GH = 20   # grid rows     (480 px tall)


class GameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Choose Your OwnAdventure Game")
        self.resizable(False, False)
        self.geometry("1200x760")
        self.configure(bg="#1a1a2e")

        self.canvas = tk.Canvas(
            self, width=GW * PS, height=GH * PS,
            highlightthickness=0, bg="#050510"
        )
        self.canvas.pack()

        self.text_frame = tk.Frame(self, bg="#1a1a2e", height=140)
        self.text_frame.pack(fill=tk.X, padx=20, pady=(10, 4))
        self.text_frame.pack_propagate(False)

        self.text_label = tk.Label(
            self.text_frame, text="",
            font=("Courier", 14, "bold"), bg="#1a1a2e", fg="#d8dce8",
            wraplength=1160, justify="center"
        )
        self.text_label.pack(expand=True)

        self.btn_frame = tk.Frame(self, bg="#1a1a2e", height=80)
        self.btn_frame.pack(fill=tk.X, padx=20, pady=(4, 16))
        self.btn_frame.pack_propagate(False)

        self._scene_key = None
        self._overlay_tag = "overlay"
        self._animation_job = None
        self._animation_phase = 0
        self._sprite_cache = {}
        self._bg_photo = None
        self._overlay_photos = []
        self._selected_character = None
        self._sprite_config = self._load_sprite_config()
        self.bind_all("<F5>", self.refresh_current_scene)
        self.bind_all("<Control-r>", self.refresh_current_scene)
        self.bind_all("<Control-R>", self.refresh_current_scene)

        self.show_intro()

    # ── Helpers ────────────────────────────────────────────────────────────
    def _clear_btns(self):
        for w in self.btn_frame.winfo_children():
            w.destroy()

    def _btn(self, label, cmd, bg="#0f3460"):
        return tk.Button(
            self.btn_frame, text=label, command=cmd,
            font=("Courier", 14, "bold"), bg=bg, fg="#ffffff",
            relief="flat", padx=20, pady=8, cursor="hand2",
            activebackground="#1a4a80", activeforeground="#ffffff",
        )

    def _text(self, t):
        self.text_label.config(text=t)

    def _px(self, c, r, color):
        x, y = c * PS, r * PS
        self.canvas.create_rectangle(x, y, x + PS, y + PS, fill=color, outline="")

    def _rect(self, c, r, w, h, color):
        for rr in range(r, r + h):
            for cc in range(c, c + w):
                self._px(cc, rr, color)

    def _set_scene(self, scene_key):
        resolved_scene = scene_key
        if self._selected_character and scene_key != "choose_character":
            variant = f"{scene_key}_{self._selected_character}"
            if variant in self._sprite_config:
                resolved_scene = variant

        if resolved_scene != self._scene_key:
            self._stop_overlay_animation()
            self._animation_phase = 0

        self._scene_key = resolved_scene

    def _choose_character_and_start(self, character):
        self._selected_character = character
        self.show_forest_fork()

    def _load_sprite_config(self):
        config_path = Path(__file__).parent / "game photos" / "sprite_config.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            scenes = loaded.get("scenes")
            if isinstance(scenes, dict):
                return scenes
        except Exception:
            pass
        return {}

    def refresh_current_scene(self, event=None):
        # Hot-reload config and redraw the active scene without restarting.
        self._sprite_config = self._load_sprite_config()
        self._sprite_cache.clear()
        self._animation_phase = 0

        scene_key = self._scene_key or "intro"
        for suffix in ("_warrior", "_hunter"):
            if scene_key.endswith(suffix):
                scene_key = scene_key[:-len(suffix)]
                break

        scene_handlers = {
            "intro": self.show_intro,
            "choose_character": self.show_choose_character,
            "confirm_quit": self.show_confirm_quit,
            "goodbye": self.show_dark_game_over,
            "forest_fork": self.show_forest_fork,
            "misty_field": self.show_mist_path,
            "river_path": self.show_river_path,
            "mountain_path": self.show_mountain_path,
            "keep_going_up": self.show_keep_going_up,
            "try_again": self.show_try_again,
            "go_back": self.show_go_back_false,
            "fairy_land": self.show_fairy_land,
            "swept_away": self.show_swept_away,
            "treasure_chest": self.show_treasure_chest,
            "magical_map": self.show_magical_map,
            "lost_in_mist": self.show_lost_in_mist,
        }

        handler = scene_handlers.get(scene_key)
        if handler is not None:
            handler()
        else:
            self._draw_scene_overlays()

        return "break"

    def _stop_overlay_animation(self):
        if self._animation_job is not None:
            self.after_cancel(self._animation_job)
            self._animation_job = None

    def _load_sprite_cells(self, rel_path):
        if rel_path in self._sprite_cache:
            return self._sprite_cache[rel_path]

        sprite_path = Path(__file__).parent / rel_path
        try:
            with open(sprite_path, "r", encoding="utf-8", newline="") as f:
                rows = []
                reader = csv.reader(f)
                for row in reader:
                    parsed = []
                    for cell in row:
                        token = cell.strip().lower()
                        if token in ("", ".", "transparent", "none"):
                            parsed.append(None)
                        else:
                            parsed.append(cell.strip())
                    rows.append(parsed)
            self._sprite_cache[rel_path] = rows
            return rows
        except Exception:
            self._sprite_cache[rel_path] = []
            return []

    def _overlay_visible(self, overlay):
        anim = overlay.get("animation")
        if not isinstance(anim, dict):
            return True
        mode = str(anim.get("mode", "")).lower()
        if mode == "frames":
            play_once = bool(anim.get("play_once", False))
            hide_on_complete = bool(anim.get("hide_on_complete", False))
            frame_count = max(1, int(overlay.get("frame_count", 9)))
            if play_once and hide_on_complete and self._animation_phase >= frame_count:
                return False
        if mode == "blink":
            return self._animation_phase % 2 == 0
        return True

    def _draw_png_overlay(self, overlay):
        from PIL import Image, ImageTk
        rel_path = overlay.get("sprite")
        if not rel_path:
            return
        sprite_path = Path(__file__).parent / rel_path
        if not sprite_path.exists():
            return
        frame_w = int(overlay.get("frame_width", 64))
        frame_h = int(overlay.get("frame_height", 64))
        sheet_row = int(overlay.get("sheet_row", 8))
        frame_count = max(1, int(overlay.get("frame_count", 9)))
        scale = int(overlay.get("scale", 3))
        anim = overlay.get("animation")
        play_once = isinstance(anim, dict) and bool(anim.get("play_once", False))
        if "frame_index" in overlay:
            frame_idx = int(overlay.get("frame_index", 0))
        else:
            if play_once:
                frame_idx = min(self._animation_phase, frame_count - 1)
            else:
                frame_idx = self._animation_phase % frame_count
        try:
            if rel_path not in self._sprite_cache:
                self._sprite_cache[rel_path] = Image.open(sprite_path).convert("RGBA")
            sheet = self._sprite_cache[rel_path]
        except Exception:
            return
        max_frame_index = max(0, (sheet.width // frame_w) - 1)
        frame_idx = max(0, min(frame_idx, max_frame_index))
        max_row_index = max(0, (sheet.height // frame_h) - 1)
        sheet_row = max(0, min(sheet_row, max_row_index))
        left = frame_idx * frame_w
        top = sheet_row * frame_h
        frame_img = sheet.crop((left, top, left + frame_w, top + frame_h))
        disp_w, disp_h = frame_w * scale, frame_h * scale
        frame_img = frame_img.resize((disp_w, disp_h), Image.NEAREST)
        photo = ImageTk.PhotoImage(frame_img)
        self._overlay_photos.append(photo)
        x = int(overlay.get("c", 0)) * PS
        y = int(overlay.get("r", 0)) * PS
        self.canvas.create_image(x, y, image=photo, anchor="nw", tags=(self._overlay_tag,))

    def _draw_png_image_overlay(self, overlay):
        from PIL import Image, ImageTk
        rel_path = overlay.get("sprite")
        if not rel_path:
            return

        sprite_path = Path(__file__).parent / rel_path
        if not sprite_path.exists():
            return

        try:
            if rel_path not in self._sprite_cache:
                self._sprite_cache[rel_path] = Image.open(sprite_path).convert("RGBA")
            img = self._sprite_cache[rel_path]
        except Exception:
            return

        display_w = int(overlay.get("display_w", 6 * PS))
        display_h = int(overlay.get("display_h", 6 * PS))
        img = img.resize((display_w, display_h), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        self._overlay_photos.append(photo)

        x = int(overlay.get("c", 0)) * PS
        y = int(overlay.get("r", 0)) * PS
        self.canvas.create_image(x, y, image=photo, anchor="nw", tags=(self._overlay_tag,))

    def _draw_overlay_sprite(self, overlay):
        if overlay.get("sprite_type") == "png_sheet":
            self._draw_png_overlay(overlay)
            return
        if overlay.get("sprite_type") == "png_image":
            self._draw_png_image_overlay(overlay)
            return

        rel_path = overlay.get("sprite")
        if not rel_path:
            return

        cells = self._load_sprite_cells(rel_path)
        c0 = int(overlay.get("c", 0))
        r0 = int(overlay.get("r", 0))

        for r_index, row in enumerate(cells):
            for c_index, color in enumerate(row):
                if not color:
                    continue
                c = c0 + c_index
                r = r0 + r_index
                if c < 0 or c >= GW or r < 0 or r >= GH:
                    continue
                x, y = c * PS, r * PS
                self.canvas.create_rectangle(
                    x, y, x + PS, y + PS,
                    fill=color, outline="", tags=(self._overlay_tag,)
                )

    def _schedule_overlay_animation(self, overlays):
        intervals = []
        for overlay in overlays:
            anim = overlay.get("animation")
            if not isinstance(anim, dict):
                continue
            mode = str(anim.get("mode", "")).lower()
            if mode in ("blink", "frames") and not self._overlay_animation_completed(overlay):
                intervals.append(int(anim.get("interval_ms", 420)))

        if not intervals:
            return

        interval = max(100, min(intervals))
        self._animation_job = self.after(interval, self._animate_overlays)

    def _overlay_animation_completed(self, overlay):
        anim = overlay.get("animation")
        if not isinstance(anim, dict):
            return False
        mode = str(anim.get("mode", "")).lower()
        if mode != "frames":
            return False
        if not bool(anim.get("play_once", False)):
            return False
        frame_count = max(1, int(overlay.get("frame_count", 9)))
        return self._animation_phase >= frame_count

    def _draw_scene_overlays(self):
        self._stop_overlay_animation()
        self.canvas.delete(self._overlay_tag)
        self._overlay_photos.clear()

        overlays = self._sprite_config.get(self._scene_key, [])
        if not isinstance(overlays, list) or not overlays:
            return

        for overlay in overlays:
            if not isinstance(overlay, dict):
                continue
            if self._overlay_visible(overlay):
                self._draw_overlay_sprite(overlay)

        self._schedule_overlay_animation(overlays)

    def _animate_overlays(self):
        self._animation_job = None
        self._animation_phase += 1
        self.canvas.delete(self._overlay_tag)
        self._overlay_photos.clear()

        overlays = self._sprite_config.get(self._scene_key, [])
        if not isinstance(overlays, list) or not overlays:
            return

        for overlay in overlays:
            if not isinstance(overlay, dict):
                continue
            if self._overlay_visible(overlay):
                self._draw_overlay_sprite(overlay)

        self._schedule_overlay_animation(overlays)

    # ══════════════════════════════════════════════════════════════════════
    # SCENES
    # ══════════════════════════════════════════════════════════════════════

    def show_intro(self):
        self._clear_btns()
        self._set_scene("intro")
        self._draw_dark_forest(paths=False)
        self._text("Welcome to Choose Your Quest!\n\nDo you wish to play?")
        self._btn("YES", self.show_choose_character).pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("NO", self.show_confirm_quit, bg="#4a1a1a").pack(side=tk.LEFT, padx=10, expand=True)

    def show_choose_character(self):
        self._clear_btns()
        self._set_scene("choose_character")
        self._draw_choose_character()
        self._text("Choose your character!")
        warrior_btn = self._btn("WARRIOR", lambda: self._choose_character_and_start("warrior"))
        hunter_btn = self._btn("HUNTER", lambda: self._choose_character_and_start("hunter"))
        warrior_btn.place(relx=0.27, y=8, anchor="n")
        hunter_btn.place(relx=0.73, y=8, anchor="n")

    def show_confirm_quit(self):
        self._clear_btns()
        self._set_scene("confirm_quit")
        self._draw_dark_gameover()
        self._text("<b>Are you sure you want to quit?")
        self._btn("YES, QUIT", self.show_dark_game_over, bg="#6a1a1a").pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("NO. GO BACK", self.show_intro).pack(side=tk.LEFT, padx=10, expand=True)

    def show_dark_game_over(self):
        self._clear_btns()
        self._set_scene("goodbye")
        self._draw_dark_game_over()
        self._text("\U0001F622  Goodbye...  \U0001F622")
        self.after(5000, self.quit)

    def show_forest_fork(self):
        self._clear_btns()
        self._set_scene("forest_fork")
        self._draw_dark_forest(paths=True)
        self._text(
            "You are transported instantly into a dark forest.\n"
            "You see two paths that lie ahead.\n"
            "You must make a choice:\n"
            "\n"
            "Go left into the dark mist — or right toward the sounds of a raging river?"
        )
        self._btn("INTO THE MIST", self.show_mist_path).pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("RIVER", self.show_river_path).pack(side=tk.LEFT, padx=10, expand=True)

    def show_mist_path(self):
        self._clear_btns()
        self._set_scene("misty_field")
        self._draw_misty_field()
        self._text(
            "You enter the icy mist and stumble into an open field.\n"
            "In the center is a glowing circle of mushrooms.\n"
            "You can feel your skin tingle with magic.\n"
            "\n"
            "Do you step inside the fairy ring or walk around it?\n"
        )
        self._btn("STEP INSIDE", self.show_fairy_land).pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("WALK AROUND", self.show_lost_in_mist).pack(side=tk.LEFT, padx=10, expand=True)

    def show_river_path(self):
        self._clear_btns()
        self._set_scene("river_path")
        self._draw_river_bridge()
        self._text(
            "The river looks treacherous.\n"
            "You can see the sharp rocks beneath the surface.\n"
            "In the far distance there's an old bridge.\n"
            "\n"
            "Do you cross the bridge or try to swim across?"
        )
        self._btn("CROSS BRIDGE", self.show_mountain_path).pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("SWIM ACROSS", self.show_swept_away).pack(side=tk.LEFT, padx=10, expand=True)

    def show_mountain_path(self):
        self._clear_btns()
        self._set_scene("mountain_path")
        self._draw_mountain_path()
        self._text(
            "You find yourself at the base of a towering mountain.\n"
            "he path ahead is steep and treacherous.\n"
            "\n"
            "Do you climb the mountain or turn back?"
        )
        self._btn("CLIMB", self.show_keep_going_up).pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("TURN BACK", self.show_intro).pack(side=tk.LEFT, padx=10, expand=True)

    def show_keep_going_up(self):
        self._clear_btns()
        self._set_scene("keep_going_up")
        self._draw_keep_going_up()
        self._text(
            "You start climbing the mountain, but it's slippery and dangerous.\n"
            "Halfway up, you lose your footing and slide halfway down.\n"
            "\n"
            "Do you want to try climbing again or head back to the forest?"
        )
        self._btn("TRY AGAIN", self.show_try_again).pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("BACK TO FOREST", self.show_go_back_false).pack(side=tk.LEFT, padx=10, expand=True)

    def show_try_again(self):
        self._clear_btns()
        self._set_scene("try_again")
        self._draw_try_again()
        self._text(
            "You carefully climb again, taking it slow and steady.\n"
            "After a long and exhausting climb, you reach the summit!\n"
            "The view is breathtaking and you feel a sense of accomplishment.\n"
            "Nearby you spot a half-buried treasure chest in the rocks.\n\n"
            "Do you open the chest or bury it again?"
        )
        self._btn("BURY IT AGAIN", self.show_go_back_false).pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("OPEN CHEST", self.show_treasure_chest, bg="#6a5200").pack(side=tk.LEFT, padx=10, expand=True)

    def show_go_back_false(self):
        self._clear_btns()
        self._set_scene("go_back")
        self._draw_go_back()
        self._text(
            "You decide to turn back and return to the forest.\n"
            "\n"
            "Out of nowhere an angry harpy appears shouting \"Thief!\" and swoops down, snatching you up into the sky!\n"
            "\n \u2620 GAME OVER \u2620"
        )
        self._btn("PLAY AGAIN", self.show_intro).pack(expand=True)

    def show_fairy_land(self):
        self._clear_btns()
        self._set_scene("fairy_land")
        self._draw_fairy_realm()
        self._text(
            "The mushrooms glow brighter and you vanish into another world!\n"
            "The world is bright and warm, filled with the scent of flowers and the sound of laughter.\n"
            "A fairy appears and offers you a choice:\n"
            "\n"
            "A golden key that can unlock any door,\n"
            "or a magic map that guides you to endless adventures.\n"
            "\n"
            "Do you take the key or the map?"
        )
        self._btn("GOLDEN KEY", self.show_treasure_chest, bg="#6a5200").pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("MAGICAL MAP", self.show_magical_map, bg="#2a2a5a").pack(side=tk.LEFT, padx=10, expand=True)

    def show_swept_away(self):
        self._clear_btns()
        self._set_scene("swept_away")
        self._draw_swept_away()
        self._text(
            "You dive in — but the current is far too strong!\n"
            "The river sweeps you away into the rapids.\n"
            "\n"
            "You are never seen again...\n\n"
            "\u2620 GAME OVER \u2620"
        )
        self._btn("PLAY AGAIN", self.show_intro).pack(expand=True)

    def show_treasure_chest(self):
        self._clear_btns()
        self._set_scene("treasure_chest")
        self._draw_treasure_chest()
        self._text(
            "You discover a magnificent treasure chest overflowing with gold coins and glittering jewels!\n\n"
            "  \u2605  YOU WIN!  \u2605"
        )
        self._btn("PLAY AGAIN", self.show_intro).pack(expand=True)

    def show_magical_map(self):
        self._clear_btns()
        self._set_scene("magical_map")
        self._draw_magical_map()
        self._text("You choose the magical map and it guides you to endless adventures.\n"
            "\n\u2605  YOU WIN!  \u2605")
        
        self._btn("PLAY AGAIN", self.show_intro).pack(expand=True)

    def show_lost_in_mist(self):
        self._clear_btns()
        self._set_scene("lost_in_mist")
        self._draw_lost_in_mist()
        self._text(
            "You walk for hours and hours...\n"
            "The mist grows thicker and you are lost forever.\n\n"
            "~ GAME OVER ~"
        )
        self._btn("PLAY AGAIN", self.show_intro).pack(expand=True)

    # ══════════════════════════════════════════════════════════════════════
    # PIXEL ART
    # ══════════════════════════════════════════════════════════════════════

    def _draw_image_scene(self, img_path):
        self.canvas.delete("all")
        try:
            from PIL import Image, ImageTk
            base = Path(__file__).parent
            img = Image.open(base / img_path).convert("RGB")
            img = img.resize((GW * PS, GH * PS), Image.LANCZOS)
            self._bg_photo = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self._bg_photo, anchor="nw")
        except Exception:
            # If image can't be loaded, fill with a dark background so text remains readable
            self._rect(0, 0, GW, GH, "#1a1a2e")
        self._draw_scene_overlays()

    def _draw_dark_forest(self, paths=False):
        img = "forked_path.jpg" if paths else "forest_path.jpg"
        self._draw_image_scene(f"game photos/{img}")

    def _draw_choose_character(self):
        self._draw_image_scene("game photos/choose_character_blank.png")

    def _draw_mountain_path(self):
        self._draw_image_scene("game photos/mountain_path.jpg")

    def _draw_climb_up(self):
        self._draw_image_scene("game photos/keep_going_up.jpg")   

    def _draw_try_again(self):
        self._draw_image_scene("game photos/try_again.jpg")
    
    def _draw_keep_going_up(self):
        self._draw_image_scene("game photos/keep_going_up.jpg")

    def _draw_treasure_chest(self):
        self._draw_image_scene("game photos/treasure_chest.jpg")

    def _draw_go_back(self):
        self._draw_image_scene("game photos/go_back.png")

    def _draw_misty_field(self):
        self._draw_image_scene("game photos/misty_field.jpg")

    def _draw_lost_in_mist(self):
        self._draw_image_scene("game photos/lost_in_mist.jpg")

    def _draw_river_bridge(self):
        self._draw_image_scene("game photos/river_bridge.jpg")

    def _draw_swept_away(self):
        self._draw_image_scene("game photos/swept_away.jpg")

    def _draw_fairy_realm(self):
        self._draw_image_scene("game photos/fairy_land.jpg")

    def _draw_treasure_chest(self):
        self._draw_image_scene("game photos/treasure_chest.jpg")

    def _draw_try_again(self):
        self._draw_image_scene("game photos/try_again.jpg")
    
    def _draw_magical_map(self):
        self._draw_image_scene("game photos/magical_map.jpg")

    def _draw_silver_potion(self):
        self._draw_image_scene("game photos/silver_potion.png")

    def _draw_dark_gameover(self):
        self._draw_image_scene("game photos/game_over.png")


if __name__ == "__main__":
    app = GameApp()
    app.mainloop()
