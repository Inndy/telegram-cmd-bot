
import os
import logging
import json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.helpers import escape_markdown
from .bot_logic import check_whitelist, execute_command

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

COMMANDS_CONFIG = {}

def load_config():
    global COMMANDS_CONFIG
    # Try to find commands.json in the current working directory first,
    # then in the same directory as the script if possible.
    config_path = 'commands.json'
    if not os.path.exists(config_path):
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'commands.json')

    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            COMMANDS_CONFIG = json.load(f)
    else:
        logging.error(f"commands.json not found at {config_path}")
        COMMANDS_CONFIG = {}

# Helper to look up shell command
def get_command_config(cmd_name):
    return COMMANDS_CONFIG.get(cmd_name, {})

def get_shell_command(cmd_name):
    return get_command_config(cmd_name).get("shell")

async def check_and_handle_auth(update: Update) -> bool:
    user_id = update.effective_user.id
    if check_whitelist(user_id):
        return True

    logging.warning(f"Unauthorized access attempt from user ID: {user_id}")
    try:
        if update.message:
            await update.message.delete()
    except Exception as e:
        logging.error(f"Failed to delete unauthorized message: {e}")

    try:
        if update.message:
            await update.message.reply_text("🚫 Access Denied: You are not authorized to use this bot.")
    except Exception as e:
        logging.error(f"Failed to send deny message: {e}")

    return False

async def generic_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_and_handle_auth(update):
        return

    parts = update.message.text.lstrip('/').split(maxsplit=1)
    command_name = parts[0]
    args = parts[1].strip() if len(parts) > 1 else ""

    cmd_config = get_command_config(command_name)
    shell_cmd = cmd_config.get("shell")

    if shell_cmd:
        if args and not cmd_config.get("allow_args", False):
            await update.message.reply_text("⚠️ This command does not accept arguments.")
            args = [] # Reset args to ignore them

        escaped_text = escape_markdown(f"Executing: {shell_cmd} with args: {args}...", version=2, entity_type='PRE')
        await update.message.reply_text(f"```\n{escaped_text}\n```", parse_mode='MarkdownV2')

        results = await execute_command(shell_cmd, args)
        escaped_results = escape_markdown(results, version=2, entity_type='PRE')
        await update.message.reply_text(f"```\n{escaped_results}\n```", parse_mode='MarkdownV2')
    else:
        await update.message.reply_text(f"Unknown command: {command_name}")

async def list_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_and_handle_auth(update):
        return

    help_text = "Available commands:\n"
    for cmd, data in COMMANDS_CONFIG.items():
        help_text += f"/{cmd} - {data['description']}\n"
    await update.message.reply_text(help_text)

async def catch_all_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This handler catches everything else
    if not await check_and_handle_auth(update):
        return

    await update.message.reply_text("Unknown command or message. Use /help to see available commands.")

async def post_init(application):
    command_list = []
    for cmd, data in COMMANDS_CONFIG.items():
        command_list.append((cmd, data["description"]))
    try:
        await application.bot.set_my_commands(command_list)
        logging.info("Commands registered with Telegram")
    except Exception as e:
        logging.error(f"Failed to register commands: {e}")

def main():
    load_dotenv()
    load_config()
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set.")
        exit(1)

    application = ApplicationBuilder().token(token).post_init(post_init).build()

    # Register a handler for listing commands
    application.add_handler(CommandHandler("help", list_commands))

    # Dynamically register handlers for predefined commands
    for cmd in COMMANDS_CONFIG:
        application.add_handler(CommandHandler(cmd, generic_command_handler))

    # Register catch-all handler LAST
    application.add_handler(MessageHandler(filters.ALL, catch_all_handler))

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
