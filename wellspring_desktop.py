"""
Wellspring Desktop — Wellness Reminder App
==========================================
Runs in your system tray and fires OS-level popups, sound effects,
and text-to-speech reminders for water, bathroom breaks, stretching,
and hourly motivation.

Install dependencies:
    pip install plyer pyttsx3 pygame tkinter

Then run:
    python wellspring_desktop.py
"""

import threading
import time
import random
import tkinter as tk
from tkinter import ttk
import pyttsx3
import math
try:
    from plyer import notification as plyer_notif
    PLYER_OK = True
except ImportError:
    PLYER_OK = False

# ── QUOTES ────────────────────────────────────────────────────────────────────
QUOTES = [
    ("The secret of getting ahead is getting started.", "Mark Twain"),
    ("You are braver than you believe, stronger than you seem.", "A.A. Milne"),
    ("It does not matter how slowly you go as long as you do not stop.", "Confucius"),
    ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
    ("Everything you've ever wanted is on the other side of fear.", "George Addair"),
    ("Success is not final, failure is not fatal: courage to continue counts.", "Winston Churchill"),
    ("Push yourself, because no one else is going to do it for you.", "Unknown"),
    ("Great things never come from comfort zones.", "Unknown"),
    ("The harder you work, the greater you'll feel when you achieve it.", "Unknown"),
    ("Don't stop when you're tired. Stop when you're done.", "Unknown"),
    ("Wake up with determination. Go to bed with satisfaction.", "Unknown"),
    ("It's going to be hard, but hard is not impossible.", "Unknown"),
    ("Don't wait for opportunity. Create it.", "Unknown"),
    ("The key to success is to focus on goals, not obstacles.", "Unknown"),
    ("Dream it. Wish it. Do it.", "Unknown"),
    ("You didn't come this far to only come this far.", "Unknown"),
    ("Small steps every day lead to big results.", "Unknown"),
    ("Be so good they can't ignore you.", "Steve Martin"),
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("In the middle of every difficulty lies opportunity.", "Albert Einstein"),
]

# ── REMINDER DEFINITIONS ──────────────────────────────────────────────────────
REMINDERS = {
    "water": {
        "emoji": "💧",
        "title": "Time to Hydrate!",
        "message": "A glass of water keeps your brain sharp and your energy up.\nTake a sip right now!",
        "speech": "Hey! It's time to drink some water. Stay hydrated!",
        "color": "#60a5fa",
        "default_interval": 20,
    },
    "pee": {
        "emoji": "🚽",
        "title": "Bathroom Break!",
        "message": "Your body has been working hard.\nTake a quick bathroom break — you deserve it!",
        "speech": "Time for a bathroom break! Take a moment for yourself.",
        "color": "#fbbf24",
        "default_interval": 60,
    },
    "break": {
        "emoji": "🧘",
        "title": "Stand Up & Stretch!",
        "message": "You've been sitting too long!\nStand up, stretch those muscles, and take 3 deep breaths.",
        "speech": "Stand up and stretch! Your body needs movement. Take three deep breaths.",
        "color": "#2dd4bf",
        "default_interval": 45,
    },
    "motivate": {
        "emoji": "🔥",
        "title": "Motivation Boost!",
        "message": "",  # filled dynamically with quote
        "speech": "",   # filled dynamically
        "color": "#fb7185",
        "default_interval": 60,
    },
}

# ── TTS ENGINE ────────────────────────────────────────────────────────────────
_tts_lock = threading.Lock()

def speak(text):
    def _speak():
        with _tts_lock:
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 160)
                engine.setProperty('volume', 0.9)
                voices = engine.getProperty('voices')
                # prefer a female English voice
                for v in voices:
                    if 'en' in v.languages[0].decode() if isinstance(v.languages[0], bytes) else 'en' in v.languages[0]:
                        engine.setProperty('voice', v.id)
                        break
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"[TTS] {e}")
    threading.Thread(target=_speak, daemon=True).start()

