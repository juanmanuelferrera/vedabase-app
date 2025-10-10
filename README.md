# Vedabase - Original

A desktop application for reading and studying the works by A. C. Bhaktivedanta Swami Prabhupada.

## Features

- 🔍 **Full-text search** - Search through all text with instant highlighting
- 🎯 **Smart highlighting** - Visual emphasis on all search matches
- ⏭️ **Navigate matches** - Jump between results with Previous/Next buttons
- 🔎 **Advanced search** - Regex patterns and search-within-results filtering
- 📑 **Cross-references** - Click verse references to jump instantly
- 📝 **Personal notes** - Add, edit, and manage annotations on any verse
- 🌓 **Dark mode** - True dark theme with white text on black background
- 📖 **Interactive TOC** - One-click collapsible Table of Contents navigation
- 🎨 **Font control** - Adjustable text size for comfortable reading
- 💾 **Fully offline** - Standalone app with all content embedded, no internet needed

## Installation

### macOS

1. Download `Vedabase.app` from the releases
2. Copy to `/Applications` or anywhere you prefer
3. **First launch**: Right-click the app and select "Open" (see Gatekeeper note below)
4. Click "Open" in the security dialog

#### macOS Gatekeeper Notice

Since this app is not signed with an Apple Developer certificate, macOS Gatekeeper will block it on first launch. This is normal for unsigned apps.

**To open the app:**
1. Right-click (or Control-click) on `Vedabase.app`
2. Select "Open" from the menu
3. Click "Open" in the dialog that appears

**Alternative method:**
1. Try to open the app normally (it will be blocked)
2. Go to System Preferences → Security & Privacy
3. Click "Open Anyway" for Vedabase

You only need to do this once. After the first launch, you can open it normally.

### Building from Source

**Prerequisites:**
- Node.js
- Rust and Cargo
- Tauri CLI

**Build commands:**
```bash
# Install dependencies
npm install

# Development mode
npm run tauri:dev

# Production build
npm run tauri:build
```

The built app will be in `src-tauri/target/release/bundle/`

## Credits

Original text: [Vaishnava Uploads](https://vaishnavauploads.pages.dev/bg)

Author: A. C. Bhaktivedanta Swami Prabhupada
