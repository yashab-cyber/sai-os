#!/bin/bash
# SAI-OS First Boot Configuration
# Runs on the first boot to finalize system setup

set -e

FIRST_BOOT_FLAG="$HOME/.config/sai/.first-boot-done"

if [ -f "$FIRST_BOOT_FLAG" ]; then
    exit 0
fi

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║                                               ║"
echo "║     ⚡ Welcome to SAI-OS!                     ║"
echo "║     Your AI Operating System                  ║"
echo "║                                               ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Ensure config directories exist
mkdir -p ~/.config/sai
mkdir -p ~/.local/share/sai
mkdir -p ~/.cache/sai

# Copy default config if not present
if [ ! -f ~/.config/sai/config.toml ]; then
    cp /etc/skel/.config/sai/config.toml ~/.config/sai/config.toml 2>/dev/null || true
fi

# ── AI Backend Setup ──
# Check if backend is already configured
SAI_BACKEND=$(grep -oP 'backend\s*=\s*"\K[^"]+' ~/.config/sai/config.toml 2>/dev/null || echo "")

if [ -z "$SAI_BACKEND" ]; then
    echo "🧠 Let's set up your AI engine..."
    echo ""

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SETUP_SCRIPT="${SCRIPT_DIR}/setup-backend.sh"

    # Try multiple locations for the setup script
    if [ -f "$SETUP_SCRIPT" ]; then
        bash "$SETUP_SCRIPT"
    elif [ -f "/opt/sai-os/scripts/setup-backend.sh" ]; then
        bash /opt/sai-os/scripts/setup-backend.sh
    elif command -v sai-setup-backend &>/dev/null; then
        sai-setup-backend
    else
        echo "⚠️  Backend setup script not found."
        echo "   Configure later: edit ~/.config/sai/config.toml"
    fi
else
    echo "✅ AI backend already configured: $SAI_BACKEND"
fi

echo ""
echo "✅ SAI-OS is ready!"
echo ""
echo "💡 Quick start:"
echo "   • Type 'sai' to open the AI Shell"
echo "   • Type 'sai \"help\"' for examples"
echo "   • Press Super+A for the AI Assistant"
echo "   • Press Super+Enter for the SAI Terminal"
echo ""
echo "🔧 Change AI backend anytime:"
echo "   • Run: sai-setup-backend"
echo "   • Or in SAI Shell: backend ollama / backend api / backend copilot"
echo ""

# Mark first boot as done
touch "$FIRST_BOOT_FLAG"
