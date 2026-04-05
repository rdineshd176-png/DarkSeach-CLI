"""Terminal output formatting for DarkSearch CLI."""

from typing import Iterable


def _color(text: str, code: str, enabled: bool = True) -> str:
    if not enabled:
        return text
    return f"\033[{code}m{text}\033[0m"


def banner() -> str:
    return "\n".join(
        [
            _color("===============================================", "96"),
            _color("   DARKSEARCH CLI :: PRIVATE RESEARCH CONSOLE", "1"),
            _color("===============================================", "96"),
            _color("[ R.dinesh :: Privacy by Design ]", "93"),
        ]
    )


def print_help() -> None:
    print("\nAvailable Commands:")
    print("  search <query>                  Run a privacy-routed search")
    print("  analyze <query>                 Search and generate analysis report")
    print("  engine [duckduckgo|searxng]     Get/set standard search engine")
    print("  mode [normal|onion]             Switch normal/onion mode")
    print("  anon [on|off]                   Toggle extra anti-tracking delay")
    print("  clear                           Clear terminal")
    print("  help                            Show this help")
    print("  exit                            Quit DarkSearch CLI\n")


def print_results(results: Iterable[dict[str, object]]) -> None:
    rows = list(results)
    if not rows:
        print(_color("No search results found.", "93"))
        return

    print()
    for idx, row in enumerate(rows, start=1):
        print(_color(f"[{idx}] {row.get('title', 'Untitled')}", "92"))
        print(_color(f"URL: {row.get('url', '')}", "96"))
        print(f"Summary: {row.get('summary', 'No summary available.')}")
        print(f"Privacy Score: {row.get('privacy_score', 'N/A')}/10")
        print("---")


def print_analysis(report: dict[str, object]) -> None:
    print("\n[ ANALYSIS REPORT ]\n")
    print(f"* Key Topic: {report.get('key_topic', 'N/A')}")
    print(f"* Important Keywords: {', '.join(report.get('keywords', [])) or 'N/A'}")
    print(f"* Summary: {report.get('summary', 'N/A')}")

    insights = report.get("insights", [])
    if isinstance(insights, list):
        print(f"* Insights: {' | '.join(str(item) for item in insights)}")
    else:
        print(f"* Insights: {insights}")
    print()


def print_error(message: str) -> None:
    print(_color(message, "91"))


def print_info(message: str) -> None:
    print(_color(message, "96"))
