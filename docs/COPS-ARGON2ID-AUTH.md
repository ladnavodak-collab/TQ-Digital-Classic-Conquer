# COPS account authentication: Argon2id fail-closed verification

This patch replaces COPS's direct comparison of plaintext account credentials with libsodium's `crypto_pwhash_str_verify`. It accepts only `$argon2id$` encoded hashes and rejects legacy plaintext passwords; there is deliberately **no plaintext fallback**. Password hashes must be generated with a vetted Argon2id library, using unique salts and current parameters.

**Database schema migration is required:** inspect the real `account.password` column before deployment and expand it to at least `VARCHAR(255)` with compatible character encoding, after an offline backup. Do not copy or publish existing password values. Existing accounts need password resets or a carefully reviewed, offline migration. Do not execute a blind schema rewrite against user data.

Libsodium developer headers/library are required. The CI test builds against system libsodium on Ubuntu. On Windows, configure an approved libsodium SDK; no crypto compatibility fallback is permitted.

This only hardens comparison. It does NOT solve protocol compatibility, credential rate limits/lockouts, client transport weaknesses, SQL schema availability, or gameplay. A real client login has **not** been tested.

Patch application order: `patch_cops_bounds.py`, `patch_cops_dh_validation.py`, `patch_cops_db_startup.py`, then `patch_cops_argon2id.py` on a disposable pinned upstream checkout.
