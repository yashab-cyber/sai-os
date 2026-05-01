# 🧠 SAI-OS — The AI Operating System

<p align="center">
  <strong>A Debian-based operating system where AI is the interface.</strong><br>
  Talk to your computer. It understands.
</p>

---

## 🌟 What is SAI-OS?

SAI-OS replaces traditional menus, terminals, and app launchers with a single AI interface.
Instead of remembering commands or clicking through menus, just say what you want:

```
sai "open my project files"
sai "clean my system"
sai "prepare my work setup"
sai "play some music"
```

**Normal OS:** User → App → Action
**SAI-OS:** User → AI → Action

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🗣️ **Natural Language Control** | Type or speak commands in plain English |
| ⚡ **AI Task Automation** | Complete multi-step tasks with one command |
| 📁 **Smart File Management** | Auto-organize, deduplicate, suggest cleanup |
| 🧠 **Personalized Memory** | Learns your habits and daily routines |
| 💻 **AI Shell** | Replace complex Linux commands with natural language |
| 🔧 **Self-Maintenance** | Auto-clean, update, and optimize your system |
| 🔔 **Intelligent Notifications** | Only useful alerts, never spam |
| 🤖 **Built-in AI Assistant** | ChatGPT-style assistant that knows your system |
| 🎙️ **Voice Control** | "Hey SAI, open YouTube" |
| 🧩 **Modular Design** | Add/remove AI modules and plugins |

## 🏗️ Architecture

```
User
 ↓
AI Interface (CLI / Voice / GUI)
 ↓
AI Brain (Ollama LLM + Function Calling)
 ↓
Task Engine (Tool Modules)
 ↓
Linux System (Debian Bookworm)
 ↓
Kernel
```

## 🚀 Quick Start

### Prerequisites
- Debian 12+ or Ubuntu 22.04+
- Python 3.11+
- 4GB+ RAM (8GB recommended for 7B model)

### Install

```bash
# Clone the repository
git clone https://github.com/yourusername/sai-os.git
cd sai-os

# Install dependencies
make install

# Start using SAI
sai "hello, what can you do?"
```

### Build ISO

```bash
# Build the full bootable ISO (requires root)
make iso
```

## 📖 Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [User Guide](docs/USER_GUIDE.md)

## 🛡️ Privacy & Security

- **100% Local AI** — All AI processing happens on your machine via Ollama
- **No Cloud Required** — Works fully offline after initial setup
- **Safety Confirmations** — Destructive commands always require explicit approval
- **Open Source** — Every line of code is auditable

## 📜 License

GPL-3.0-or-later — Free as in freedom.
