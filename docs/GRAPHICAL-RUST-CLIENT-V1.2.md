# Graphical Rust client shell — v1.2.0

Status: **source prepared, Windows build UNVERIFIED**. Uses `minifb 0.27` as an optional Rust graphics dependency. No Preservation code or game assets are copied.

What it does: Opens a local application window at the configured resolution (1920x1080 by default), draws an original placeholder UI, displays observed FPS, supports capped/uncapped rendering, shows the mouse position with a crosshair, and closes on Escape. Windowed and borderless settings are wired to the window creation. No networking, account login, character rendering, map rendering, NPCs, auto-clicker, or COPS gameplay integration. The simple software framebuffer is for smoke testing only; a future GPU renderer will replace it.

## Windows 11 build/run (PowerShell in `rust-client/`)
1. Install Rust using https://rustup.rs/; check `cargo --version`.
2. `cargo test` — tests the settings library.
3. `cargo run -- init` — creates `client-settings.conf` without overwriting an existing file.
4. `cargo run --features graphics --bin tq-classic-window -- client-settings.conf`
5. Press Escape to close. If 1920x1080 is too large for your screen, edit `width` and `height` in the settings file then retry.

`auto_clicker_enabled` is a configuration placeholder only; no input automation or injected clicks are implemented. The FPS selection affects only drawing rate and never gameplay simulation. The effective render FPS may be lower than the cap depending on hardware and OS scheduling. "Uncapped" can use significant CPU/GPU resources.

## Release gate
- Compile and test on Windows 11, record exact Rust/cargo and GPU versions.
- Verify borderless/windowed mode and physical pixel scale (100%, 125%, 150%) without mouse offsets.
- Verify Alt-Tab, minimized behavior, fullscreen desktop taskbar handling, 1920x1080 at 60/144/240/uncapped.
- Decide on GPU-based renderer and implement independent simulation ticks before client network play.
- Review upstream client, protocol, copyright and license before integrating assets.
