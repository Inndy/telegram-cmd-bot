#!/bin/bash
set -e

# Configuration
SERVICE_NAME="telegram-cmd-bot"
VENV_DIR=".venv"
MAIN_SCRIPT="main.py"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting setup for $SERVICE_NAME...${NC}"

# 1. Setup Configuration Files
if [ ! -f "commands.json" ]; then
    if [ -f "commands.json.example" ]; then
        echo -e "${GREEN}Copying commands.json.example to commands.json...${NC}"
        cp commands.json.example commands.json
    else
        echo -e "${RED}Warning: commands.json.example not found!${NC}"
    fi
else
    echo "commands.json already exists, skipping..."
fi

# 2. Setup Virtual Environment
if command -v uv &> /dev/null; then
    echo -e "${GREEN}uv detected.${NC}"
    if [ -f "uv.lock" ]; then
        echo "Syncing dependencies with uv..."
        uv sync
    else
        echo "Creating venv with uv..."
        uv venv $VENV_DIR
        # Assuming we need to install from pyproject.toml if uv.lock doesn't exist but uv does
        if [ -f "pyproject.toml" ]; then
             echo "Installing dependencies from pyproject.toml..."
             # Use pip inside uv venv if silent sync isn't an option without lockfile,
             # but uv pip install is better.
             # However, simpler fallback:
             source $VENV_DIR/bin/activate
             uv pip install .
        fi
    fi
else
    echo "uv not found. Fallback to python3 -m venv..."
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv $VENV_DIR
    fi
    source $VENV_DIR/bin/activate

    echo "Installing dependencies..."
    pip install .
fi

# Ensure we have absolute paths
PWD=$(pwd)
PYTHON_EXEC="$PWD/$VENV_DIR/bin/python3"
SCRIPT_PATH="$PWD/$MAIN_SCRIPT"
USER_NAME=$(whoami)
GROUP_NAME=$(id -gn)

# 3. Generate Systemd Service
SERVICE_FILE="$SERVICE_NAME.service"

echo -e "${GREEN}Generating systemd service file: $SERVICE_FILE${NC}"

cat <<EOF > $SERVICE_FILE
[Unit]
Description=Telegram Command Bot Service
After=network.target

[Service]
Type=simple
User=$USER_NAME
Group=$GROUP_NAME
WorkingDirectory=$PWD
ExecStart=$PYTHON_EXEC $SCRIPT_PATH
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 4. Instructions
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "To install the systemd service, run the following commands:"
echo -e "${GREEN}sudo cp $SERVICE_FILE /etc/systemd/system/$SERVICE_FILE${NC}"
echo -e "${GREEN}sudo systemctl daemon-reload${NC}"
echo -e "${GREEN}sudo systemctl enable $SERVICE_FILE${NC}"
echo -e "${GREEN}sudo systemctl start $SERVICE_FILE${NC}"
echo -e "${GREEN}sudo systemctl status $SERVICE_FILE${NC}"
