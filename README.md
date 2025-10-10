# Vedabase - Original

A desktop application for reading the Bhagavad-gita As It Is (1972 edition) by A. C. Bhaktivedanta Swami Prabhupada.

## Features

- 🔍 **Full-text search** - Search through all chapters and verses
- 🎯 **Highlight results** - Visual highlighting of search matches
- ⏭️ **Navigate matches** - Previous/Next buttons to jump between results
- 🔎 **Advanced search** - Regex support and search-within-results
- 📑 **Cross-references** - Jump between referenced verses
- 📝 **Notes & annotations** - Add personal notes to verses
- 🌓 **Dark mode** - White text on black background for comfortable reading
- 📖 **Table of Contents** - Collapsible TOC for easy navigation
- 🎨 **Font size control** - Adjust text size to your preference
- 💾 **Offline & standalone** - No internet required, all data embedded

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
