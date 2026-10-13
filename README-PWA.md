# VectorCraft PWA on GitHub Pages

This fork extends the upstream [VectorCraft](https://github.com/storytold/vectorcraft) browser/WebAssembly build with PWA packaging.

## Hosting

Repository: https://github.com/CptNope/vectorcraft

1. Set **Settings → Pages → Build and deployment → Source** to **GitHub Actions**.
2. Open **Actions → Deploy VectorCraft PWA to GitHub Pages**. Enable workflows in the fork if prompted.
3. Run the deployment workflow (or push a relevant change to `main`).
4. When the deployment is successful, visit https://cptnope.github.io/vectorcraft/ .

The workflow compiles the **fork's own Rust code** using the upstream Trunk build with relative URLs, creates install icons and a service worker, preserves applicable license notices, and publishes the static `dist/web` build.

Install on Android using your browser's **Install app / Add to Home Screen** option, or on iPad in Safari using **Share → Add to Home Screen**.

## Offline usage

After installation, open the editor online once and let all WASM/JS/fonts load. Subsequent sessions can use cached files offline. Offline availability depends on browser storage policy and whether the necessary assets were cached. The service worker does not provide file synchronization.

## Important

- The original VectorCraft editor is retained; this does **not** add AI or Apple Pencil/S Pen pressure features.
- GitHub Pages is a static host; any future AI/MCP service requires a separate backend.
- The editor's upstream license files and NOTICE are preserved, and its ArtCraft brand assets have separate trademark restrictions. This PWA uses generic icons.
- WebAssembly may require compatible graphics APIs on mobile browsers. See [upstream web-hosting notes](https://github.com/storytold/vectorcraft/blob/main/packaging/web/README.md).
