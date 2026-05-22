# Distance Combination Calculator — Web App

A browser-based calculator that finds the best combination of distances with gaps fitting a total length. Runs entirely client-side using Python compiled to WebAssembly (Pyodide).

## Test locally

Serve the `docs/` folder with any static HTTP server:

```bash
python3 -m http.server 8080 -d docs
```

Then open http://localhost:8080 in your browser.

> First load takes a few seconds while the Python runtime (Pyodide) downloads and initializes.

## Publish on GitHub Pages

1. Push this repository to GitHub.
2. Go to your repository on GitHub → **Settings** → **Pages**.
3. Under **Build and deployment**:
   - Source: **Deploy from a branch**
   - Branch: `main` (or your default branch)
   - Folder: `/docs`
4. Click **Save**.
5. After a minute or two, your site will be live at:
   ```
   https://<your-username>.github.io/<repo-name>/
   ```

## Inputs

| Field | Description |
|-------|-------------|
| Distances | 1–10 space-separated values (e.g. `25.5 40 80`) |
| From gap | Minimum allowed gap between items |
| To gap | Maximum allowed gap between items |
| Total length | Target total length to fill |
| Tolerance (advanced) | How close the result must match the total length (default: `0.001`) |
| Gap step (advanced) | Resolution for rounding the gap value (default: `0.1`) |
