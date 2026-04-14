#!/usr/bin/env node
// Generate consolidated HTML files from SQLite — one per book
// Embeds all verses inline, no external DB needed at runtime

const Database = require('better-sqlite3');
const fs = require('fs');
const path = require('path');

const DB_PATH = path.join(__dirname, '..', 'src-tauri', 'resources', 'vedabase.db');
const OUT_DIR = path.join(__dirname, '..', 'dist', 'books');

const db = new Database(DB_PATH, { readonly: true });

const BOOKS = {
  bg:'Bhagavad-gītā As It Is',sb:'Śrīmad-Bhāgavatam',cc:'Śrī Caitanya-caritāmṛta',
  noi:'Nectar of Instruction',kb:'Kṛṣṇa, the Supreme Personality of Godhead',
  nod:'The Nectar of Devotion',iso:'Śrī Īśopaniṣad',ssr:'The Science of Self-Realization',
  bbd:'Beyond Birth and Death',bs:'Śrī Brahma-saṁhitā',owk:'On the Way to Kṛṣṇa',
  pop:'The Path of Perfection',poy:'The Perfection of Yoga',pqpa:'Perfect Questions, Perfect Answers',
  rv:'Rāja-vidyā: The King of Knowledge',tlc:'Teachings of Lord Caitanya',
  tlk:'Teachings of Lord Kapila',tqk:'Teachings of Queen Kuntī',lob:'Light of the Bhāgavata',
  ejop:'Easy Journey to Other Planets',ekc:'Elevation to Kṛṣṇa Consciousness',
  lcfl:'Life Comes from Life',rop:'Kṛṣṇa, the Reservoir of Pleasure',
  tpm:'Transcendental Teachings of Prahlāda Mahārāja',tys:'Kṛṣṇa Consciousness: The Topmost Yoga System',
  transcripts:'Transcripts',letters:'Letters',
};

fs.mkdirSync(OUT_DIR, { recursive: true });

function esc(s) { return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function cleanText(s) {
  if (!s) return '';
  return s
    .replace(/^Translation\n/i, '')
    .replace(/^Purport\n/i, '')
    .replace(/^Synonyms\n/i, '')
    .replace(/\s*Donate\s*Thanks to .*/s, '')
    .replace(/\s*His Divine Grace A\.C\. Bhaktivedanta Swami Prabhupāda.*$/s, '')
    .replace(/\s*Content used with permission.*$/s, '')
    .replace(/\s*Privacy policy\s*$/s, '')
    .replace(/\s*Text \d+\s*$/s, '')
    .trim();
}
function nl2br(s) { return (s||'').replace(/\n/g,'<br>'); }

let totalSize = 0;

for (const [slug, name] of Object.entries(BOOKS)) {
  const rows = db.prepare('SELECT ref, verse_text, synonyms, translation, purport FROM verses WHERE book = ? AND lang = ? ORDER BY id').all(slug, 'en');
  if (rows.length === 0) continue;

  const verses = rows.map(r => ({
    ref: r.ref,
    v: cleanText(r.verse_text) || undefined,
    s: cleanText(r.synonyms) || undefined,
    t: cleanText(r.translation) || undefined,
    p: cleanText(r.purport) || undefined,
  }));

  const outFile = path.join(OUT_DIR, slug + '.json');
  fs.writeFileSync(outFile, JSON.stringify(verses));
  const size = fs.statSync(outFile).size;
  totalSize += size;
  console.log(`${slug}: ${rows.length} verses, ${(size/1024/1024).toFixed(1)} MB`);
}

// Generate search index as JSON (just ref + translation for client-side search)
const searchData = db.prepare('SELECT ref, book, translation FROM verses WHERE lang = ? AND translation IS NOT NULL').all('en');
const searchJson = JSON.stringify(searchData);
const searchFile = path.join(OUT_DIR, 'search-index.json');
fs.writeFileSync(searchFile, searchJson);
const searchSize = fs.statSync(searchFile).size;
totalSize += searchSize;

console.log(`\nsearch-index.json: ${searchData.length} entries, ${(searchSize/1024/1024).toFixed(1)} MB`);
console.log(`\nTotal: ${(totalSize/1024/1024).toFixed(1)} MB uncompressed`);

db.close();
