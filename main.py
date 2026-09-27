import json
import math
import random
import time
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle, Triangle
from kivy.metrics import dp
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window

try:
    Window.clearcolor = (7 / 255, 11 / 255, 24 / 255, 1)
except Exception:
    pass

V_W = 1280.0
V_H = 720.0
TARGET_FPS = 60.0

BG = (7 / 255, 11 / 255, 24 / 255, 1)
GRID = (16 / 255, 26 / 255, 49 / 255, 1)
CYAN = (66 / 255, 245 / 255, 1, 1)
PINK = (1, 60 / 255, 172 / 255, 1)
YELLOW = (1, 230 / 255, 109 / 255, 1)
WHITE = (244 / 255, 247 / 255, 1, 1)
RED = (1, 92 / 255, 122 / 255, 1)
GREEN = (104 / 255, 1, 176 / 255, 1)
MUTED = (110 / 255, 127 / 255, 168 / 255, 1)

MODE_KEYS = ("classic", "endless", "time")
TEXT = {
    "en": {
        "language": "فارسی",
        "menu": "☰ MENU",
        "exit": "✕ EXIT",
        "pause": "Ⅱ",
        "resume": "▶",
        "choose": "Choose your game mode",
        "classic": "CLASSIC",
        "classic_desc": "5 lives • score • dodge • shoot",
        "endless": "ENDLESS",
        "endless_desc": "No lives • no death • survive forever",
        "time": "TIME ATTACK",
        "time_desc": "Beat your survival time record",
        "play": "PLAY",
        "start": "TAP TO START",
        "score": "SCORE",
        "lives": "LIVES",
        "level": "LEVEL",
        "time": "TIME",
        "endless_hud": "ENDLESS • ∞ LIVES",
        "combo": "COMBO",
        "paused": "PAUSED",
        "resume_text": "Tap pause or MENU to continue",
        "gameover": "GAME OVER",
        "runover": "RUN OVER",
        "best": "BEST",
        "again": "TAP TO PLAY AGAIN",
        "life_lost": "-1 LIFE",
        "life_plus": "+1 LIFE",
        "bonus": "BONUS",
        "new_time": "NEW TIME RECORD!",
        "new_score": "NEW SCORE RECORD!",
        "level_up": "LEVEL UP!",
        "level_break": "ENEMIES RESTARTING...",
        "touch": "Touch controls • Hold arrows to move • Hold FIRE to shoot",
    },
    "fa": {
        "language": "English",
        "menu": "☰ منو",
        "exit": "✕ خروج",
        "pause": "Ⅱ",
        "resume": "▶",
        "choose": "حالت بازی را انتخاب کن",
        "classic": "کلاسیک",
        "classic_desc": "۵ جان • امتیاز • جاخالی • شلیک",
        "endless": "بی‌نهایت",
        "endless_desc": "بدون جان • بدون مرگ • تا هر وقت بخواهی",
        "time": "حمله زمانی",
        "time_desc": "رکورد زمان زنده ماندنت را بشکن",
        "play": "شروع",
        "start": "برای شروع لمس کن",
        "score": "امتیاز",
        "lives": "جان",
        "level": "مرحله",
        "time": "زمان",
        "endless_hud": "بی‌نهایت • ∞ جان",
        "combo": "کمبو",
        "paused": "بازی متوقف است",
        "resume_text": "برای ادامه روی توقف یا منو بزن",
        "gameover": "بازی تمام شد",
        "runover": "پایان اجرا",
        "best": "رکورد",
        "again": "برای بازی دوباره لمس کن",
        "life_lost": "-۱ جان",
        "life_plus": "+۱ جان",
        "bonus": "امتیاز اضافه",
        "new_time": "رکورد جدید زمان!",
        "new_score": "رکورد جدید امتیاز!",
        "level_up": "مرحله بالاتر رفت!",
        "level_break": "دشمن‌ها دوباره شروع می‌شوند...",
        "touch": "کنترل لمسی • فلش‌ها را نگه دار • FIRE را نگه دار",
    },
}


