#!/bin/bash
# Build the SQLite database for the Tauri app from vedabase-site data
# Usage: ./scripts/build-db.sh

set -e

SITE_DIR="../vedabase-site"
DB_PATH="src-tauri/resources/vedabase.db"

mkdir -p src-tauri/resources

echo "Building vedabase.db from $SITE_DIR/data/..."

# Remove old DB
rm -f "$DB_PATH"

# Create schema
sqlite3 "$DB_PATH" < "$SITE_DIR/schema.sql"

echo "Loading English data..."
for f in "$SITE_DIR"/data/insert_0*.sql; do
  echo "  $(basename $f)"
  sqlite3 "$DB_PATH" < "$f"
done

# Load additional English data
for f in "$SITE_DIR"/data/insert_new_books.sql "$SITE_DIR"/data/insert_remaining_books.sql "$SITE_DIR"/data/insert_letters.sql "$SITE_DIR"/data/insert_missing_letters.sql "$SITE_DIR"/data/insert_transcripts.sql; do
  if [ -f "$f" ]; then
    echo "  $(basename $f)"
    sqlite3 "$DB_PATH" < "$f"
  fi
done

# Load Spanish data
if [ -d "$SITE_DIR/data/es" ]; then
  echo "Loading Spanish data..."
  for f in "$SITE_DIR"/data/es/insert_es_*.sql; do
    echo "  $(basename $f)"
    sqlite3 "$DB_PATH" < "$f"
  done
fi

# Show stats
echo ""
echo "Database stats:"
sqlite3 "$DB_PATH" "SELECT lang, count(*) as verses FROM verses GROUP BY lang;"
echo ""
ls -lh "$DB_PATH"
echo ""
echo "Done! Database at: $DB_PATH"
