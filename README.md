# Vedabase - Original

> ⚠️ **Legacy.** This repository is no longer maintained. The current app is served at **https://app.vedabase.cc**.

A desktop and web application for reading and studying the complete works of A. C. Bhaktivedanta Swami Prabhupada — original, unedited editions as originally published.

**[Use Online](https://vedabase-app.pages.dev/app)** · **[Download Desktop App](https://github.com/juanmanuelferrera/vedabase-app/releases/latest)** · **[Landing Page](https://vedabase-app.pages.dev/)**

## Content

- **Bhagavad-gita As It Is** — 1972 original edition
- **Srimad Bhagavatam** — all 12 cantos
- **Caitanya Caritamrta** — Adi, Madhya, Antya lilas
- **Krsna Book**
- **21 other books** — Nectar of Devotion, Sri Isopanisad, Teachings of Lord Caitanya, and more
- **Lectures** — hundreds of lectures from 1966–1976
- **Conversations** — 1,009 morning walks, room conversations, and interviews (1967–1977)
- **Letters** — 6,605 letters to disciples and others (1947–1977)

## Features

- **Full-text search** with instant highlighting across all books
- **Boolean search** — use `+` for AND, `OR` for either term
- **Diacritics-insensitive search** — search "Krsna" to find "Kṛṣṇa"
- **Regex search** for advanced pattern matching
- **Search All** — search across every book at once
- **Cross-references** — click verse references to jump instantly
- **Bookmarks** — save and manage your reading positions
- **Reading statistics** — track your study progress
- **Interactive TOC** — collapsible Table of Contents navigation
- **Dark mode** — warm dark theme for comfortable reading
- **Font control** — adjustable text size
- **Fully offline** — standalone desktop app with all content embedded

## Download

### Desktop App (v1.5.0)

| Platform | Download |
|----------|----------|
| macOS (Apple Silicon) | [Vedabase_1.5.0_aarch64.dmg](https://github.com/juanmanuelferrera/vedabase-app/releases/latest) |
| macOS (Intel) | [Vedabase_1.5.0_x64.dmg](https://github.com/juanmanuelferrera/vedabase-app/releases/latest) |
| Windows | [Vedabase_1.5.0_x64-setup.exe](https://github.com/juanmanuelferrera/vedabase-app/releases/latest) |
| Linux | [Vedabase_1.5.0_amd64.deb](https://github.com/juanmanuelferrera/vedabase-app/releases/latest) |

### Online Version

No installation needed — use the app directly in your browser at **[vedabase-app.pages.dev/app](https://vedabase-app.pages.dev/app)**.

## Installation

### macOS

1. Download the `.dmg` for your Mac (Apple Silicon or Intel)
2. Open the DMG and drag `Vedabase` to Applications
3. **First launch**: Right-click the app and select "Open" (required for unsigned apps)
4. Click "Open" in the security dialog

> **Gatekeeper note:** Since this app is not signed with an Apple Developer certificate, macOS will block it on first launch. Right-click → Open bypasses this. You only need to do this once.

**Alternative:** Open Terminal and run:
```
xattr -cr /Applications/Vedabase.app
```

### Windows

1. Download `Vedabase_1.5.0_x64-setup.exe`
2. Run the installer
3. If Windows Defender SmartScreen appears, click "More info" → "Run anyway"

### Linux

1. Download `Vedabase_1.5.0_amd64.deb`
2. Install: `sudo dpkg -i Vedabase_1.5.0_amd64.deb`

## Tech Stack

Built with [Tauri](https://tauri.app/) (Rust + WebView) for lightweight, native performance.

## Credits

Original text: [Vaishnava Uploads](https://vaishnavauploads.pages.dev/bg)

Author: A. C. Bhaktivedanta Swami Prabhupada

Sponsored by: [Vedic Vault](https://www.vedicvault.org/projects)
