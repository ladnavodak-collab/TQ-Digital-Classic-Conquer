# Rust client track — v1.1.0

**Status:** Original, independent Rust settings implementation. **Not a renderer, launcher, auto-clicker, or networked game client.** No Preservation source files have been copied. Exact compatibility with the Preservation client is not established.

## Reproducible Windows 11 validation
Install Rust stable via https://rustup.rs/ (use its official Windows installer), open PowerShell in `rust-client`, run `cargo test`, then `cargo run -- init` and `cargo run -- check`. File `client-settings.conf` is created locally. Do not run `init` against an existing config; it refuses overwriting.

Settings: 1920x1080 default, windowed or borderless, caps 30/60/120/144/165/240 or uncapped, auto-clicker OFF by default. A setting does not implement an actual feature. Frame-limit pacing only returns target nanoseconds; no render loop exists and no game timing is controlled by FPS.

## Next acceptance criteria
1. Confirm the upstream Preservation source license and pin a commit before reusing any part.
2. On Windows, verify Rust unit tests and build; fix compile errors if any. Rust toolchain is not installed in our current Linux container, so Rust code has NOT been compiled here.
3. Create independent window and rendering backend, prove 1920x1080 mouse coordinates and keyboard events.
4. Document and test 5065 wire protocol with server code. No login traffic is supported now.
5. For official auto-clicker, require explicit enable/disable and authorized actions; server enforces cooldowns. Never bypass anti-cheat checks.
6. Signed patching, supply-chain safeguards, rollback, and crash handling are requirements—not implemented functionality.
