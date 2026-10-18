# Stim Lab

A static site on GitHub Pages (https://pweisbro.github.io/artifacts/; the repo and URL keep the old "artifacts" name so existing links and Home Screen icons keep working), used mostly as a home-screen web app on iPhone and iPad. `index.html` is the homepage that lists every app; each app is one self-contained HTML page in the repo root.

## Whenever an app is added, renamed or removed, update the homepage in the same change

1. **`index.html`**: add, edit or remove the app's entry in the `APPS` array near the top of the script. Required: `name`, `href`, `blurb` (one plain sentence or two on what you do in it). Optional: `ground` (the app's background color), `accent`, `titleClass` (a CSS class that sets the name in the app's own typeface; add the class and its Google Font next to `.t-bench` / `.t-ink`), and `art` (a key in `ARTS` for a custom live preview). Without `art`, the tile gets the generic accent-color glow.
2. **The app page**: give it a "Back to Stim Lab" link to `./`, placed where it fits that app's UI. Home-screen web apps have no browser back button, so this is the only way home. Reuse the 2x2 grid icon from `spectrum-bench.html` or `resonant-ink.html` and keep `aria-label="Back to Stim Lab"`.
3. **`sw.js`**: add the page to `CORE` and bump the `CACHE` version (`artifacts-vN`) so it works offline.
4. **`README.md`**: add a short section for the app.

## Conventions

- Pages are self-contained: inline CSS and JS, fonts only from Google Fonts, no build step.
- Links between pages are relative (`./`, `name.html`) so the site keeps working if the repo is renamed.
- Every page registers `sw.js`.
- An app can also be added to the Home Screen on its own, opening straight to its page: give it a `<name>.webmanifest` (`id` and `start_url` = its page, `scope` = `./`), its own icons, and the `apple-mobile-web-app-*` meta tags plus `<link rel="manifest">` pointing at that manifest, as `resonant-ink.html` does. List the manifest and icons in `sw.js` `CORE`.
- Check new or changed pages at phone width (393x852) and iPad width (1032x1376) before pushing.
