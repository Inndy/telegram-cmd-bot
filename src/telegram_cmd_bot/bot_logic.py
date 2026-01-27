
import os
import subprocess
import asyncio
from contextlib import asynccontextmanager

WHITELIST_FILE = "whitelist.txt"
_whitelist_cache = set()
_last_mtime = 0

# Singleton command tracking
_running_singletons: set[str] = set()
_singleton_lock = asyncio.Lock()

class CommandAlreadyRunningError(Exception):
    """Raised when attempting to execute a singleton command that's already running."""
    def __init__(self, command_name: str):
        self.command_name = command_name
        super().__init__(f"Command '{command_name}' is already running")

def get_whitelist_path():
    if os.path.exists(WHITELIST_FILE):
        return WHITELIST_FILE

    # Fallback to project root if running from within the package
    root_path = os.path.join(os.path.dirname(__file__), '..', '..', WHITELIST_FILE)
    return root_path

def get_whitelist():
    global _last_mtime

    whitelist_path = get_whitelist_path()

    if not os.path.exists(whitelist_path):
        try:
            with open(whitelist_path, "w") as f:
                print("# Put you Telegram user id here", file=f)
                print("# You can use @username_to_id_bot to query your id", file=f)
        except Exception as e:
            print(f"Error creating whitelist: {e}")
        return set()

    try:
        current_mtime = os.path.getmtime(whitelist_path)
        if current_mtime > _last_mtime:
            with open(whitelist_path, "r") as f:
                _whitelist_cache.clear()
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        try:
                            _whitelist_cache.add(int(line))
                        except ValueError:
                            pass
            _last_mtime = current_mtime
    except Exception as e:
        print(f"Error reading whitelist: {e}")

    return _whitelist_cache

def check_whitelist(user_id):
    return user_id in get_whitelist()

@asynccontextmanager
async def singleton_guard(command_name: str, is_singleton: bool):
    """
    Context manager for singleton command execution tracking.

    Args:
        command_name: Name of the command being executed
        is_singleton: Whether the command has singleton enforcement

    Raises:
        CommandAlreadyRunningError: If singleton command is already running

    Ensures cleanup even if command fails or handler crashes.
    """
    if not is_singleton:
        # Non-singleton commands pass through with zero overhead
        yield
        return

    # Check and mark as running
    async with _singleton_lock:
        if command_name in _running_singletons:
            raise CommandAlreadyRunningError(command_name)
        _running_singletons.add(command_name)

    try:
        yield
    finally:
        # Always cleanup, even on exception
        async with _singleton_lock:
            _running_singletons.discard(command_name)

async def execute_command(cmd, args=None):
    if args is None:
        args = []

    try:
        is_shell = isinstance(cmd, str)

        # Safety Check: Do NOT allow args if cmd is a raw shell string
        if is_shell and args:
            return "Error: Arguments are not allowed for shell string commands to prevent injection."

        final_cmd = cmd
        if not is_shell and args:
             # cmd is a list, safely append args
            if isinstance(args, str):
                final_cmd = cmd + [args]
            else:
                final_cmd = cmd + args

        process = subprocess.Popen(
            final_cmd,
            shell=is_shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()

        output = ""
        if stdout:
            output += f"Output:\n{stdout}\n"
        if stderr:
            output += f"Error:\n{stderr}\n"

        if not output:
            output = "Command executed with no output."

        return output
    except Exception as e:
        return f"Execution failed: {e}"
