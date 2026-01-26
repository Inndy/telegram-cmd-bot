# Telegram Cmd Bot

A Telegram bot that allows authorized users to execute predefined shell commands.

## Features

- Execute shell commands from Telegram.
- Whitelist-based authentication using Telegram user IDs.
- Configurable commands via `commands.json`.
- Support for optional arguments (optional).

## Setup

1.  **Environment Variables**: Create a `.env` file based on `.env.example` and set your `TELEGRAM_BOT_TOKEN`.
2.  **Whitelist**: Add your Telegram user ID to `whitelist.txt`.
3.  **Commands**: Configure your commands in `commands.json`.

## Installation

You can install the bot as a package:

```bash
uv pip install .
```

Or for development (editable mode):

```bash
uv pip install -e .
```

## Usage

Once installed, you can start the bot using the following command:

```bash
telegram-cmd-bot
```

### Whitelist configuration

The `whitelist.txt` file should contain one Telegram user ID per line. Lines starting with `#` are ignored.

### Commands configuration

The `commands.json` defines the available commands:

```json
{
  "status": {
    "shell": "systemctl status my-service",
    "description": "Check service status",
    "allow_args": false
  },
  "log": {
    "shell": "journalctl -u my-service -n 20",
    "description": "Show last 20 log lines",
    "allow_args": false
  }
}
```
