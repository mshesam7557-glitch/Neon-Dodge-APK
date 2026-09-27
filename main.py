from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse, Line, Polygon
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from random import randint, uniform, choice
from math import sin, cos, pi, hypot
import json
from pathlib import Path

W, H = 900, 600
FPS = 1 / 60

TEXT = {
    'en': {
        'title': 'NEON DODGE', 'choose': 'Choose your game mode',
        'classic': 'CLASSIC', 'classic_desc': '5 lives • score • dodge • shoot',
        'endless': 'ENDLESS', 'endless_desc': 'No lives • no death • survive forever',
        'time': 'TIME ATTACK', 'time_desc': 'Beat your survival time record',
        'play': 'PLAY', 'menu': 'MENU', 'exit': 'EXIT', 'lang': 'فارسی',
        'pause': 'PAUSE', 'resume': 'RESUME', 'shoot': 'FIRE',
        'start_help': '← / → or A / D = choose mode   •   Enter / Space = start',
        'score': 'SCORE', 'lives': 'LIVES', 'level': 'LEVEL', 'time': 'TIME',
        'best': 'BEST', 'game_over': 'GAME OVER', 'play_again': 'PLAY AGAIN',
        'new_record': 'NEW RECORD!', 'level_up': 'LEVEL UP!',
        'life': '-1 LIFE', 'life_plus': '+1 LIFE', 'bonus': '+BONUS',
        'endless_hud': 'ENDLESS • ∞ LIVES',
    },
    'fa': {
        'title': 'نئون داج', 'choose': 'حالت بازی را انتخاب کن',
        'classic': 'کلاسیک', 'classic_desc': '۵ جان • امتیاز • جاخالی • شلیک',
        'endless': 'بی‌نهایت', 'endless_desc': 'بدون جان • بدون مرگ • تا هر وقت بخواهی',
        'time': 'حمله زمانی', 'time_desc': 'رکورد زمان زنده ماندن را بشکن',
        'play': 'شروع', 'menu': 'منو', 'exit': 'خروج', 'lang': 'English',
        'pause': 'توقف', 'resume': 'ادامه', 'shoot': 'شلیک',
        'start_help': '← / → یا A / D = انتخاب حالت   •   Enter / Space = شروع',
        'score': 'امتیاز', 'lives': 'جان', 'level': 'مرحله', 'time': 'زمان',
        'best': 'رکورد', 'game_over': 'بازی تمام شد', 'play_again': 'دوباره بازی کن',
        'new_record': 'رکورد جدید!', 'level_up': 'مرحله بالاتر!',
        'life': '-۱ جان', 'life_plus': '+۱ جان', 'bonus': '+امتیاز',
        'endless_hud': 'بی‌نهایت • ∞ جان',
    }
}

MODES = ['classic', 'endless', 'time']

