use rusqlite::Connection;
use serde::Serialize;
use std::sync::Mutex;
use tauri::{Manager, State};

struct DbState(Mutex<Connection>);

#[derive(Serialize)]
struct SearchResult {
    r#ref: String,
    book: String,
    url: String,
    translation: String,
    snippet: String,
}

#[derive(Serialize)]
struct SearchResponse {
    query: String,
    lang: String,
    count: usize,
    results: Vec<SearchResult>,
}

#[tauri::command]
fn search(db: State<DbState>, query: String, lang: String, book: Option<String>, limit: Option<usize>) -> Result<SearchResponse, String> {
    let conn = db.0.lock().map_err(|e| e.to_string())?;
    let limit = limit.unwrap_or(20).min(100);

    let mut sql = String::from(
        "SELECT v.ref, v.book, v.url, v.translation, \
         snippet(verses_fts, 6, '<b>', '</b>', '...', 40) as snip \
         FROM verses_fts \
         JOIN verses v ON v.id = verses_fts.rowid \
         WHERE verses_fts MATCH ?1 AND v.lang = ?2"
    );
    let mut params: Vec<Box<dyn rusqlite::types::ToSql>> = vec![
        Box::new(query.clone()),
        Box::new(lang.clone()),
    ];

    if let Some(ref b) = book {
        sql.push_str(" AND v.book = ?3");
        params.push(Box::new(b.clone()));
    }

    sql.push_str(" ORDER BY rank LIMIT ?");
    params.push(Box::new(limit as i64));

    let param_refs: Vec<&dyn rusqlite::types::ToSql> = params.iter().map(|p| p.as_ref()).collect();

    let mut stmt = conn.prepare(&sql).map_err(|e| e.to_string())?;
    let results: Vec<SearchResult> = stmt
        .query_map(param_refs.as_slice(), |row| {
            Ok(SearchResult {
                r#ref: row.get(0)?,
                book: row.get(1)?,
                url: row.get(2)?,
                translation: row.get::<_, Option<String>>(3)?.unwrap_or_default(),
                snippet: row.get::<_, Option<String>>(4)?.unwrap_or_default(),
            })
        })
        .map_err(|e| e.to_string())?
        .filter_map(|r| r.ok())
        .collect();

    let count = results.len();
    Ok(SearchResponse { query, lang, count, results })
}

#[tauri::command]
fn search_synonyms(db: State<DbState>, original: String, lang: String) -> Result<Vec<SearchResult>, String> {
    let conn = db.0.lock().map_err(|e| e.to_string())?;
    let pattern = format!("%{}%", original);

    let mut stmt = conn
        .prepare(
            "SELECT ref, book, url, synonyms, '' as snip \
             FROM verses WHERE synonyms LIKE ?1 AND lang = ?2 \
             ORDER BY ref LIMIT 100",
        )
        .map_err(|e| e.to_string())?;

    let results: Vec<SearchResult> = stmt
        .query_map(rusqlite::params![pattern, lang], |row| {
            Ok(SearchResult {
                r#ref: row.get(0)?,
                book: row.get(1)?,
                url: row.get(2)?,
                translation: row.get::<_, Option<String>>(3)?.unwrap_or_default(),
                snippet: String::new(),
            })
        })
        .map_err(|e| e.to_string())?
        .filter_map(|r| r.ok())
        .collect();

    Ok(results)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }

            // Open or create the SQLite database
            let app_dir = app
                .path()
                .app_data_dir()
                .expect("failed to get app data dir");
            std::fs::create_dir_all(&app_dir).ok();
            let db_path = app_dir.join("vedabase.db");

            let conn = Connection::open(&db_path).expect("failed to open database");

            // Create tables if they don't exist
            conn.execute_batch(
                "CREATE TABLE IF NOT EXISTS verses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ref TEXT NOT NULL,
                    book TEXT NOT NULL,
                    lang TEXT NOT NULL DEFAULT 'en',
                    url TEXT NOT NULL,
                    verse_text TEXT,
                    synonyms TEXT,
                    translation TEXT,
                    purport TEXT,
                    UNIQUE(ref, lang)
                );
                CREATE VIRTUAL TABLE IF NOT EXISTS verses_fts USING fts5(
                    ref, book, lang, verse_text, synonyms, translation, purport,
                    content='verses', content_rowid='id'
                );
                CREATE TRIGGER IF NOT EXISTS verses_ai AFTER INSERT ON verses BEGIN
                    INSERT INTO verses_fts(rowid, ref, book, lang, verse_text, synonyms, translation, purport)
                    VALUES (new.id, new.ref, new.book, new.lang, new.verse_text, new.synonyms, new.translation, new.purport);
                END;
                CREATE TRIGGER IF NOT EXISTS verses_ad AFTER DELETE ON verses BEGIN
                    INSERT INTO verses_fts(verses_fts, rowid, ref, book, lang, verse_text, synonyms, translation, purport)
                    VALUES ('delete', old.id, old.ref, old.book, old.lang, old.verse_text, old.synonyms, old.translation, old.purport);
                END;"
            ).expect("failed to create tables");

            app.manage(DbState(Mutex::new(conn)));
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![search, search_synonyms])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
