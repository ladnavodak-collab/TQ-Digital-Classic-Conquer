# CI validation

This pull request is deliberately opened to exercise private GitHub Actions on both Windows and Ubuntu.

## Expected jobs
- C++ on Windows and Ubuntu: configure with CMake, build, and run CTest.
- Rust on Windows and Ubuntu: cargo test.

## Limitations
These are bootstrap checks only. The full COPS server and Preservation-inspired game client are not included yet.

## Safety
- Keep repository visibility private.
- Do not print secrets, tokens or credentials in CI logs.
- No uploaded proprietary client binaries.
- No deploy, cloud hosting, or public service exposure.

If jobs remain pending without runners, check GitHub Settings > Actions > General for repository Actions enablement and runner availability.
