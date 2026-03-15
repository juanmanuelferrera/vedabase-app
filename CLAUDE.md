- always use Tauri to build the app
- no preguntes cuando tengas que build el app

## Deploy

- **CF Pages project:** `vedabase-app`
- **Deploy directory:** `deploy/` (NOT `vedabase-app/`)
- **Structure:**
  - `deploy/index.html` → landing page at `app.bhaktiyoga.es/`
  - `deploy/app/` → web reader app at `app.bhaktiyoga.es/app/`
- **Command:** `npx wrangler pages deploy deploy/ --project-name vedabase-app --branch master --commit-dirty=true`
- **IMPORTANT:** Always deploy from `deploy/`, never from `vedabase-app/` directly — that overwrites the landing page
- **Source of truth:** edit files in `vedabase-app/`, then sync to `deploy/app/` before deploying:
  `rsync -av --delete --exclude='generate_letters_html.py' --exclude='landing.html' vedabase-app/ deploy/app/`
- **Service worker:** bump `CACHE_NAME` version in `service-worker.js` and `sw.js` when updating HTML content, otherwise browsers serve stale cached files