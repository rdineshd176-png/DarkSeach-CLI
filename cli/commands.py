"""Command handlers for DarkSearch CLI."""

import requests

from core.config import AppConfig
from core.session import PrivacySession
from core.tor import is_tor_running
from engines.duckduckgo import DuckDuckGoEngine
from engines.onion import OnionEngine
from engines.searxng import SearXNGEngine
from processing.analyzer import analyze_results
from processing.ranker import rank_results
from privacy.scorer import attach_privacy_scores
from utils.formatter import print_analysis, print_error, print_help, print_info, print_results
from utils.helpers import clear_terminal


class CommandProcessor:
    """Parses commands and executes DarkSearch workflows."""

    def __init__(self, config: AppConfig, session: PrivacySession):
        self.config = config
        self.session = session
        self.engines = {
            "duckduckgo": DuckDuckGoEngine(session),
            "searxng": SearXNGEngine(session),
        }
        self.onion_engine = OnionEngine(session)

    def execute(self, raw: str) -> bool:
        """Execute a command line. Returns True when CLI should exit."""
        line = raw.strip()
        if not line:
            print_error("Invalid command. Type 'help' for usage.")
            return False

        parts = line.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if cmd == "help":
            print_help()
            return False

        if cmd == "clear":
            clear_terminal()
            return False

        if cmd == "exit":
            return True

        if cmd == "engine":
            return self._handle_engine(arg)

        if cmd == "mode":
            return self._handle_mode(arg)

        if cmd == "anon":
            return self._handle_anon(arg)

        if cmd == "search":
            return self._handle_search(arg)

        if cmd == "analyze":
            return self._handle_analyze(arg)

        print_error("Invalid command. Type 'help' for usage.")
        return False

    def _handle_engine(self, arg: str) -> bool:
        if not arg:
            print_info(f"Current engine: {self.config.engine}")
            return False
        if self.config.mode == "onion":
            print_error("Engine switching is disabled in onion mode.")
            return False
        if self.config.set_engine(arg):
            print_info(f"Engine set to: {self.config.engine}")
        else:
            print_error("Invalid engine. Use duckduckgo or searxng.")
        return False

    def _handle_mode(self, arg: str) -> bool:
        if not arg:
            print_info(f"Current mode: {self.config.mode}")
            return False
        if self.config.set_mode(arg):
            print_info(f"Mode set to: {self.config.mode}")
        else:
            print_error("Invalid mode. Use normal or onion.")
        return False

    def _handle_anon(self, arg: str) -> bool:
        if not arg:
            state = "on" if self.config.anon else "off"
            print_info(f"Anon mode is: {state}")
            return False
        if self.config.set_anon(arg):
            state = "on" if self.config.anon else "off"
            print_info(f"Anon mode set to: {state}")
            self.session.rotate_session(force=True)
        else:
            print_error("Invalid anon value. Use on or off.")
        return False

    def _run_query(self, query: str) -> list[dict[str, object]]:
        if not query:
            raise ValueError("Please provide a search query.")

        if not is_tor_running(self.config.tor_proxy, timeout=8):
            raise RuntimeError("Tor is not running. Please start Tor.")

        if self.config.mode == "onion":
            raw_results = self.onion_engine.search(query, self.config.result_limit)
        else:
            engine = self.engines[self.config.engine]
            raw_results = engine.search(query, self.config.result_limit)

        ranked = rank_results(raw_results, query)
        scored = attach_privacy_scores(ranked)
        return scored

    def _handle_search(self, arg: str) -> bool:
        try:
            results = self._run_query(arg)
            print_results(results)
        except ValueError as exc:
            print_error(str(exc))
        except RuntimeError as exc:
            print_error(str(exc))
        except requests.Timeout:
            print_error("Request timed out. Please try again.")
        except requests.RequestException:
            print_error("Search engine request failed over Tor.")
        except Exception:
            print_error("Engine failure occurred while processing search.")
        return False

    def _handle_analyze(self, arg: str) -> bool:
        try:
            results = self._run_query(arg)
            if not results:
                print_error("No results available for analysis.")
                return False
            print_results(results[:5])
            report = analyze_results(arg, results)
            print_analysis(report)
        except ValueError as exc:
            print_error(str(exc))
        except RuntimeError as exc:
            print_error(str(exc))
        except requests.Timeout:
            print_error("Request timed out. Please try again.")
        except requests.RequestException:
            print_error("Search engine request failed over Tor.")
        except Exception:
            print_error("Engine failure occurred while processing analysis.")
        return False
