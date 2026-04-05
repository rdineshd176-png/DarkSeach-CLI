# DarkSearch CLI

Privacy-focused command-line research search tool that routes all search traffic through Tor.

> Crafted by **R.dinesh** :: Privacy by Design // Research in Stealth Mode

## Setup

1. Install dependency:

   ```bash
   pip install requests[socks]
   ```

2. Start Tor:

   Linux/Termux examples:

   ```bash
   tor
   ```

   or

   ```bash
   service tor start
   ```

3. Run DarkSearch CLI:

   ```bash
   python main.py
   ```

## Auto Setup Script (Linux/Termux)

You can run a single setup script to check Python, install pip tooling,
install `requests[socks]`, and install Tor when possible:

```bash
chmod +x setup.sh
./setup.sh
```

## Features

- Interactive prompt: `DarkSearch> `
- Commands: `exit`, `clear`, `help`
- Optional commands: `engine`, `engine duckduckgo`, `engine searxng`, `anon on`, `anon off`
- Search results include title, URL, and summary
- Results are limited to clean top entries (up to 10)
- No query storage, logs, or history

## Privacy Notes

- Uses Tor SOCKS5 proxy with `socks5h://127.0.0.1:9050` for DNS leak prevention
- Randomized User-Agent per request
- Random delay between requests
