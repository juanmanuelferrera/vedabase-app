# Installing on macOS

Since this app is not signed with an Apple Developer certificate, macOS Gatekeeper will block it by default. Follow these steps to install:

## Installation Steps

1. **Download** the `.dmg` file from the [releases page](https://github.com/juanmanuelferrera/bhagavad-gita-app/releases)

2. **Open** the DMG file and drag the app to your Applications folder

3. **Bypass Gatekeeper** using one of these methods:

   ### Method 1: Right-click method (easiest)
   - Right-click (or Control-click) on the app
   - Select "Open" from the menu
   - Click "Open" in the dialog that appears
   - The app will now open and be remembered as safe

   ### Method 2: System Settings
   - Try to open the app normally (it will be blocked)
   - Go to System Settings → Privacy & Security
   - Scroll down to the "Security" section
   - Click "Open Anyway" next to the message about the blocked app
   - Click "Open" to confirm

   ### Method 3: Terminal (advanced)
   ```bash
   xattr -cr /Applications/Bhagavad-gita.app
   ```

## Why is this necessary?

This app is not signed with an Apple Developer certificate ($99/year). It's completely safe and open source - you can review the code on GitHub.

## Questions?

If you have any issues, please open an issue on [GitHub](https://github.com/juanmanuelferrera/bhagavad-gita-app/issues).
