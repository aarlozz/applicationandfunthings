# 🌿 Wellspring — Your Daily Wellness Companion

A productivity wellness app that reminds you to drink water, take bathroom breaks, stand up and stretch, and sends you hourly motivation — so you never forget to take care of yourself while working.

Available as a **website** and a **desktop app**.

---

## ✨ Features

- 💧 **Drink water reminders** — customizable interval (every 5–60 min)
- 🚽 **Bathroom break reminders** — so you never hold it in too long
- 🧘 **Stand & stretch reminders** — fight the sitting disease
- 🔥 **Hourly motivation boosts** — a fresh quote every hour to keep you going
- 🔔 **Browser notifications** — alerts even when the tab is in the background
- 🔊 **Text-to-speech** — reminders spoken out loud
- 🎵 **Chime sounds** — unique sound for each reminder type
- ⏱️ **Snooze button** — delay any reminder by 5 minutes
- 📋 **Activity log** — see a history of all your reminders
- 🎛️ **Adjustable intervals** — set each reminder on its own schedule

---

## 🌐 Website

The website version runs entirely in your browser — no installation needed.

**Live site:** [https://wellspring-app.vercel.app](https://wellspring-app.vercel.app)

### Run locally

Just open the file directly in your browser:

```bash
# Option 1 — double click index.html in your file explorer

# Option 2 — open from terminal
open index.html          # Mac
start index.html         # Windows
xdg-open index.html      # Linux
```

> **Note:** Browser notifications require HTTPS to work. They will function on the deployed Vercel link but not when opening the file locally.

---

## 💻 Desktop App

The desktop app runs as a standalone window on your computer. It fires real OS-level system notifications and works even when your browser is closed.

### Download

👉 Go to [Releases](../../releases) and download the latest version for your OS:

| Platform | File |
|----------|------|
| Windows  | `wellspring_desktop.exe` |
| Mac      | `wellspring_desktop.app` |

Just double-click to run — no Python or any other software needed.

### Run from source

If you prefer to run the Python script directly:

**1. Install Python 3**

Download from [python.org](https://python.org/downloads). During install, check **"Add Python to PATH"**.

**2. Install dependencies**

```bash
pip install plyer pyttsx3
```

**3. Run the app**

```bash
python wellspring_desktop.py
```

---

## 🗂️ Project Structure

```
wellspring/
├── index.html                 # Website (deployed to Vercel)
├── wellspring_desktop.py      # Desktop app source code
├── README.md                  # You are here
└── .gitignore                 # Ignores PyInstaller build files
```

---

## 🛠️ Build Desktop App from Source

To package the Python script into a standalone executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Build for your current OS
pyinstaller --onefile --windowed wellspring_desktop.py
```

The output will be in the `dist/` folder:
- `dist/wellspring_desktop.exe` on Windows
- `dist/wellspring_desktop` on Mac/Linux

---

## 🚀 Deployment

| Part | Platform | Status |
|------|----------|--------|
| Website | Vercel | ✅ Live |
| Desktop app | GitHub Releases | ✅ Available |

The website is auto-deployed from this repo via Vercel — every push to `main` updates the live site automatically.

---

## 🧰 Tech Stack

| Component | Technology |
|-----------|------------|
| Website | HTML, CSS, JavaScript (vanilla) |
| Audio | Web Audio API + SpeechSynthesis API |
| Notifications | Web Notifications API |
| Desktop UI | Python + Tkinter |
| Desktop TTS | pyttsx3 |
| Desktop notifications | plyer |
| Packaging | PyInstaller |

---

## 📋 Roadmap

- [ ] Dark / light mode toggle on website
- [ ] Custom reminder messages
- [ ] Sound theme selection
- [ ] Mobile app version
- [ ] Reminder history statistics

---

## 🤝 Contributing

Pull requests are welcome! Feel free to open an issue first to discuss what you'd like to change.

---

## 📄 License

MIT — free to use, modify, and share.

---

*Built with ❤️ to help you stay healthy while you work hard.*