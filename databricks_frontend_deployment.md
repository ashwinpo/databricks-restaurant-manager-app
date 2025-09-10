# Deploying Modern Front-End Frameworks (React/Vite) to Databricks Apps

> A step-by-step playbook with caveats, gotchas, and reusable tricks. Works for React + Vite, Next.js (static export), SvelteKit, or any framework that produces a **static `dist/` (or `build/`) folder**.

---

## 1. High-Level Flow

1. Develop locally – use Vite/CRA/Next.js dev server.
2. Run the framework’s **production build** (`npm run build`).
3. Commit the generated `dist/` folder **into your repo** (yes, really) so Databricks can serve it.
4. In FastAPI (or Flask), mount the `dist` directory **after all API routes**:
   ```python
   from pathlib import Path
   from fastapi.staticfiles import StaticFiles

   build_dir = Path(__file__).parent.parent / "frontend" / "dist"
   app.mount("/", StaticFiles(directory=build_dir, html=True), name="static")
   ```
5. Push code to Databricks Repo → **Sync** → Press **Deploy App**.

---

## 2. Directory Layout

```
my-app/
├─ backend/
│  └─ app.py               # FastAPI entry-point
├─ frontend/
│  ├─ src/                 # React source
│  ├─ dist/                # 💡 Production build (checked-in)
│  └─ vite.config.js
└─ app.yaml                # Databricks App manifest
```

### Why commit `dist/`?
Databricks Apps mount your repo verbatim inside the cluster driver. They don’t run `npm run build` for you.  
If `dist/` isn’t present **at runtime** the static mount will 404 and you’ll see a blank page / old UI.

> ✅  Include `dist/` in Git **and** remove it from `.gitignore` inside `frontend/`.

---

## 3. Vite Configuration Nuances

1. **Base path** must be `/` so asset URLs resolve correctly under the root domain:
   ```js
   // vite.config.js
   export default defineConfig({
     base: '/',
   })
   ```
2. Dev-time proxy (optional):
   ```js
   server: {
     proxy: {
       '/api': 'http://localhost:8000',
     }
   }
   ```
3. Large bundle warnings (>500 kB) are OK; Databricks serves static files via Nginx.

---

## 4. FastAPI Integration Details

| Concern | Best Practice |
|---------|---------------|
| **Mount order** | Define *all* `/api/...` routes first, **then** mount static files. Otherwise the `/api` routes might get swallowed by the static handler. |
| **Env detection** | Use an env var or simple path check to detect whether code is running inside Databricks (OAuth creds) vs local (PAT). |
| **Debug endpoint** | Add `@app.get("/api/debug/frontend")` to dump build-dir metadata. Fantastic for live troubleshooting. |

---

## 5. Common Pitfalls & Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| App shows old/basic UI | `dist/` wasn’t committed OR cached HTML in browser | 1) Commit & sync `dist/` 2) Hard-reload (`Cmd+Shift+R`) |
| 404 on JS/CSS | `base` path wrong | Set Vite `base: '/'` |
| CORS errors in dev | Missing proxy | Add Vite `server.proxy` to forward `/api` |
| Hot-reload not working | Using production build locally | Run `npm run dev` during local work |
| New build not served | Databricks driver still has old code cached | Click **Restart** in the App UI; verify build timestamp via `/api/debug/frontend` |

---

## 6. Cache-Busting Strategy (Optional)

Browsers may cache aggressively. Two simple layers:

1. **HTML changes** ⇒ New content hash in bundled filenames (Vite default).
2. **Static mount** ⇒ Serve with `cache-control: max-age=0` via FastAPI `StaticFiles` (requires custom subclass). Usually Vite hashes are enough.

---

## 7. Automating the Build Step

If you *really* don’t want to commit `dist/`:

1. Add a Databricks **init script** that runs `npm ci && npm run build` inside the cluster driver, **before** FastAPI starts.
2. Drawback: increases cold-start time and needs network access to npm registry.

For demos & POCs, committing `dist/` is simpler.

---

## 8. CI/CD Example (GitHub Actions)

```yaml
name: Build & Push Databricks App
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Node
        uses: actions/setup-node@v4
        with:
          node-version: 18
      - run: |
          cd frontend
          npm ci
          npm run build
      - name: Commit build artifacts
        run: |
          git config user.name github-actions
          git config user.email github-actions@github.com
          git add frontend/dist -f
          git commit -m "Update dist [skip ci]" || echo "No changes"
          git push
```

Once merged, let Databricks Repo auto-sync or call the Repos API to pull.

---

## 9. Debug Checklist

1. `GET /api/debug/frontend` returns `build_dir_exists: true` and list of assets.
2. Open browser DevTools → *Network* → disable cache → reload.
3. Confirm HTML `<title>` is the new one.
4. Verify JS bundle contains keywords from your latest code (`grep` locally).

---

## 10. Reusable Boilerplate Snippet

```python
# backend/app.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

# API routes here …

# ---- Static Front-end ----
build_dir = Path(__file__).parent.parent / "frontend" / "dist"
if build_dir.exists():
    app.mount("/", StaticFiles(directory=build_dir, html=True), name="static")
else:
    import logging; logging.warning("Frontend build not found: %s", build_dir)
```

---

Happy deploying! 🎉
