# TQ Digital Classic Conquer

**Private development repository.** Do not make this repository public or commit game client assets, credentials or proprietary source.

## Scope
- Target: classic 5065 gameplay; C++ server with a separate Rust client.
- Current GitHub state: **CI bootstrap** with a small compile-tested policy module and Rust settings example, **not the entire Drive v1.3.0 foundation**.
- The full standalone foundation is archived in the private project Google Drive folder.
- **Not a playable game server.** No COPS integration, login or game-world support is claimed.

## Test locally
```sh
cmake -S . -B build -DBUILD_TESTING=ON
cmake --build build --config Debug
ctest --test-dir build -C Debug --output-on-failure
cd rust-client && cargo test --all-targets
```

## Workflow
See `.github/workflows/ci.yml`. CI runs native C++ checks on Ubuntu and Windows, and Rust tests on Ubuntu and Windows.

### Security
- Do not commit passwords, database connection strings, tokens, or licensed proprietary client assets.
- Pull requests must keep core validation on the server.
- Repository visibility must remain **private**.
- This repository is a source bootstrap, not an automatically synced copy of the ZIP archives.
