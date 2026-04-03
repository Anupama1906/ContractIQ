#!/usr/bin/env bash
# ======================================================
# ContractIQ — AI environment installer
# Usage: bash install_ai.sh
# Works on: Windows (Git Bash / WSL), macOS, Linux
# ======================================================

set -e  # Exit on any error

VENV_DIR=".venv-ai"
PYTHON="python3"

# On Windows via Git Bash, python3 might just be python
if ! command -v python3 &>/dev/null; then
  PYTHON="python"
fi

echo ""
echo "============================================="
echo "  ContractIQ — AI Environment Setup"
echo "============================================="
echo ""

# ── 1. Create virtual environment ──────────────────
if [ ! -d "$VENV_DIR" ]; then
  echo "[1/5] Creating virtual environment: $VENV_DIR"
  $PYTHON -m venv $VENV_DIR
else
  echo "[1/5] Virtual environment already exists, skipping."
fi

# ── 2. Activate ────────────────────────────────────
echo "[2/5] Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
  source "$VENV_DIR/Scripts/activate"
else
  source "$VENV_DIR/bin/activate"
fi

# ── 3. Upgrade pip ─────────────────────────────────
echo "[3/5] Upgrading pip..."
pip install --upgrade pip --quiet

# ── 4. Install CPU torch FIRST (special index URL) ─
echo "[4/5] Installing PyTorch (CPU)..."
pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu --quiet
echo "      torch installed."

# ── 5. Install remaining AI dependencies ───────────
echo "[5/5] Installing AI requirements..."
pip install -r ai/requirements.txt --quiet

# ── Post-install: spaCy model ──────────────────────
echo ""
echo "Downloading spaCy model (en_core_web_sm)..."
python -m spacy download en_core_web_sm --quiet

echo ""
echo "============================================="
echo "  AI environment ready."
echo "  Activate with:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
  echo "    source .venv-ai/Scripts/activate"
else
  echo "    source .venv-ai/bin/activate"
fi
echo "============================================="