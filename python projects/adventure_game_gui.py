import tkinter as tk

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

    # ══════════════════════════════════════════════════════════════════════
    # SCENES
    # ══════════════════════════════════════════════════════════════════════

    def show_intro(self):
        self._clear_btns()
        self._draw_dark_forest(paths=False)
        self._text("Welcome to Choose Your Quest!\nDo you wish to play?")
        self._btn("YES", self.show_forest_fork).pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("NO", self.show_confirm_quit, bg="#4a1a1a").pack(side=tk.LEFT, padx=10, expand=True)

    def show_confirm_quit(self):
        self._clear_btns()
        self._draw_dark_gameover()
        self._text("Are you sure you want to quit?")
        self._btn("YES, QUIT", self.show_goodbye, bg="#6a1a1a").pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("NO. GO BACK", self.show_intro).pack(side=tk.LEFT, padx=10, expand=True)

    def show_goodbye(self):
        self._clear_btns()
        self._draw_dark_gameover()
        self._text("\U0001F622  Goodbye...  \U0001F622")
        self.after(5000, self.quit)

    def show_forest_fork(self):
        self._clear_btns()
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
        self._draw_river_bridge()
        self._text(
            "The river looks treacherous.\n"
            "You can see the sharp rocks beneath the surface.\n"
            "In the far distance there's an old bridge.\n"
            "Do you cross the bridge or try to swim across?"
        )
        self._btn("CROSS BRIDGE", self.show_treasure_chest).pack(side=tk.LEFT, padx=10, expand=True)
        self._btn("SWIM ACROSS", self.show_swept_away).pack(side=tk.LEFT, padx=10, expand=True)

    def show_fairy_ring(self):
        self._clear_btns()
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
        self._draw_treasure_chest()
        self._text(
            "You discover a magnificent treasure chest\n"
            "overflowing with gold coins and glittering jewels!\n\n"
            "  \u2605  YOU WIN!  \u2605"
        )
        self._btn("PLAY AGAIN", self.show_intro).pack(expand=True)

    def show_silver_potion(self):
        self._clear_btns()
        self._draw_silver_potion()
        self._text(
            "You drink the silver potion and make your wish.\n"
            "You wish for endless adventure and live happily ever after!\n\n"
            "  \u2605  YOU WIN!  \u2605"
        )
        self._btn("PLAY AGAIN", self.show_intro).pack(expand=True)

    def show_lost_in_mist(self):
        self._clear_btns()
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
        from pathlib import Path
        try:
            from PIL import Image
        except ImportError:
            self.canvas.delete("all")
            return
        self.canvas.delete("all")
        base = Path(__file__).parent
        img = Image.open(base / img_path).convert("RGB").resize((GW, GH), Image.LANCZOS)
        for r in range(GH):
            for c in range(GW):
                red, green, blue = img.getpixel((c, r))
                self._px(c, r, f"#{red:02x}{green:02x}{blue:02x}")

    def _draw_dark_forest(self, paths=False):
        img = "forked_path.png" if paths else "forest_path.png"
        self._draw_image_scene(f"game photos/{img}")

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