class HoldButton(ButtonBehavior, Label):
    """Touch button that stays active while the finger is held down."""
    active = BooleanProperty(False)
    accent = StringProperty("cyan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.halign = "center"
        self.valign = "middle"
        self.color = WHITE
        self.font_size = dp(22)
        self.bold = True
        self.markup = False
        self._build_canvas()

    def _build_canvas(self):
        with self.canvas.before:
            self._bg_color = Color(18 / 255, 28 / 255, 50 / 255, 0.72)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            self._line_color = Color(*CYAN)
            self._line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(12)), width=1.4)
        self.bind(pos=self._sync, size=self._sync, active=self._sync)

    def _sync(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._line.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(12))
        c = GREEN if self.active and self.accent == "green" else CYAN if self.accent == "cyan" else PINK
        alpha = 0.88 if self.active else 0.52
        self._bg_color.rgba = (c[0], c[1], c[2], alpha)
        self._line_color.rgba = (c[0], c[1], c[2], 1)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.active = True
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.active:
            self.active = False
            return True
        return super().on_touch_up(touch)


class NeonField(Widget):
    def __init__(self, app_ui, **kwargs):
        super().__init__(**kwargs)
        self.app_ui = app_ui
        self.player_x = V_W / 2
        self.player_y = V_H - 115
        self.player_r = 22
        self.enemies = []
        self.bullets = []
        self.powerups = []
        self.particles = []
        self.enemy_timer = 0.0
        self.power_timer = 0.0
        self.shot_cooldown = 0.0
        self.invulnerable_until = 0.0
        self.flash_until = 0.0
        self.level_pause_until = 0.0
        self.level_effect_until = 0.0
        self.level_effect_start = 0.0
        self.message_until = 0.0
        self.message = ""
        self.level = 1
        self.score = 0
        self.lives = 5
        self.combo = 0
        self.survival_time = 0.0
        self.run_start = 0.0
        self.last_update = time.perf_counter()
        self.state = "menu"
        self.mode = "classic"
        self.language = "en"
        self.best_score = 0
        self.best_time = 0.0

        self.sound_dir = Path(__file__).resolve().parent / "data" / "sounds"
        self.sounds = {}
        for name in ("shoot", "hit", "powerup", "gameover", "levelup", "combo", "life_lost", "select", "start", "pause"):
            try:
                self.sounds[name] = SoundLoader.load(str(self.sound_dir / f"{name}.wav"))
            except Exception:
                self.sounds[name] = None

        self.load_records()
        self.bind(size=lambda *_: self.redraw())
        Clock.schedule_interval(self.tick, 1.0 / TARGET_FPS)

    def t(self, key):
        return TEXT[self.language].get(key, key)

    def play_sound(self, name):
        sound = self.sounds.get(name)
        if sound is None:
            return
        try:
            sound.stop()
            sound.play()
        except Exception:
            pass

    def load_records(self):
        try:
            path = Path(App.get_running_app().user_data_dir) / "records.json"
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                self.best_score = int(data.get("best_score", 0))
                self.best_time = float(data.get("best_time", 0.0))
        except Exception:
            self.best_score = 0
            self.best_time = 0.0

    def save_records(self):
        try:
            path = Path(App.get_running_app().user_data_dir) / "records.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"best_score": self.best_score, "best_time": self.best_time}), encoding="utf-8")
        except Exception:
            pass

    # ----- gameplay -----
    def start_game(self, mode):
        self.mode = mode
        self.state = "playing"
        self.score = 0
        self.lives = 5
        self.level = 1
        self.combo = 0
        self.enemy_timer = 0.0
        self.power_timer = 0.0
        self.shot_cooldown = 0.0
        self.level_pause_until = 0.0
        self.level_effect_until = 0.0
        self.message_until = 0.0
        self.message = ""
        self.enemies.clear()
        self.bullets.clear()
        self.powerups.clear()
        self.particles.clear()
        self.player_x = V_W / 2
        self.player_y = V_H - 115
        self.run_start = time.perf_counter()
        self.survival_time = 0.0
        self.play_sound("start")
        self.app_ui.refresh_ui()

    def back_to_menu(self):
        self.state = "menu"
        self.enemies.clear(); self.bullets.clear(); self.powerups.clear(); self.particles.clear()
        self.app_ui.refresh_ui()

    def toggle_pause(self):
        if self.state == "playing":
            self.state = "paused"
            self.play_sound("pause")
        elif self.state == "paused":
            self.state = "playing"
            self.play_sound("pause")
        self.app_ui.refresh_ui()

    def game_over(self):
        self.state = "gameover"
        if self.mode == "time":
            self.best_time = max(self.best_time, self.survival_time)
        elif self.mode == "classic":
            self.best_score = max(self.best_score, self.score)
        self.save_records()
        self.spawn_particles(self.player_x, self.player_y, PINK, 44)
        self.play_sound("gameover")
        self.app_ui.refresh_ui()

    def current_level(self):
        if self.mode == "classic":
            return 1 + int(self.score // 750)
        if self.mode == "endless":
            return 1 + int(self.survival_time // 45)
        return 1 + int(self.survival_time // 50)

    def enemy_spawn_interval(self):
        base = 0.92 if self.mode == "classic" else 0.82 if self.mode == "endless" else 0.88
        return max(0.17, base / (1.0 + 0.055 * (self.level - 1)))

    def enemy_batch(self):
        return min(4, 1 + (self.level - 1) // 3)

    def spawn_enemy(self):
        for _ in range(self.enemy_batch()):
            r = random.randint(14, 24)
            x = random.randint(r + 10, int(V_W - r - 10))
            speed = min(8.5, random.uniform(2.0, 3.15) + 0.22 * (self.level - 1))
            self.enemies.append({
                "x": float(x), "y": float(-r - random.randint(10, 60)),
                "r": r, "speed": speed, "phase": random.random() * math.tau,
                "kind": random.choice(("orb", "diamond", "orb")),
            })

    def spawn_powerup(self):
        if self.mode == "endless":
            return
        x = random.randint(50, int(V_W - 50))
        kind = "heart" if self.mode == "time" else random.choice(("heart", "score"))
        self.powerups.append({"x": float(x), "y": -30.0, "r": 15, "speed": 2.2 + min(2.5, self.level * 0.06), "pulse": 0.0, "kind": kind})

    def spawn_particles(self, x, y, color, amount=10):
        for _ in range(amount):
            a = random.uniform(0, math.tau); s = random.uniform(1.5, 6.0)
            self.particles.append({"x": x, "y": y, "vx": math.cos(a)*s, "vy": math.sin(a)*s, "life": random.uniform(.25, .75), "size": random.uniform(2, 6), "color": color})

    def combo_mult(self):
        return 1.0 + 0.25 * min(max(self.combo - 1, 0), 12)

    def score_kill(self, base=15):
        if self.mode == "time":
            return 0
        self.combo += 1
        payout = int(round(base * self.combo_mult()))
        self.score += payout
        if self.combo >= 3:
            self.play_sound("combo")
        return payout

    def award_bonus(self, base=50):
        if self.mode == "time":
            return 0
        payout = int(round(base * self.combo_mult()))
        self.score += payout
        return payout

    def level_up(self, new_level):
        now = time.perf_counter()
        self.level = new_level
        self.level_pause_until = now + 2.0
        self.level_effect_until = now + 2.0
        self.level_effect_start = now
        self.enemies.clear(); self.bullets.clear()
        self.enemy_timer = 0.0; self.power_timer = 0.0
        self.message = f"{self.t('level_up')}  •  {new_level}"
        self.message_until = now + 2.0
        self.spawn_particles(V_W/2, 90, CYAN, 40)
        self.play_sound("levelup")

    def shoot(self):
        if self.state != "playing" or self.shot_cooldown > 0:
            return
        self.shot_cooldown = 0.13
        self.bullets.append({"x": self.player_x, "y": self.player_y - self.player_r - 7, "speed": 16.0, "r": 5})
        self.play_sound("shoot")

    def move_player(self, left, right, up, down, dt):
        dx = float(right) - float(left); dy = float(down) - float(up)
        if dx == 0 and dy == 0:
            return
        n = math.hypot(dx, dy)
        s = 7.6 * dt * 60
        self.player_x = max(self.player_r, min(V_W-self.player_r, self.player_x + dx/n*s))
        self.player_y = max(60+self.player_r, min(V_H-85-self.player_r, self.player_y + dy/n*s))

    def update(self, dt):
        if self.state != "playing":
            return
        now = time.perf_counter()
        self.shot_cooldown = max(0, self.shot_cooldown - dt)
        self.survival_time = now - self.run_start

        new_level = self.current_level()
        if new_level > self.level:
            self.level_up(new_level)

        # Read touch controls from the UI.
        self.move_player(
            self.app_ui.left_btn.active,
            self.app_ui.right_btn.active,
            self.app_ui.up_btn.active,
            self.app_ui.down_btn.active,
            dt,
        )
        if self.app_ui.fire_btn.active:
            self.shoot()

        if now < self.level_pause_until:
            self.update_particles(dt)
            return

        self.enemy_timer += dt
        if self.enemy_timer >= self.enemy_spawn_interval():
            self.enemy_timer = 0.0
            self.spawn_enemy()

        self.power_timer += dt
        if self.power_timer >= 4.0:
            self.power_timer = 0.0
            self.spawn_powerup()

        for b in self.bullets[:]:
            b["y"] -= b["speed"] * dt * 60
            if b["y"] < -20:
                self.bullets.remove(b); continue
            hit = None
            for e in self.enemies:
                if math.hypot(e["x"]-b["x"], e["y"]-b["y"]) <= e["r"] + b["r"] + 2:
                    hit = e; break
            if hit:
                if b in self.bullets: self.bullets.remove(b)
                if hit in self.enemies: self.enemies.remove(hit)
                self.score_kill(15)
                self.spawn_particles(hit["x"], hit["y"], YELLOW, 14)
                self.play_sound("hit")

        for p in self.powerups[:]:
            p["y"] += p["speed"] * dt * 60
            p["pulse"] += dt * 7
            if p["y"] > V_H + 40:
                self.powerups.remove(p)

        for e in self.enemies[:]:
            e["y"] += e["speed"] * dt * 60
            e["phase"] += dt * 4.2
            e["x"] += math.sin(e["phase"]) * 0.65
            if e["y"] >= V_H - 70:
                self.enemies.remove(e)
                if self.mode != "endless":
                    self.lives -= 1
                    self.combo = 0
                    self.message = self.t("life_lost")
                    self.message_until = now + .65
                    self.spawn_particles(e["x"], V_H-70, RED, 20)
                    self.play_sound("life_lost")
                    if self.lives <= 0:
                        self.game_over(); return

        if self.mode != "endless" and now >= self.invulnerable_until:
            for e in self.enemies[:]:
                if math.hypot(e["x"]-self.player_x, e["y"]-self.player_y) <= e["r"] + self.player_r - 2:
                    self.enemies.remove(e)
                    self.lives -= 1; self.combo = 0
                    self.invulnerable_until = now + 1.0
                    self.message = self.t("life_lost"); self.message_until = now + .65
                    self.spawn_particles(self.player_x, self.player_y, RED, 26)
                    self.play_sound("life_lost")
                    if self.lives <= 0:
                        self.game_over(); return
                    break

        for p in self.powerups[:]:
            if math.hypot(p["x"]-self.player_x, p["y"]-self.player_y) <= p["r"] + self.player_r:
                self.powerups.remove(p)
                if p["kind"] == "heart":
                    self.lives = min(5, self.lives + 1)
                    self.message = self.t("life_plus")
                else:
                    amount = self.award_bonus(50)
                    self.message = f"+{amount}"
                self.message_until = now + .8
                self.play_sound("powerup")
                self.spawn_particles(p["x"], p["y"], GREEN if p["kind"] == "heart" else YELLOW, 16)

        self.update_particles(dt)

    def update_particles(self, dt):
        for p in self.particles[:]:
            p["x"] += p["vx"] * dt * 60; p["y"] += p["vy"] * dt * 60
            p["vy"] += 0.05 * dt * 60; p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

    # ----- drawing -----
    def tr(self, x, y):
        # Keep 16:9 virtual coordinates while fitting any non-fullscreen phone area.
        scale = min(self.width / V_W, self.height / V_H) if self.width and self.height else 1
        ox = (self.width - V_W*scale) / 2
        oy = (self.height - V_H*scale) / 2
        return ox + x*scale, oy + y*scale, scale

    def rect(self, x, y, w, h):
        X, Y, s = self.tr(x, y)
        return X, Y, w*s, h*s

    def redraw(self):
        self.canvas.clear()
        # Base background.
        with self.canvas:
            Color(*BG); Rectangle(pos=self.pos, size=self.size)
            Color(*GRID)
            _, _, s = self.tr(0, 0)
            for gx in range(0, int(V_W)+1, 64):
                x, y1, _ = self.tr(gx, 0); _, y2, _ = self.tr(gx, V_H)
                Line(points=[x, y1, x, y2], width=max(1, s))
            for gy in range(0, int(V_H)+1, 64):
                x1, y, _ = self.tr(0, gy); x2, _, _ = self.tr(V_W, gy)
                Line(points=[x1, y, x2, y], width=max(1, s))
            x1, y, _ = self.tr(0, V_H-70); x2, _, _ = self.tr(V_W, V_H-70)
            Color(23/255,48/255,84/255,1); Line(points=[x1,y,x2,y], width=max(2, s*2))

            if self.state == "playing" or self.state in ("paused", "gameover"):
                self.draw_world()
                if self.state == "paused":
                    self.draw_overlay(self.t("paused"), self.t("resume_text"), CYAN)
                elif self.state == "gameover":
                    self.draw_overlay_gameover()
            elif self.state == "menu":
                # Menu background only; actual labels/buttons are Kivy widgets.
                pass

    def draw_world(self):
        now = time.perf_counter()
        # powerups
        for p in self.powerups:
            x, y, s = self.tr(p["x"], p["y"])
            r = p["r"]*s
            fill = GREEN if p["kind"] == "heart" else YELLOW
            pulse = .5 + .5*math.sin(p["pulse"])
            Color(fill[0], fill[1], fill[2], .8)
            Line(circle=(x,y,r+7*s+pulse*3*s), width=max(1, 2*s))
            Color(fill[0], fill[1], fill[2], 1)
            Ellipse(pos=(x-r,y-r), size=(2*r,2*r))

        # enemies
        for e in self.enemies:
            x,y,s = self.tr(e["x"], e["y"]); r=e["r"]*s
            Color(0.2,0.09,0.17,1); Line(circle=(x,y,r+4*s), width=max(1,2*s))
            if e["kind"] == "diamond":
                Color(*RED)
                Triangle(points=[x, y+r, x+r, y, x, y-r])
            else:
                Color(*PINK); Ellipse(pos=(x-r,y-r), size=(2*r,2*r))
            Color(*YELLOW); Ellipse(pos=(x-r*.28,y-r*.28), size=(.56*r,.56*r))

        # bullets
        for b in self.bullets:
            x,y,s=self.tr(b["x"], b["y"])
            Color(0.09,0.25,0.39,1); Line(points=[x,y+16*s,x,y-16*s], width=max(3,7*s))
            Color(*CYAN); Line(points=[x,y+12*s,x,y-12*s], width=max(2,4*s))
            Color(*WHITE); Ellipse(pos=(x-4*s,y-4*s), size=(8*s,8*s))

        # player
        visible = not (now < self.invulnerable_until and int(now*16)%2==0)
        if visible:
            x,y,s=self.tr(self.player_x,self.player_y); r=self.player_r*s
            Color(0.09,0.25,0.39,1); Line(circle=(x,y,r+6*s), width=max(1,2*s))
            Color(*CYAN); Triangle(points=[x,y+r*-1.15, x+r,y+r*.9, x-r,y+r*.9])
            Color(*BG); Line(points=[x-9*s,y+5*s,x,y-8*s,x+9*s,y+5*s], width=max(1,2*s))

        # particles
        for p in self.particles:
            x,y,s=self.tr(p["x"],p["y"]); r=max(1,p["size"]*s*(p["life"]/.75))
            Color(*p["color"]); Ellipse(pos=(x-r,y-r), size=(2*r,2*r))

        if now < self.level_effect_until:
            elapsed = now - self.level_effect_start
            pulse = (math.sin(elapsed*12)+1)/2
            x,y,s=self.tr(V_W/2, 108)
            Color(*YELLOW); Line(circle=(x,y,34*s+12*pulse*s), width=max(2,3*s))
            Color(*CYAN); Line(points=[self.tr(55,135)[0],self.tr(55,135)[1],self.tr(V_W-55,135)[0],self.tr(V_W-55,135)[1]], width=max(2,3*s))

    def draw_overlay(self, title, subtitle, color):
        X,Y,s=self.tr(0,0)
        Color(0.02,0.04,0.09,0.70)
        Rectangle(pos=self.pos, size=self.size)
        # Text labels are handled by App UI layer.

    def draw_overlay_gameover(self):
        X,Y,s=self.tr(0,0)
        Color(0.02,0.04,0.09,0.76)
        Rectangle(pos=self.pos, size=self.size)

    def on_touch_down(self, touch):
        # Game-area tap does not replace the on-screen buttons.
        return super().on_touch_down(touch)

    def tick(self, dt):
        dt = min(0.04, max(0.001, dt))
        self.update(dt)
        self.redraw()
        self.app_ui.refresh_ui()


class NeonAppUI(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.field = NeonField(self)
        self.add_widget(self.field)

        self.title = Label(text="NEON DODGE", color=CYAN, bold=True, font_size=dp(38), size_hint=(1,None), height=dp(64), pos_hint={"x":0,"top":0.90})
        self.subtitle = Label(text="", color=WHITE, font_size=dp(16), size_hint=(1,None), height=dp(36), pos_hint={"x":0,"top":0.83})
        self.add_widget(self.title); self.add_widget(self.subtitle)

        self.lang_btn = self.make_button("فارسی", (0.77,0.90,0.11,0.07), self.change_language)
        self.exit_btn = self.make_button("✕ EXIT", (0.89,0.90,0.10,0.07), self.exit_game)

        self.mode_buttons = {}
        self._create_mode_buttons()
        self.start_btn = self.make_button("TAP TO START", (0.34,0.23,0.32,0.09), self.start_selected)

        self.menu_btn = self.make_button("☰ MENU", (0.015,0.92,0.12,0.06), self.back_menu)
        self.pause_btn = self.make_button("Ⅱ", (0.84,0.92,0.06,0.06), self.pause_toggle)

        self.hud_left = Label(text="", color=WHITE, bold=True, font_size=dp(15), size_hint=(None,None), size=(dp(300),dp(40)), pos_hint={"x":0.12,"top":0.99}, halign="left")
        self.hud_center = Label(text="", color=CYAN, bold=True, font_size=dp(14), size_hint=(None,None), size=(dp(300),dp(40)), pos_hint={"x":0.39,"top":0.99}, halign="center")
        self.hud_right = Label(text="", color=GREEN, bold=True, font_size=dp(13), size_hint=(None,None), size=(dp(300),dp(40)), pos_hint={"x":0.62,"top":0.99}, halign="right")
        self.message_label = Label(text="", color=YELLOW, bold=True, font_size=dp(18), size_hint=(0.8,None), height=dp(42), pos_hint={"x":0.10,"y":0.10}, halign="center")
        for w in (self.hud_left,self.hud_center,self.hud_right,self.message_label): self.add_widget(w)

        # Touch movement controls.
        self.left_btn = HoldButton(text="◀", accent="cyan")
        self.right_btn = HoldButton(text="▶", accent="cyan")
        self.up_btn = HoldButton(text="▲", accent="cyan")
        self.down_btn = HoldButton(text="▼", accent="cyan")
        self.fire_btn = HoldButton(text="FIRE", accent="green")
        self.add_widget(self.left_btn); self.add_widget(self.right_btn); self.add_widget(self.up_btn); self.add_widget(self.down_btn); self.add_widget(self.fire_btn)
        self._layout_touch_controls()
        self.bind(size=lambda *_: self._layout_touch_controls())

        self.gameover_title = Label(text="", color=PINK, bold=True, font_size=dp(38), size_hint=(1,None), height=dp(60), pos_hint={"x":0,"top":0.68})
        self.gameover_stats = Label(text="", color=WHITE, bold=True, font_size=dp(20), size_hint=(1,None), height=dp(80), pos_hint={"x":0,"top":0.58}, halign="center")
        self.gameover_again = self.make_button("TAP TO PLAY AGAIN", (0.30,0.28,0.40,0.09), self.play_again)
        self.gameover_menu = self.make_button("☰ MENU", (0.38,0.18,0.24,0.08), self.back_menu)
        self.add_widget(self.gameover_title); self.add_widget(self.gameover_stats)

        self.refresh_ui()

    def make_button(self, text, rel, callback):
        x,y,w,h = rel
        from kivy.uix.button import Button
        b = Button(text=text, size_hint=(w,h), pos_hint={"x":x,"y":y}, background_normal="", background_color=(18/255,28/255,50/255,0.88), color=WHITE, font_size=dp(12), bold=True)
        b.bind(on_release=callback)
        self.add_widget(b)
        return b

    def _create_mode_buttons(self):
        positions = {
            "classic": (0.07,0.34,0.27,0.20),
            "endless": (0.365,0.34,0.27,0.20),
            "time": (0.66,0.34,0.27,0.20),
        }
        for mode in MODE_KEYS:
            b = self.make_button("", positions[mode], lambda _b, m=mode: self.select_mode(m))
            self.mode_buttons[mode] = b

    def _layout_touch_controls(self):
        # Bottom-left D-pad and bottom-right fire, responsive to phone size.
        self.left_btn.size_hint = (0.09,0.11); self.left_btn.pos_hint={"x":0.045,"y":0.035}
        self.right_btn.size_hint = (0.09,0.11); self.right_btn.pos_hint={"x":0.215,"y":0.035}
        self.up_btn.size_hint = (0.09,0.11); self.up_btn.pos_hint={"x":0.13,"y":0.095}
        self.down_btn.size_hint = (0.09,0.11); self.down_btn.pos_hint={"x":0.13,"y":0.015}
        self.fire_btn.size_hint = (0.16,0.16); self.fire_btn.pos_hint={"x":0.79,"y":0.045}

    def change_language(self, *_):
        self.field.language = "fa" if self.field.language == "en" else "en"
        self.field.play_sound("select")
        self.refresh_ui()

    def exit_game(self, *_):
        self.field.save_records()
        App.get_running_app().stop()

    def select_mode(self, mode):
        self.field.selected_mode = mode
        self.field.play_sound("select")
        self.refresh_ui()

    def start_selected(self, *_):
        self.field.start_game(getattr(self.field, "selected_mode", "classic"))

    def play_again(self, *_):
        self.field.start_game(self.field.mode)

    def pause_toggle(self, *_):
        self.field.toggle_pause()

    def back_menu(self, *_):
        self.field.back_to_menu()

    def set_visible(self, widget, visible):
        widget.disabled = not visible
        widget.opacity = 1 if visible else 0

    def refresh_ui(self, *_):
        lang = self.field.language
        state = self.field.state
        mode = self.field.mode

        self.title.text = "NEON DODGE"
        self.subtitle.text = TEXT[lang]["choose"] if state == "menu" else ""
        self.lang_btn.text = TEXT[lang]["language"]
        self.exit_btn.text = TEXT[lang]["exit"]

        # Menu.
        menu = state == "menu"
        self.set_visible(self.lang_btn, True)
        self.set_visible(self.exit_btn, True)
        self.set_visible(self.title, menu)
        self.set_visible(self.subtitle, menu)
        self.set_visible(self.start_btn, menu)
        for m,b in self.mode_buttons.items():
            self.set_visible(b, menu)
            selected = (m == getattr(self.field, "selected_mode", "classic"))
            names = {
                "classic": (TEXT[lang]["classic"], TEXT[lang]["classic_desc"]),
                "endless": (TEXT[lang]["endless"], TEXT[lang]["endless_desc"]),
                "time": (TEXT[lang]["time"], TEXT[lang]["time_desc"]),
            }
            b.text = f"{names[m][0]}\n{names[m][1]}\n\n{TEXT[lang]['play']}"
            b.background_color = (24/255,39/255,64/255,1) if selected else (13/255,22/255,40/255,1)
        self.start_btn.text = TEXT[lang]["start"]
        self.start_btn.disabled = not menu; self.start_btn.opacity = 1 if menu else 0

        # Top in-game controls.
        in_game = state in ("playing", "paused", "gameover")
        self.set_visible(self.menu_btn, in_game)
        self.set_visible(self.pause_btn, state in ("playing", "paused"))

        # HUD.
        show_hud = in_game
        self.set_visible(self.hud_left, show_hud)
        self.set_visible(self.hud_center, show_hud)
        self.set_visible(self.hud_right, show_hud)
        if show_hud:
            if mode == "time":
                self.hud_left.text = f"{TEXT[lang]['time']}  {self.format_time(self.field.survival_time)}"
            else:
                self.hud_left.text = f"{TEXT[lang]['score']}  {self.field.score:05d}"
            self.hud_center.text = f"{TEXT[lang]['level']} {self.field.level}"
            self.hud_right.text = TEXT[lang]["endless_hud"] if mode == "endless" else f"{TEXT[lang]['lives']}  {'♥' * self.field.lives}"
            self.pause_btn.text = TEXT[lang]["resume"] if state == "paused" else TEXT[lang]["pause"]

        # Touch controls only during live gameplay.
        for b in (self.left_btn,self.right_btn,self.up_btn,self.down_btn,self.fire_btn):
            self.set_visible(b, state == "playing")
        self.message_label.text = self.field.message if time.perf_counter() < self.field.message_until else ""
        self.set_visible(self.message_label, state == "playing" and bool(self.message_label.text))

        # Overlay labels.
        is_go = state == "gameover"
        self.set_visible(self.gameover_title, is_go)
        self.set_visible(self.gameover_stats, is_go)
        self.set_visible(self.gameover_again, is_go)
        self.set_visible(self.gameover_menu, is_go)
        if is_go:
            self.gameover_title.text = TEXT[lang]["gameover"] if mode != "endless" else TEXT[lang]["runover"]
            if mode == "time":
                self.gameover_stats.text = f"{TEXT[lang]['time']}  {self.format_time(self.field.survival_time)}\n{TEXT[lang]['best']}  {self.format_time(self.field.best_time)}"
            elif mode == "classic":
                self.gameover_stats.text = f"{TEXT[lang]['score']}  {self.field.score:05d}\n{TEXT[lang]['best']}  {self.field.best_score:05d}"
            else:
                self.gameover_stats.text = f"{TEXT[lang]['score']}  {self.field.score:05d}"
            self.gameover_again.text = TEXT[lang]["again"]
            self.gameover_menu.text = TEXT[lang]["menu"]

    def format_time(self, seconds):
        m = int(seconds // 60); s = seconds % 60
        return f"{m:02d}:{s:05.2f}"


class NeonDodgeApp(App):
    title = "Neon Dodge"

    def build(self):
        self.icon = str(Path(__file__).resolve().parent / "data" / "neondodge_icon.png")
        # Fullscreen intentionally disabled for mobile: system bars remain available.
        try:
            Window.fullscreen = False
            Window.show_cursor = False
        except Exception:
            pass
        return NeonAppUI()

    def on_pause(self):
        # Android can pause the app when the user backgrounds it.
        return True

    def on_stop(self):
        try:
            self.root.field.save_records()
        except Exception:
            pass


if __name__ == "__main__":
    NeonDodgeApp().run()
