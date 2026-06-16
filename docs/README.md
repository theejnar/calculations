# Calculations — Web Apps

A collection of browser-based calculation tools. No server needed — everything runs in your browser using Python compiled to WebAssembly (Pyodide).

## Available Calculators

### Distance Combination Calculator (`distance-combination.html`)

Find the best combination of distances with gaps that fit a total length. Supports import/export of settings and preset examples.

**CLI usage:**

```bash
# From a JSON settings file
python3 docs/distance_combination_cli.py -f docs/examples/distance-3-sizes.json

# With inline arguments
python3 docs/distance_combination_cli.py -d "70 95 120" --from-gap 10 --to-gap 20 --total-length 5000

# Export current settings to a file
python3 docs/distance_combination_cli.py -d "70 95 120" --from-gap 10 --to-gap 20 --total-length 5000 -e my-settings.json
```

| Field | Description |
|-------|-------------|
| Distances | 1–10 space-separated values (e.g. `70 95 120`) |
| From gap | Minimum allowed gap between items |
| To gap | Maximum allowed gap between items |
| Total length | Target total length to fill |
| Tolerance (advanced) | How close the result must match the total length (default: `0.001`) |
| Gap step (advanced) | Resolution for rounding the gap value (default: `0.1`) |

### Area Calculator via Triangulation (`area.html`)

Calculate any polygon's area by measuring the sides of surrounding triangles. Supports importing polygon definitions from JSON.

### Pairwise List Sorter (`sort.html`)

Rank a list of items by personal preference using pairwise comparisons. Import, sort, and export.

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
