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

# Start Ollama if not running
if ! pgrep -x ollama >/dev/null; then
    echo "🧠 Starting AI engine..."
    ollama serve &
    sleep 3
fi

# Check if model is available
if ! ollama list 2>/dev/null | grep -q "llama3.2"; then
    echo "📥 Downloading AI model (first time only, ~2GB)..."
    ollama pull llama3.2:3b
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

# Mark first boot as done
touch "$FIRST_BOOT_FLAG"
