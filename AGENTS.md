<!-- Beware that CLAUDE.md and GEMINI.md is symlink to AGENTS.md. Update to agent doc should goes to AGENTS.md -->

# Gemini Context: Telegram Command Bot

This `GEMINI.md` provides context and instructions for working with the Telegram Command Bot project.

## Project Overview

**Name:** Telegram Cmd Bot
**Purpose:** A Telegram bot designed to execute predefined shell commands on the host server, authorized via a user whitelist.
**Core Stack:** Python 3.10+, `python-telegram-bot`, `python-dotenv`.

## Key Components

### Files & Directories
- **`src/telegram_cmd_bot/`**: Contains the source code.
    - `main.py`: Entry point. Handles Telegram updates, command dispatching, and authorization checks.
    - `bot_logic.py`: Contains core logic, likely including the whitelist check (`check_whitelist`) and command execution (`execute_command`).
- **`commands.json`**: JSON configuration file defining available commands, their shell equivalents, and permissions (e.g., `allow_args`).
- **`.env`**: Stores sensitive configuration like `TELEGRAM_BOT_TOKEN`.
- **`whitelist.txt`**: (Expected) A text file containing authorized Telegram User IDs.
- **`setup.sh`**: Bash script for automated setup, virtual environment creation (`uv` or `venv`), and systemd service generation.
- **`pyproject.toml`**: Project metadata and build configuration.

### Configuration

1.  **Environment**: Requires a `.env` file with `TELEGRAM_BOT_TOKEN`.
2.  **Commands**: defined in `commands.json`. Format:
    ```json
    {
      "command_name": {
        "shell": "echo 'command to run'",
        "description": "Help text",
        "allow_args": false
      }
    }
    ```
3.  **Auth**: Whitelist authorized users by adding their Telegram numeric ID to `whitelist.txt`.

## Development & Usage

### Setup
The project includes a `setup.sh` script to automate initialization:
```bash
./setup.sh
```
This script handles:
- Virtual environment creation (prefers `uv` if available).
- Dependency installation.
- Systemd service file generation.

### Manual Running
```bash
# Activate venv
source .venv/bin/activate

# Run the bot
python src/telegram_cmd_bot/main.py
```

### Build & Install
Dependencies are managed via `pyproject.toml`.
```bash
pip install -e .
```

## Known Issues / Observations
- **Entry Point Mismatch**: `pyproject.toml` defines the script entry point as `telegram_cmd_bot.main:main`, but the source directory is named `src/telegram_cmd_bot/`. This will cause the `telegram-cmd-bot` console script to fail unless the directory is renamed or `pyproject.toml` is updated.

## Task Context
When working on this project:
- **Safety**: Be cautious when modifying command execution logic (`subprocess` calls). Ensure inputs are validated or strictly limited to the `commands.json` definitions.
- **Conventions**: Follow existing pattern of async handlers in `main.py`.
- **Logs**: The bot uses standard `logging`. Check output for auth failures or execution errors.