class GameWidget(Widget):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.mode = 'classic'
        self.state = 'menu'
        self.lang = 'en'
        self.keys = set()
        self.score = 0
        self.lives = 5
        self.level = 1
        self.combo = 0
        self.survival = 0.0
        self.best_time = 0.0
        self.best_score = 0
        self.start_time = 0.0
        self.level_flash = 0.0
        self.level_break = 0.0
        self.enemy_spawn = 0.0
        self.power_spawn = 0.0
        self.shot_cd = 0.0
        self.player = [0.5, 0.15]
        self.enemies = []
        self.bullets = []
        self.powerups = []
        self.load_records()
        Clock.schedule_interval(self.update, FPS)

        Window.bind(on_key_down=self.key_down, on_key_up=self.key_up)

    def t(self, k):
        return TEXT[self.lang][k]

    def load_records(self):
        p = Path(App.get_running_app().user_data_dir) / 'records.json'
        try:
            d = json.loads(p.read_text())
            self.best_time = float(d.get('best_time', 0))
            self.best_score = int(d.get('best_score', 0))
        except Exception:
            pass

    def save_records(self):
        p = Path(App.get_running_app().user_data_dir) / 'records.json'
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({'best_time': self.best_time, 'best_score': self.best_score}))
        except Exception:
            pass

    def key_down(self, window, key, scancode, codepoint, modifiers):
        # Physical scancodes 26/8/20/44 are used for WASD so the game works
        # even when the Android/PC keyboard layout is Persian.
        if key == 282:  # F3: language toggle on desktop debug builds.
            self.lang = 'fa' if self.lang == 'en' else 'en'; self.redraw(); return True
        if key in (276, 1073741904): self.menu_move(-1); return True
        if key in (275, 1073741903): self.menu_move(1); return True
        if key in (13, 32):
            if self.state == 'menu': self.start(self.mode)
            elif self.state == 'gameover': self.start(self.mode)
            elif self.state == 'paused': self.state = 'playing'
            return True
        if key == 27:
            if self.state == 'playing': self.state = 'paused'
            elif self.state == 'paused': self.state = 'playing'
            self.redraw(); return True
        self.keys.add(key)
        return False

    def key_up(self, window, key, *args):
        self.keys.discard(key)

    def menu_move(self, d):
        if self.state != 'menu': return
        self.mode = MODES[(MODES.index(self.mode) + d) % len(MODES)]
        self.redraw()

    def start(self, mode):
        self.mode = mode
        self.state = 'playing'
        self.score = 0; self.lives = 5; self.level = 1; self.combo = 0
        self.survival = 0.0; self.start_time = Clock.get_time()
        self.level_flash = 0.0; self.level_break = 0.0
        self.enemy_spawn = 0; self.power_spawn = 0; self.shot_cd = 0
        self.player = [0.5, 0.15]
        self.enemies.clear(); self.bullets.clear(); self.powerups.clear()
        self.redraw()

    def game_over(self):
        self.state = 'gameover'
        if self.mode == 'time':
            if self.survival > self.best_time:
                self.best_time = self.survival
                self.message = self.t('new_record')
        elif self.mode == 'classic':
            if self.score > self.best_score:
                self.best_score = self.score
        self.save_records(); self.redraw()

    def shoot(self):
        if self.state != 'playing' or self.shot_cd > 0: return
        self.shot_cd = 0.14
        self.bullets.append({'x': self.player[0], 'y': self.player[1] + 0.05, 'v': 1.35})
        self.redraw()

    def spawn_enemy(self):
        self.enemies.append({'x': uniform(0.04, .96), 'y': 1.06, 'r': uniform(.018, .029),
                             'v': uniform(.34, .48) + self.level * .035,
                             'phase': uniform(0, 2*pi), 'kind': choice(['orb','diamond'])})

    def spawn_power(self):
        if self.mode == 'endless': return
        kind = 'life' if self.mode == 'time' else choice(['life','score'])
        self.powerups.append({'x': uniform(.06,.94), 'y': 1.05, 'r': .024, 'v': .23, 'kind': kind, 'phase': 0})

    def update(self, dt):
        if self.state != 'playing':
            self.redraw(); return
        now = Clock.get_time()
        self.shot_cd = max(0, self.shot_cd - dt)
        self.survival = now - self.start_time

        # Leveling: each mode has a different, much slower progression.
        old_level = self.level
        if self.mode == 'classic': self.level = 1 + self.score // 750
        elif self.mode == 'endless': self.level = 1 + int(self.survival // 45)
        else: self.level = 1 + int(self.survival // 50)
        if self.level != old_level:
            self.level_flash = 2.0
            self.level_break = 1.8
            self.enemies.clear()
            self.bullets.clear()

        # During level-break, do not spawn enemies for a moment.
        self.level_flash = max(0, self.level_flash - dt)
        self.level_break = max(0, self.level_break - dt)

        speed = 0.55 * dt
        dx = dy = 0
        # WASD physical keys + arrows.
        if 97 in self.keys or 30 in self.keys or 276 in self.keys: dx -= 1
        if 100 in self.keys or 33 in self.keys or 275 in self.keys: dx += 1
        if 119 in self.keys or 17 in self.keys or 273 in self.keys: dy += 1
        if 115 in self.keys or 31 in self.keys or 274 in self.keys: dy -= 1
        if dx or dy:
            l = hypot(dx,dy)
            self.player[0] = min(.96, max(.04, self.player[0] + dx/l * speed))
            self.player[1] = min(.90, max(.08, self.player[1] + dy/l * speed))

        self.enemy_spawn += dt
        base = max(.22, .92 - self.level*.045)
        if self.level_break <= 0 and self.enemy_spawn >= base:
            # Multiple spawns on higher levels.
            self.enemy_spawn = 0
            count = 1 + (1 if self.level >= 4 and randint(0,2)==0 else 0) + (1 if self.level >= 8 and randint(0,3)==0 else 0)
            for _ in range(count): self.spawn_enemy()

        if self.mode != 'endless':
            self.power_spawn += dt
            if self.power_spawn >= 4.2:
                self.power_spawn = 0
                self.spawn_power()

        for b in self.bullets[:]:
            b['y'] += b['v'] * dt
            if b['y'] > 1.15: self.bullets.remove(b); continue
            hit = None
            for e in self.enemies:
                if hypot(e['x']-b['x'], e['y']-b['y']) < e['r'] + .012:
                    hit = e; break
            if hit:
                if b in self.bullets: self.bullets.remove(b)
                if hit in self.enemies: self.enemies.remove(hit)
                self.combo += 1
                if self.mode != 'time': self.score += 15 * min(self.combo, 6)

        for e in self.enemies[:]:
            e['y'] -= e['v'] * dt
            e['x'] += sin(e['phase'] + now*3) * .0006
            if e['y'] < .05:
                self.enemies.remove(e)
                if self.mode != 'endless':
                    self.lives -= 1; self.combo = 0
                    if self.lives <= 0: self.game_over(); return
                continue
            if self.mode != 'endless' and hypot(e['x']-self.player[0], e['y']-self.player[1]) < e['r'] + .028:
                self.enemies.remove(e); self.lives -= 1; self.combo = 0
                if self.lives <= 0: self.game_over(); return

        for p in self.powerups[:]:
            p['y'] -= p['v'] * dt
            p['phase'] += dt*4
            if p['y'] < -.08: self.powerups.remove(p); continue
            if hypot(p['x']-self.player[0], p['y']-self.player[1]) < p['r'] + .035:
                self.powerups.remove(p)
                if p['kind'] == 'life': self.lives = min(5, self.lives+1)
                else: self.score += 50 * max(1, min(self.combo, 6))

        self.redraw()

    def draw_bg(self):
        Color(.02,.04,.09); Rectangle(pos=self.pos,size=self.size)
        Color(.05,.09,.16,.8)
        for x in range(0, 901, 50): Line(points=[self.x+x*self.width/900, self.y, self.x+x*self.width/900, self.y+self.height], width=.7)
        for y in range(0, 601, 50): Line(points=[self.x, self.y+y*self.height/600, self.x+self.width, self.y+y*self.height/600], width=.7)

    def norm(self,x,y): return (self.x+x*self.width, self.y+y*self.height)

    def redraw(self):
        self.canvas.clear(); self.draw_bg()
        if self.state == 'menu': self.draw_menu(); return
        self.draw_world()
        if self.state == 'paused': self.draw_overlay(self.t('pause'), self.t('resume'))
        if self.state == 'gameover': self.draw_gameover()

    def draw_player(self):
        x,y=self.norm(*self.player); r=.03*self.height
        Color(0.26,0.96,1); Polygon(points=[x,y+r,x+r*.9,y-r*.6,x,y-r*.2,x-r*.9,y-r*.6])
        Color(1,1,1); Line(points=[x,y+r,x+r*.9,y-r*.6,x,y-r*.2,x-r*.9,y-r*.6,x,y+r],width=1.2)

    def draw_world(self):
        for e in self.enemies:
            x,y=self.norm(e['x'],e['y']); r=e['r']*self.height
            Color(1,.24,.67,.28); Line(circle=(x,y,r+8),width=2)
            Color(1,.24,.67); Ellipse(pos=(x-r,y-r),size=(2*r,2*r))
        for b in self.bullets:
            x,y=self.norm(b['x'],b['y']); r=5
            Color(.26,.96,1,.25); Line(points=[x,y,x,y-20],width=6)
            Color(.26,.96,1); Line(points=[x,y,x,y-18],width=3)
        for p in self.powerups:
            x,y=self.norm(p['x'],p['y']); r=p['r']*self.height
            Color(.4,1,.7,.3); Line(circle=(x,y,r+8+sin(p['phase'])*3),width=2)
            Color(.4,1,.7) if p['kind']=='life' else Color(1,.9,.35)
            Ellipse(pos=(x-r,y-r),size=(2*r,2*r))
        self.draw_player()
        self.draw_hud()

    def draw_hud(self):
        Color(1,1,1)
        if self.mode == 'time':
            Label(text=f"{self.t('time')} {int(self.survival//60):02d}:{self.survival%60:05.2f}", pos=(20,self.height-55), size=(250,40)).texture_update();
        # Labels are handled with transient widgets by MobileApp overlay.

    def draw_menu(self): pass
    def draw_overlay(self, a,b): pass
    def draw_gameover(self): pass

class MobileApp(App):
    def build(self):
        Window.clearcolor=(.02,.04,.09,1)
        self.root = FloatLayout()
        self.game = GameWidget(self)
        self.root.add_widget(self.game)
        self.labels=[]
        self.make_ui()
        return self.root

    def add_label(self, **kwargs):
        w=Label(**kwargs); self.root.add_widget(w); self.labels.append(w); return w

    def clear_labels(self):
        for w in self.labels:
            if w.parent: w.parent.remove_widget(w)
        self.labels=[]

    def make_ui(self):
        # Touch controls; UI is rebuilt every frame to keep language/game state simple.
        Clock.schedule_interval(self.refresh_ui, 1/30)

    def btn(self, text, x, y, w, h, action, fs=14):
        b=Button(text=text, size_hint=(None,None), size=(w,h), pos_hint={'x':x,'y':y}, font_size=fs)
        b.bind(on_release=lambda *_: action()); self.root.add_widget(b); self.labels.append(b); return b

    def refresh_ui(self, dt):
        self.clear_labels()
        g=self.game
        if g.state=='menu':
            self.add_label(text=g.t('title'), font_size='34sp', size_hint=(1,None), height=60, pos_hint={'x':0,'y':.77})
            self.add_label(text=g.t('choose'), font_size='16sp', size_hint=(1,None), height=40, pos_hint={'x':0,'y':.68})
            xs=[.07,.36,.65]
            for i,m in enumerate(MODES):
                b=self.btn(g.t(m), xs[i], .42, .28, .20, lambda m=m:g.start(m), 16)
                if g.mode==m: b.background_color=(.15,.65,1,1)
                self.add_label(text=g.t(m+'_desc'), font_size='11sp', size_hint=(.27,None), height=55, pos_hint={'x':xs[i]+.005,'y':.39})
            self.btn('←',.12,.25,.16,.11,lambda:g.menu_move(-1),22); self.btn('→',.72,.25,.16,.11,lambda:g.menu_move(1),22)
            self.btn(g.t('play'),.41,.22,.18,.10,lambda:g.start(g.mode),14)
            self.btn(g.t('lang'),.82,.88,.15,.08,lambda:self.toggle_lang(),11)
            return
        # game HUD
        mode=g.mode
        if mode=='time': hud=f"{g.t('time')} {int(g.survival//60):02d}:{g.survival%60:05.2f}   {g.t('level')} {g.level}"
        elif mode=='endless': hud=f"{g.t('score')} {g.score:05d}   {g.t('level')} {g.level}   ∞"
        else: hud=f"{g.t('score')} {g.score:05d}   {g.t('level')} {g.level}   {g.t('lives')} {'♥'*g.lives}"
        self.add_label(text=hud, font_size='15sp', size_hint=(.8,None),height=40,pos_hint={'x':.1,'y':.90})
        self.btn('←',.02,.08,.14,.10,lambda:self.move(-1),22)
        self.btn('→',.18,.08,.14,.10,lambda:self.move(1),22)
        self.btn('↑',.10,.19,.14,.10,lambda:self.move(0,1),22)
        self.btn('↓',.10,.01,.14,.10,lambda:self.move(0,-1),22)
        self.btn(g.t('shoot'),.78,.04,.18,.15,lambda:g.shoot(),13)
        self.btn('Ⅱ' if g.state=='playing' else '▶',.84,.87,.11,.08,lambda:self.pause(),12)
        self.btn(g.t('menu'),.70,.87,.13,.08,lambda:self.menu(),11)
        self.btn(g.t('lang'),.46,.88,.15,.08,lambda:self.toggle_lang(),11)
        if g.level_flash>0:
            self.add_label(text=g.t('level_up'),font_size='28sp',size_hint=(1,None),height=55,pos_hint={'x':0,'y':.48})

    def move(self,dx=0,dy=0):
        x,y=self.game.player; self.game.player=[min(.96,max(.04,x+dx*.05)),min(.90,max(.08,y+dy*.05))]
    def pause(self):
        if self.game.state=='playing': self.game.state='paused'
        elif self.game.state=='paused': self.game.state='playing'
    def menu(self): self.game.show_menu()
    def toggle_lang(self): self.game.lang='fa' if self.game.lang=='en' else 'en'

    def on_stop(self):
        self.game.save_records()

if __name__=='__main__':
    MobileApp().run()
