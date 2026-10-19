Live classic MsgWalk and position persistence

This CI-only localhost protocol probe authenticates a fresh synthetic user against the real COPS C++ server, completes Blowfish/DH game-port login with the one-time transfer token, loads the existing classic character, enters test map 1002, and sends a real encrypted MsgWalk east from (8,8) to (9,8). It checks the server's encrypted echo and polls the disposable MariaDB account's saved coordinates after client disconnect. Server source is also patched to reject walks lacking verified transfer tickets or loaded players and to echo movements only after successful tile validation.

This is **synthetic test geometry** and a Python protocol client. It does not prove the Conquer 5065 client renders Twin City, nor does it validate real art, NPCs, or general-world movement. No public listener should be opened on the basis of this test.
