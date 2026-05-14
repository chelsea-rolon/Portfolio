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
        self.title("Adventure Game")
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
            font=("Courier", 14), bg="#1a1a2e", fg="#d8dce8",
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
        self._sprite_config = self._load_sprite_config()

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
        self._scene_key = scene_key

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
        if mode == "blink":
            return self._animation_phase % 2 == 0
        return True

    def _draw_overlay_sprite(self, overlay):
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
            if mode == "blink":
                intervals.append(int(anim.get("interval_ms", 420)))

        if not intervals:
            return

        interval = max(100, min(intervals))
        self._animation_job = self.after(interval, self._animate_overlays)

    def _draw_scene_overlays(self):
        self._stop_overlay_animation()
        self.canvas.delete(self._overlay_tag)

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
        self._text("Welcome to Choose Your Quest!\nDo you wish to play?")
        self._btn("YES", self.show_forest_fork).pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("NO", self.show_confirm_quit, bg="#4a1a1a").pack(side=tk.LEFT, padx=10, expand=True)

    def choose_character(self):
        self._clear_btns()
        self._set_scene("choose_character")
        self._draw_dark_forest(paths=False)
        self._text("Choose your character:")
        self._btn("WARRIOR", self.show_forest_fork).pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("MAGE", self.show_forest_fork).pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("ROGUE", self.show_forest_fork).pack(side=tk.LEFT, padx=10, expand=True)

    def show_confirm_quit(self):
        self._clear_btns()
        self._set_scene("confirm_quit")
        self._draw_dark_gameover()
        self._text("Are you sure you want to quit?")
        self._btn("YES, QUIT", self.show_goodbye, bg="#6a1a1a").pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("NO. GO BACK", self.show_intro).pack(side=tk.LEFT, padx=10, expand=True)

    def show_goodbye(self):
        self._clear_btns()
        self._set_scene("goodbye")
        self._draw_dark_gameover()
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
            "Go left into the dark mist — or right toward the sounds of a raging river?"
        )
        self._btn("INTO THE MIST", self.show_mist_path).pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("RIVER", self.show_river_path).pack(side=tk.LEFT, padx=10, expand=True)

    def show_mist_path(self):
        self._clear_btns()
        self._set_scene("mist_path")
        self._draw_misty_field()
        self._text(
            "You enter the icy mist and stumble into an open field.\n"
            "In the center is a glowing circle of mushrooms.\n"
            "You can feel your skin tingle with magic."
            "Do you step inside the fairy ring or walk around it?\n"
        )
        self._btn("STEP INSIDE", self.show_fairy_ring).pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("WALK AROUND", self.show_lost_in_mist).pack(side=tk.LEFT, padx=10, expand=True)

    def show_river_path(self):
        self._clear_btns()
        self._set_scene("river_path")
        self._draw_river_bridge()
        self._text(
            "The river looks treacherous.\n"
            "You can see the sharp rocks beneath the surface.\n"
            "In the far distance there's an old bridge.\n"
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
            "The path ahead is steep and treacherous.\n"
            "Do you climb the mountain or turn back?"
        )
        self._btn("CLIMB", self.show_CLIMB_UP).pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("TURN BACK", self.show_intro).pack(side=tk.LEFT, padx=10, expand=True)

    def show_CLIMB_UP(self):
        self._clear_btns()
        self._set_scene("climb_up")
        self._draw_climb_up()
        self._text(
            "You start climbing the mountain, but it's slippery and dangerous.\n"
            "Halfway up, you lose your footing and fall back down to the base.\n"
            "Do you want to try climbing again or head back to the forest?"
        )
        self._btn("TRY AGAIN", self.show_CLIMB_UP_Again).pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("BACK TO FOREST", self.show_go_back_false).pack(side=tk.LEFT, padx=10, expand=True)

    def show_CLIMB_UP_Again(self):
        self._clear_btns()
        self._set_scene("climb_up_again")
        self._draw_keep_going_up()
        self._text(
            "You carefully climb again, taking it slow and steady.\n"
            "After a long and exhausting climb, you reach the summit!\n"
            "The view is breathtaking and you feel a sense of accomplishment.\n"
            "Nearby you see a treasure chest half-buried in the rocks.\n"
        )
        self._btn("HEAD BACK DOWN", self.show_mountain_path).pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("OPEN CHEST", self.show_treasure_chest, bg="#6a5200").pack(side=tk.LEFT, padx=10, expand=True)

    def show_go_back_false(self):
        self._clear_btns()
        self._set_scene("go_back_false")
        self._draw_go_back_false()
        self._text(
            "You decide to turn back and return to the fork in the forest.\n"
            "Out of nowhere a harpy comes swooping down and snatches you up into the sky!\n"
            "\u2620 GAME OVER \u2620"
        )
        self._btn("PLAY AGAIN", self.show_intro).pack(expand=True)

    def show_fairy_ring(self):
        self._clear_btns()
        self._set_scene("fairy_ring")
        self._draw_fairy_realm()
        self._text(
            "The mushrooms glow brighter and you vanish into another world!\n"
            "The world is bright and warm, filled with the scent of flowers and the sound of laughter.\n"
            "A fairy appears and offers you a choice:\n"
            "A golden key that can unlock any door,\n"
            "or a silver potion that grants you one wish.\n"
            "Do you take the key or drink the potion?"
        )
        self._btn("GOLDEN KEY", self.show_treasure_chest, bg="#6a5200").pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("SILVER POTION", self.show_silver_potion, bg="#2a2a5a").pack(side=tk.LEFT, padx=10, expand=True)

    def show_swept_away(self):
        self._clear_btns()
        self._set_scene("swept_away")
        self._draw_swept_away()
        self._text(
            "You dive in — but the current is far too strong!\n"
            "The river sweeps you away into the rapids.\n"
            "You sre never seen again...\n\n"
            "\u2620 GAME OVER \u2620"
        )
        self._btn("PLAY AGAIN", self.show_intro).pack(expand=True)

    def show_treasure_chest(self):
        self._clear_btns()
        self._set_scene("treasure_chest")
        self._draw_treasure_chest()
        self._text(
            "You discover a magnificent treasure chest\n"
            "overflowing with gold coins and glittering jewels!\n\n"
            "  \u2605  YOU WIN!  \u2605"
        )
        self._btn("PLAY AGAIN", self.show_intro).pack(expand=True)

    def show_silver_potion(self):
        self._clear_btns()
        self._set_scene("silver_potion")
        self._draw_silver_potion()
        self._text(
            "You drink the silver potion and make your wish.\n"
            "You wish for endless adventure and live happily ever after!\n\n"
            "  \u2605  YOU WIN!  \u2605"
        )
        self._btn("PLAY AGAIN", self.show_intro).pack(expand=True)

    def show_lost_in_mist(self):
        self._clear_btns()
        self._set_scene("lost_in_mist")
        self._draw_dark_gameover()
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
            from PIL import Image
            base = Path(__file__).parent
            img = Image.open(base / img_path).convert("RGB").resize((GW, GH), Image.LANCZOS)
            for r in range(GH):
                for c in range(GW):
                    red, green, blue = img.getpixel((c, r))
                    self._px(c, r, f"#{red:02x}{green:02x}{blue:02x}")
        except Exception:
            # If image can't be loaded, fill with a dark background so text remains readable
            self._rect(0, 0, GW, GH, "#1a1a2e")
        self._draw_scene_overlays()

    def _draw_dark_forest(self, paths=False):
        img = "forked_path.png" if paths else "forest_path.png"
        self._draw_image_scene(f"game photos/{img}")

    def _draw_choose_character(self):
        self._draw_image_scene("game photos/choose_character.png")

    def _draw_mountain_path(self):
        self._draw_image_scene("game photos/mountain_trail.png")

    def _draw_climb_up(self):
        self._draw_image_scene("game photos/mountain_trail.png")   

    def _draw_climb_up_again(self):
        self._draw_image_scene("game photos/keep_going_up.png")
    
    def _draw_keep_going_up(self):
        self._draw_image_scene("game photos/keep_going_up.png")

    def _draw_treasure_chest(self):
        self._draw_image_scene("game photos/treasure_chest.png")

    def _draw_go_back_false(self):
        self._draw_image_scene("game photos/go_back_false.png")

    def _draw_misty_field(self):
        self._draw_image_scene("game photos/misty_field.png")

    def _draw_river_bridge(self):
        self._draw_image_scene("game photos/river_bridge.png")

    def _draw_swept_away(self):
        self._draw_image_scene("game photos/swept_away.png")

    def _draw_fairy_realm(self):
        self._draw_image_scene("game photos/fairy_land.png")

    def _draw_treasure_chest(self):
        self._draw_image_scene("game photos/treasure_chest.png")

    def _draw_silver_potion(self):
        self._draw_image_scene("game photos/silver_potion.png")

    def _draw_dark_gameover(self):
        self._draw_image_scene("game photos/game_over.png")


if __name__ == "__main__":
    app = GameApp()
    app.mainloop()
