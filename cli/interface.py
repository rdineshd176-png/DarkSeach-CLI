"""Interactive CLI loop for DarkSearch."""

from cli.commands import CommandProcessor
from core.config import AppConfig
from core.session import PrivacySession
from core.tor import is_tor_running
from utils.formatter import banner, print_error, print_help, print_info


def run_cli() -> None:
    config = AppConfig()
    session = PrivacySession(config)
    commands = CommandProcessor(config, session)

    print(banner())
    print_info("Anonymous research over Tor SOCKS5 proxy.")

    if not is_tor_running(config.tor_proxy, timeout=8):
        print_error("Tor is not running. Please start Tor.")
        return

    print_help()

    while True:
        try:
            raw = input("DarkSearch> ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting DarkSearch CLI.")
            break

        should_exit = commands.execute(raw)
        if should_exit:
            print("Exiting DarkSearch CLI.")
            break
