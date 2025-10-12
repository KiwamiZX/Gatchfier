<p align="center"><img width="400" height="400" alt="vertical logo" src="https://github.com/user-attachments/assets/cd5289e7-17ab-49d6-848f-da71d8a3c2cd" /></p>

# Gatchfier Network Toolkit

Gatchfier is a PySide6 desktop application that bundles together day-to-day network diagnostics in a single, themeable UI. The refreshed interface offers both neon and light modes while keeping each tool focused and easy to use.

## Features

- **Ping** – run single or continuous ICMP echo tests, track latency statistics, and view live logs.
- **Traceroute** – trace IPv4/IPv6 network paths with controllable hop limits and responsive cancellation.
- **Port Scan** – perform full TCP port sweeps with live progress updates and summarised results.
- **DNS Lookup** – resolve IPv4 or IPv6 records using the system resolver.
- **Whois** – query domain registration details and display key ownership fields.
- **Theme Toggle** – switch between neon and light themes and persist the preference across sessions.
- **Safe Config Storage** – user preferences live in `%USERPROFILE%\.gatchfier\config.json` to keep the app portable.

## Requirements

- Windows 10 or later
- Python 3.10+ (for development)
- Recommended: PowerShell 7+ for running helper scripts

## Screenshots
<img width="1919" height="1021" alt="image" src="https://github.com/user-attachments/assets/e2853aa3-e243-4e9f-a50f-8ce9d673282c" />
<img width="1919" height="1022" alt="image" src="https://github.com/user-attachments/assets/8c16df3e-082a-4cf3-87c6-d1903856f6e0" />


## Getting Started (Development)

1. Create and activate a virtual environment.
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Launch the application from source:
   ```powershell
   python app.py
   ```

Configuration files are written to `%USERPROFILE%\.gatchfier`. Delete the folder if you need to reset stored preferences.

## Project Layout

- `app.py` – application entry point, window chrome, theming, and tab registration.
- `tabs/` – individual tool implementations (ping, traceroute, port scan, DNS, whois).

## License

This project is released under the [MIT License](LICENSE).

