# COPS v7 receive bounds patch — experimental

Run `python tools/patch_cops_bounds.py /path/to/unmodified/COPS-v7-Emulator` in a disposable checkout.

This patch fixes a known unsafe call to `QTcpSocket::read` that passed `bytesAvailable()` into a fixed 4096-byte stack array. It also rejects undersized key-exchange fields and truncated/invalid packet lengths before copies/decoding, with fail-closed disconnects.

**Important:** This is *not* the final network transport. COPS still assumes each TCP read contains complete messages, whereas TCP may split or coalesce frames. The current fix intentionally disconnects on fragmented payloads, which may reject valid connections. The packet processing and cipher-state change require a real stream reassembler, fuzzing, and real patch-5065 client interoperability tests. No claim of exploit-proof networking.

Upstream COPS credentials are still unsafe, and COPS has not been deployed. Never use the patched emulator on the public Internet. Keep upstream notices and check exact license obligations.

CI probe applies this patch to public upstream code in an ephemeral GitHub runner and compiles it using Qt5. The patch is not copied into our main foundation build.
