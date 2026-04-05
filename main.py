"""
DocSearch CLI - Privacy-focused research search tool.

Setup:
1) pip install requests[socks]
2) Start Tor (Linux/Termux examples):
   - tor
   - or service tor start
3) Run:
   python main.py
"""

import os

import requests

from search import SearchClient
from tor import is_tor_running
from utils import colorize


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_help() -> None:
    print("\nCommands:")
    print("  exit                 Quit DocSearch CLI")
    print("  clear                Clear terminal")
    print("  engine               Show current engine")
    print("  engine duckduckgo    Switch to DuckDuckGo HTML")
    print("  engine searxng       Switch to SearXNG")
    print("  anon on              Enable extra anti-tracking delay")
    print("  anon off             Disable extra anti-tracking delay")
    print("  help                 Show this help\n")


def print_results(results: list[dict[str, str]], colors: bool = True) -> None:
    if not results:
        print(colorize("No search results found.", "yellow", colors))
        return

    print()
    for idx, row in enumerate(results, start=1):
        title = colorize(row["title"], "green", colors)
        url = colorize(row["url"], "cyan", colors)
        print(f"[{idx}] {title}")
        print(f"URL: {url}")
        print(f"Summary: {row['summary']}\n")


def handle_command(raw: str, client: SearchClient) -> bool:
    """Handle non-search commands. Return True if command consumed."""
    cmd = raw.strip()

    if cmd == "":
        print("Please enter a query or type 'help'.")
        return True

    if cmd == "help":
        print_help()
        return True

    if cmd == "clear":
        clear_screen()
        return True

    if cmd == "engine":
        print(f"Current engine: {client.engine}")
        return True

    if cmd.startswith("engine "):
        _, _, name = cmd.partition(" ")
        if client.set_engine(name):
            print(f"Search engine set to: {client.engine}")
        else:
            print("Invalid engine. Use: duckduckgo or searxng")
        return True

    if cmd in {"anon on", "anon off"}:
        enabled = cmd.endswith("on")
        client.set_anon_mode(enabled)
        status = "enabled" if enabled else "disabled"
        print(f"Extra anonymous delay: {status}")
        return True

    return False


def run_cli() -> None:
    print(colorize("DocSearch CLI", "bold"))
    print("Privacy-focused research search via Tor SOCKS5 proxy.")

    if not is_tor_running():
        print(colorize("Tor is not running. Please start Tor.", "red"))
        return

    client = SearchClient(engine="duckduckgo", anon_mode=True)
    print("Type 'help' for commands. Type 'exit' to quit.\n")

    while True:
        try:
            raw = input("DocSearch> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting DocSearch CLI.")
            break

        if raw.lower() == "exit":
            print("Exiting DocSearch CLI.")
            break

        if handle_command(raw.lower(), client):
            continue

        try:
            results = client.search(raw, limit=7)
            print_results(results)
        except ValueError as exc:
            print(colorize(str(exc), "yellow"))
        except requests.Timeout:
            print(colorize("Request timed out. Please try again.", "red"))
        except requests.RequestException:
            print(colorize("Search request failed over Tor. Try again.", "red"))
        except Exception:
            print(colorize("Unexpected error occurred. Please try again.", "red"))


if __name__ == "__main__":
    run_cli()
