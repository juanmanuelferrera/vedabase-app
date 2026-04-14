#!/usr/bin/env node
// Extract verse data from R2 HTML files with proper devanagari + line breaks
// Replaces the DB-based generate-html.js for books that have R2 HTML pages

const fs = require('fs');
const path = require('path');

const R2_DIR = '/Users/jaganat/git_projects/vedabase-site/public/en/library';
const OUT_DIR = path.join(__dirname, '..', 'dist', 'books');

const BOOKS_WITH_VERSES = ['bg', 'sb', 'cc', 'iso', 'noi', 'bs'];

function stripHtml(s) {
  return (s || '')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/p>/gi, '\n\n')
    .replace(/<\/div>/gi, '\n')
    .replace(/<em>/gi, '').replace(/<\/em>/gi, '')
    .replace(/<strong>/gi, '').replace(/<\/strong>/gi, '')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#x27;/g, "'")
    .replace(/&#39;/g, "'")
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

function cleanTrailing(s) {
  return (s || '')
    .replace(/\s*(?:TEXT|Text)\s+\d+(?:\s+(?:TEXT|Text)\s+\d+)*\s*$/s, '')
    .replace(/\s*Donate\s*Thanks to .*/s, '')
    .replace(/\s*His Divine Grace A\.C\. Bhaktivedanta Swami Prabhupāda.*$/s, '')
    .replace(/\s*Content used with permission.*$/s, '')
    .replace(/\s*Privacy policy\s*$/s, '')
    .trim();
}

function extractVerse(htmlFile, book, ref) {
  try {
    const html = fs.readFileSync(htmlFile, 'utf8');

    // Extract devanagari
    let devanagari = '';
    const devMatch = html.match(/<div[^>]*text-center[^>]*>([\u0900-\u097F][\s\S]*?)<\/div>/);
    if (devMatch) {
      devanagari = stripHtml(devMatch[1]).trim();
    }

    // Extract transliteration (roman verse text) - in italic/em centered div
    let verseText = '';
    const vtMatch = html.match(/<div[^>]*text-center[^>]*italic[^>]*>[\s\S]*?<em>([\s\S]*?)<\/em>/);
    if (vtMatch) {
      verseText = stripHtml(vtMatch[1]).trim();
    } else {
      // Try alternate pattern
      const vt2 = html.match(/class="av-verse_text"[\s\S]*?<div[^>]*>([\s\S]*?)<\/div>/);
      if (vt2) verseText = stripHtml(vt2[1]).trim();
    }

    // Extract synonyms
    let synonyms = '';
    const synMatch = html.match(/class="av-synonyms"[\s\S]*?<div[^>]*copy[^>]*>([\s\S]*?)<\/div>\s*<\/div>\s*<\/div>/);
    if (synMatch) {
      synonyms = stripHtml(synMatch[1]).trim();
    } else {
      const syn2 = html.match(/Synonyms<\/h2>[\s\S]*?<div[^>]*copy[^>]*>([\s\S]*?)<\/div>/);
      if (syn2) synonyms = stripHtml(syn2[1]).trim();
    }

    // Extract translation — stop at av-purport or next section
    let translation = '';
    const transMatch = html.match(/class="av-translation"[\s\S]*?<div[^>]*copy[^>]*>([\s\S]*?)<\/div>\s*<\/div>\s*<\/div>\s*<div class="av-/);
    if (transMatch) {
      translation = stripHtml(transMatch[1]).trim();
    } else {
      const tr2 = html.match(/Translation<\/h2>[\s\S]*?<div[^>]*copy[^>]*>([\s\S]*?)<\/div>\s*<\/div>\s*(?:<\/div>|<div class="av-)/);
      if (tr2) translation = stripHtml(tr2[1]).trim();
    }

    // Extract purport — stop at footer or prev/next nav
    let purport = '';
    const purpMatch = html.match(/class="av-purport"[\s\S]*?<div[^>]*copy[^>]*>([\s\S]*?)(?:<div[^>]*id="footer"|<div class="mt-10|<\/main>|$)/);
    if (purpMatch) {
      purport = stripHtml(purpMatch[1]).trim();
    } else {
      const pu2 = html.match(/Purport<\/h2>[\s\S]*?<div[^>]*copy[^>]*>([\s\S]*?)(?:<div[^>]*id="footer"|<div class="mt-10|<\/main>|$)/);
      if (pu2) purport = stripHtml(pu2[1]).trim();
    }

    // Clean trailing nav text
    purport = cleanTrailing(purport);
    translation = cleanTrailing(translation);

    if (!verseText && !translation && !purport) return null;

    const result = { ref };
    if (devanagari) result.d = devanagari;
    if (verseText) result.v = verseText;
    if (synonyms) result.s = synonyms;
    if (translation) result.t = translation;
    if (purport) result.p = purport;
    return result;
  } catch (e) {
    return null;
  }
}

// Walk directories and find all verse HTML files
function walkBook(bookDir, book) {
  const verses = [];

  function walk(dir, prefix) {
    let entries;
    try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
    for (const e of entries) {
      if (!e.isDirectory()) continue;
      const subPath = prefix ? prefix + '/' + e.name : e.name;
      const indexFile = path.join(dir, e.name, 'index.html');
      if (fs.existsSync(indexFile) && /\d/.test(e.name)) {
        const ref = book + '/' + subPath;
        const v = extractVerse(indexFile, book, ref);
        if (v) verses.push(v);
      }
      walk(path.join(dir, e.name), subPath);
    }
  }

  walk(bookDir, '');
  return verses;
}

// Main
fs.mkdirSync(OUT_DIR, { recursive: true });

for (const book of BOOKS_WITH_VERSES) {
  const bookDir = path.join(R2_DIR, book);
  if (!fs.existsSync(bookDir)) { console.log(book + ': no R2 directory'); continue; }

  const verses = walkBook(bookDir, book);
  if (verses.length === 0) { console.log(book + ': no verses found'); continue; }

  // Sort numerically
  verses.sort((a, b) => {
    const pa = a.ref.replace(book + '/', '').split('/').map(Number);
    const pb = b.ref.replace(book + '/', '').split('/').map(Number);
    for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
      if ((pa[i] || 0) !== (pb[i] || 0)) return (pa[i] || 0) - (pb[i] || 0);
    }
    return 0;
  });

  // Check extraction quality
  let withDev = 0, withVT = 0, withSyn = 0, withTr = 0, withPu = 0;
  for (const v of verses) {
    if (v.d) withDev++;
    if (v.v) withVT++;
    if (v.s) withSyn++;
    if (v.t) withTr++;
    if (v.p) withPu++;
  }

  const outFile = path.join(OUT_DIR, book + '.json');
  fs.writeFileSync(outFile, JSON.stringify(verses));
  const size = (fs.statSync(outFile).size / 1024 / 1024).toFixed(1);
  console.log(`${book}: ${verses.length} verses, ${size} MB (dev:${withDev} vt:${withVT} syn:${withSyn} tr:${withTr} pu:${withPu})`);
}

console.log('\nDone. Books without R2 HTML still use generate-html.js (DB-based).');
