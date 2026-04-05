"""Small helper functions used across CLI modules."""

import os
from urllib.parse import urlparse


def clear_terminal() -> None:
    os.system("clear")


def extract_domain(url: str) -> str:
    return (urlparse(url).hostname or "").lower()
