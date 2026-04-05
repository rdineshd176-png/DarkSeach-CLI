"""Global runtime configuration for DarkSearch CLI."""

from dataclasses import dataclass


@dataclass
class AppConfig:
    """Shared mutable state for CLI runtime options."""

    engine: str = "duckduckgo"
    mode: str = "normal"  # normal|onion
    anon: bool = True
    result_limit: int = 7
    timeout: int = 20
    tor_proxy: str = "socks5h://127.0.0.1:9050"

    def set_engine(self, value: str) -> bool:
        value = value.strip().lower()
        if value in {"duckduckgo", "searxng"}:
            self.engine = value
            return True
        return False

    def set_mode(self, value: str) -> bool:
        value = value.strip().lower()
        if value in {"normal", "onion"}:
            self.mode = value
            return True
        return False

    def set_anon(self, value: str) -> bool:
        value = value.strip().lower()
        if value == "on":
            self.anon = True
            return True
        if value == "off":
            self.anon = False
            return True
        return False