# ── POPUP WINDOW ──────────────────────────────────────────────────────────────
class PopupWindow:
    def __init__(self, reminder_type, title, message, color, on_dismiss, on_snooze):
        self.on_dismiss = on_dismiss
        self.on_snooze  = on_snooze
        self.root = tk.Tk()
        self.root.title("Wellspring")
        self.root.configure(bg="#0a0f0d")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(False)

        # Center on screen
        w, h = 420, 320
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # Fade-in animation vars
        self.alpha = 0.0
        self.root.attributes('-alpha', 0.0)

        # ── Canvas for background ──
        self.canvas = tk.Canvas(self.root, bg="#0a0f0d", highlightthickness=0, width=w, height=h)
        self.canvas.pack(fill='both', expand=True)

        # Glow circle at top
        self.canvas.create_oval(w//2-120, -60, w//2+120, 120,
            fill=self._hex_fade(color, 0.12), outline='')

        # Emoji
        emoji = REMINDERS[reminder_type]['emoji']
        self.canvas.create_text(w//2, 80, text=emoji, font=('Segoe UI Emoji', 36))

        # Title
        self.canvas.create_text(w//2, 135, text=title, fill='#e8f5ee',
            font=('Georgia', 18, 'bold'), anchor='center')

        # Message (word-wrapped)
        msg_lines = message.split('\n')
        y_off = 170
        for line in msg_lines:
            self.canvas.create_text(w//2, y_off, text=line, fill='#6b8f76',
                font=('Helvetica', 11), anchor='center')
            y_off += 22

        # Buttons
        btn_frame = tk.Frame(self.canvas, bg="#0a0f0d")
        self.canvas.create_window(w//2, 270, window=btn_frame)

        dismiss_btn = tk.Button(
            btn_frame, text="Got it! ✓", command=self._dismiss,
            bg=color, fg='#0a0f0d', font=('Helvetica', 11, 'bold'),
            relief='flat', padx=22, pady=8, cursor='hand2',
            activebackground=color, bd=0
        )
        dismiss_btn.pack(side='left', padx=6)

        snooze_btn = tk.Button(
            btn_frame, text="Snooze 5m", command=self._snooze,
            bg='#162019', fg='#6b8f76', font=('Helvetica', 10),
            relief='flat', padx=16, pady=8, cursor='hand2',
            activebackground='#1e3326', bd=0
        )
        snooze_btn.pack(side='left', padx=6)

        # Close on Escape
        self.root.bind('<Escape>', lambda e: self._dismiss())

        # Fade in
        self._fade_in()

    def _hex_fade(self, hex_color, alpha):
        """Returns a slightly-transparent approximation by blending with bg."""
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            br, bg2, bb = 10, 15, 13
            nr = int(br + (r - br) * alpha)
            ng = int(bg2 + (g - bg2) * alpha)
            nb = int(bb + (b - bb) * alpha)
            return f'#{nr:02x}{ng:02x}{nb:02x}'
        except:
            return '#162019'

    def _fade_in(self):
        self.alpha += 0.07
        if self.alpha < 1.0:
            self.root.attributes('-alpha', min(self.alpha, 1.0))
            self.root.after(20, self._fade_in)
        else:
            self.root.attributes('-alpha', 1.0)

    def _dismiss(self):
        self.root.destroy()
        if self.on_dismiss:
            self.on_dismiss()

    def _snooze(self):
        self.root.destroy()
        if self.on_snooze:
            self.on_snooze()

    def show(self):
        self.root.mainloop()

# ── MAIN APP ──────────────────────────────────────────────────────────────────
class WellspringApp:
    def __init__(self):
        self.running = False
        self.timers = {k: 0 for k in REMINDERS}
        self.intervals = {k: REMINDERS[k]['default_interval'] for k in REMINDERS}
        self.quote_idx = 0
        self.session_seconds = 0
        self.popup_active = False
        self._snooze_timers = {}

        # Build main control window
        self._build_ui()

    def _build_ui(self):
        self.root = tk.Tk()
        self.root.title("🌿 Wellspring — Wellness Reminders")
        self.root.configure(bg="#0a0f0d")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        w, h = 480, 600
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{sw-w-20}+{sh-h-60}")

        # ── Header ──
        header = tk.Frame(self.root, bg="#0a0f0d", pady=20)
        header.pack(fill='x', padx=24)

        tk.Label(header, text="🌿 Wellspring", bg="#0a0f0d", fg="#4ade80",
                 font=('Georgia', 22, 'bold')).pack(side='left')

        self.status_label = tk.Label(header, text="● Idle", bg="#0a0f0d",
                                      fg="#6b8f76", font=('Helvetica', 10))
        self.status_label.pack(side='right', pady=6)

        # ── Session timer ──
        timer_frame = tk.Frame(self.root, bg="#111a15", pady=16)
        timer_frame.pack(fill='x', padx=24, pady=(0,16))

        tk.Label(timer_frame, text="SESSION TIME", bg="#111a15", fg="#6b8f76",
                 font=('Helvetica', 8)).pack()

        self.timer_label = tk.Label(timer_frame, text="00:00:00", bg="#111a15",
                                     fg="#4ade80", font=('Courier', 32, 'bold'))
        self.timer_label.pack()

        # ── Buttons ──
        btn_frame = tk.Frame(self.root, bg="#0a0f0d")
        btn_frame.pack(pady=(0,16))

        self.start_btn = tk.Button(
            btn_frame, text="▶  Start Session", command=self.toggle_session,
            bg="#4ade80", fg="#0a0f0d", font=('Helvetica', 11, 'bold'),
            relief='flat', padx=20, pady=8, cursor='hand2'
        )
        self.start_btn.pack(side='left', padx=6)

        tk.Button(
            btn_frame, text="↺ Reset", command=self.reset_session,
            bg="#162019", fg="#6b8f76", font=('Helvetica', 10),
            relief='flat', padx=14, pady=8, cursor='hand2'
        ).pack(side='left', padx=6)

        tk.Button(
            btn_frame, text="🧪 Test", command=self.test_reminder,
            bg="#162019", fg="#6b8f76", font=('Helvetica', 10),
            relief='flat', padx=14, pady=8, cursor='hand2'
        ).pack(side='left', padx=6)

        # ── Reminder interval controls ──
        controls = tk.Frame(self.root, bg="#0a0f0d")
        controls.pack(fill='x', padx=24)

        self.interval_labels = {}
        self.next_labels = {}

        row_data = [
            ("water",    "💧 Drink Water",     5,  60,  5),
            ("pee",      "🚽 Bathroom Break",  30, 180, 15),
            ("break",    "🧘 Stand & Stretch", 20, 120, 5),
            ("motivate", "🔥 Motivation",      30, 120, 15),
        ]

        for key, label, mn, mx, step in row_data:
            row = tk.Frame(controls, bg="#111a15", pady=8)
            row.pack(fill='x', pady=4)
            row.columnconfigure(1, weight=1)

            color = REMINDERS[key]['color']

            # Label
            tk.Label(row, text=label, bg="#111a15", fg="#e8f5ee",
                     font=('Helvetica', 10, 'bold'), width=18, anchor='w').grid(
                     row=0, column=0, padx=(12,6), pady=2)

            # Slider
            var = tk.IntVar(value=self.intervals[key])
            slider = ttk.Scale(row, from_=mn, to=mx, variable=var, orient='horizontal',
                               command=lambda v, k=key, _var=var: self._update_interval(k, _var))
            slider.grid(row=0, column=1, padx=6, sticky='ew')

            # Value label
            val_lbl = tk.Label(row, text=f"{self.intervals[key]}m", bg="#111a15",
                                fg=color, font=('Helvetica', 9), width=5)
            val_lbl.grid(row=0, column=2, padx=4)
            self.interval_labels[key] = (var, val_lbl)

            # Next label
            next_lbl = tk.Label(row, text=f"Next in {self.intervals[key]}m", bg="#111a15",
                                  fg="#6b8f76", font=('Helvetica', 8), anchor='w')
            next_lbl.grid(row=1, column=0, columnspan=3, padx=12, sticky='w')
            self.next_labels[key] = next_lbl

        # ── Quote ──
        q_frame = tk.Frame(self.root, bg="#111a15", pady=12)
        q_frame.pack(fill='x', padx=24, pady=(16,0))

        tk.Label(q_frame, text="✦ MOTIVATION", bg="#111a15", fg="#fb7185",
                 font=('Helvetica', 7)).pack(pady=(0,4))

        q = random.choice(QUOTES)
        self.quote_label = tk.Label(q_frame, text=f'"{q[0]}"', bg="#111a15",
                                     fg="#e8f5ee", font=('Georgia', 10, 'italic'),
                                     wraplength=400, justify='center')
        self.quote_label.pack()
        tk.Label(q_frame, text=f"— {q[1]}", bg="#111a15", fg="#6b8f76",
                 font=('Helvetica', 8)).pack(pady=(4,0))

        # ── Log ──
        log_frame = tk.Frame(self.root, bg="#0a0f0d")
        log_frame.pack(fill='both', expand=True, padx=24, pady=16)

        tk.Label(log_frame, text="ACTIVITY LOG", bg="#0a0f0d", fg="#6b8f76",
                 font=('Helvetica', 7)).pack(anchor='w')

        self.log_box = tk.Text(log_frame, bg="#0a0f0d", fg="#6b8f76",
                                font=('Courier', 9), height=6, relief='flat',
                                state='disabled', wrap='word')
        self.log_box.pack(fill='both', expand=True)
        self._log("🌱 Wellspring ready. Press Start to begin.")

    def _update_interval(self, key, var):
        val = int(var.get())
        # snap to nearest 5
        val = round(val / 5) * 5
        self.intervals[key] = max(1, val)
        self.timers[key] = 0
        lbl = self.interval_labels[key][1]
        lbl.config(text=f"{val}m")
        self.next_labels[key].config(text=f"Next in {val}m")

    def _log(self, msg):
        now = time.strftime('%H:%M')
        self.log_box.config(state='normal')
        self.log_box.insert('1.0', f"[{now}] {msg}\n")
        self.log_box.config(state='disabled')

    def toggle_session(self):
        self.running = not self.running
        if self.running:
            self.start_btn.config(text="⏸  Pause")
            self.status_label.config(text="● Active", fg="#4ade80")
            self._log("Session started 🌱")
            self._run_tick()
        else:
            self.start_btn.config(text="▶  Resume")
            self.status_label.config(text="● Paused", fg="#fbbf24")
            self._log("Session paused ⏸")

    def reset_session(self):
        self.running = False
        self.session_seconds = 0
        self.timers = {k: 0 for k in REMINDERS}
        self.start_btn.config(text="▶  Start Session")
        self.status_label.config(text="● Idle", fg="#6b8f76")
        self.timer_label.config(text="00:00:00")
        for k in REMINDERS:
            self.next_labels[k].config(text=f"Next in {self.intervals[k]}m")
        self._log("Session reset ↺")

    def _run_tick(self):
        if not self.running:
            return
        self.session_seconds += 1
        h = self.session_seconds // 3600
        m = (self.session_seconds % 3600) // 60
        s = self.session_seconds % 60
        self.timer_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")

        # Check reminders every 60 seconds
        if self.session_seconds % 60 == 0:
            for key in REMINDERS:
                self.timers[key] += 1
                remaining = self.intervals[key] - self.timers[key]
                self.next_labels[key].config(text=f"Next in {max(0,remaining)}m")
                if self.timers[key] >= self.intervals[key]:
                    self.timers[key] = 0
                    threading.Thread(target=self._fire_reminder, args=(key,), daemon=True).start()

        self.root.after(1000, self._run_tick)

    def _fire_reminder(self, key):
        r = REMINDERS[key]
        title   = r['title']
        message = r['message']
        speech  = r['speech']

        if key == 'motivate':
            q, author = QUOTES[self.quote_idx % len(QUOTES)]
            self.quote_idx += 1
            message = f'"{q}"\n— {author}'
            speech  = f"Motivation time! {q}"
            self.root.after(0, lambda: self.quote_label.config(text=f'"{q}"'))

        # OS notification
        if PLYER_OK:
            try:
                plyer_notif.notify(title=f"{r['emoji']} {title}", message=message,
                                   app_name="Wellspring", timeout=8)
            except: pass

        # TTS
        speak(speech)

        # Popup (must run on main thread)
        self.root.after(0, lambda: self._show_popup(key, title, message))

        # Log
        self.root.after(0, lambda: self._log(f"{r['emoji']} {title}"))

    def _show_popup(self, key, title, message):
        color = REMINDERS[key]['color']
        popup = PopupWindow(
            reminder_type=key,
            title=title,
            message=message,
            color=color,
            on_dismiss=None,
            on_snooze=lambda: self._snooze(key)
        )
        # Run popup in separate thread so main window stays responsive
        threading.Thread(target=popup.show, daemon=True).start()

    def _snooze(self, key):
        self._log(f"⏱ {REMINDERS[key]['emoji']} snoozed 5 minutes")
        def snooze_fire():
            time.sleep(5 * 60)
            self._fire_reminder(key)
        threading.Thread(target=snooze_fire, daemon=True).start()

    def test_reminder(self):
        keys = list(REMINDERS.keys())
        key = keys[int(time.time()) % len(keys)]
        threading.Thread(target=self._fire_reminder, args=(key,), daemon=True).start()

    def _on_close(self):
        self.running = False
        self.root.destroy()

    def run(self):
        self.root.mainloop()


# ── ENTRY POINT ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🌿 Starting Wellspring Desktop...")
    print("   Install deps: pip install plyer pyttsx3")
    app = WellspringApp()
    app.run()