#!/bin/bash
# Script to create DMG properly with ad-hoc signing
# This method works correctly on macOS

set -e

APP_PATH="$1"
DMG_NAME="$2"
VOLNAME="${3:-Vedabase}"

if [ -z "$APP_PATH" ] || [ -z "$DMG_NAME" ]; then
    echo "Usage: ./create-dmg.sh <path-to-app> <dmg-name> [volume-name]"
    exit 1
fi

TEMP_DMG="${DMG_NAME}_temp.dmg"

echo "Creating temporary DMG..."
hdiutil create -srcfolder "$APP_PATH" -volname "$VOLNAME" -fs HFS+ -format UDRW "$TEMP_DMG"

echo "Converting to compressed DMG..."
hdiutil convert "$TEMP_DMG" -format UDZO -o "$DMG_NAME"

echo "Cleaning up..."
rm "$TEMP_DMG"

echo "DMG created successfully: $DMG_NAME"
