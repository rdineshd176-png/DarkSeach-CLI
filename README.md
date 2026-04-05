# DarkSearch CLI

Cybersecurity-grade, privacy-first research CLI with Tor-only routing and modular architecture.

Crafted by **R.dinesh** :: Privacy by Design // Research in Stealth Mode

## Setup (Linux / Termux)

1. Install dependency:

   ```bash
   pip install requests[socks]
   ```

2. Start Tor:

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

## Auto Setup Script

Run the installer to auto-check Python, install dependencies, install/start Tor when possible, and launch DarkSearch CLI:

```bash
chmod +x setup.sh
./setup.sh
```

## Command Reference

- `search <query>`
- `analyze <query>`
- `engine [duckduckgo|searxng]`
- `mode [normal|onion]`
- `anon [on|off]`
- `clear`
- `help`
- `exit`

## Architecture

```text
.
+-- main.py
+-- cli/
|   +-- interface.py
|   +-- commands.py
+-- core/
|   +-- tor.py
|   +-- session.py
|   +-- config.py
+-- engines/
|   +-- duckduckgo.py
|   +-- searxng.py
|   +-- onion.py
+-- processing/
|   +-- parser.py
|   +-- ranker.py
|   +-- analyzer.py
+-- privacy/
|   +-- fingerprint.py
|   +-- scorer.py
+-- utils/
|   +-- formatter.py
|   +-- helpers.py
+-- data/
   +-- user_agents.txt
```

## Security and Privacy Design

- All traffic routes through Tor SOCKS5: `socks5h://127.0.0.1:9050`
- Tor availability is validated before operations
- Randomized User-Agent and headers per session
- Random delays and session rotation to reduce fingerprint stability
- Onion mode restricts output to `.onion` sources
- Built-in privacy score (`1/10` to `10/10`) per result
- No external AI APIs

## Output Format

Search result format:

```text
[1] Title
URL: ...
Summary: ...
Privacy Score: 8/10
---
```

Analysis format:

```text
[ ANALYSIS REPORT ]

* Key Topic:
* Important Keywords:
* Summary:
* Insights:
```
