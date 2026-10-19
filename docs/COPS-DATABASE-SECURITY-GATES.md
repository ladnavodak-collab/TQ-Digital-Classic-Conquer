# Database startup security checklist

COPS v7 has insecure default database settings and account authentication. Release blockers:
- Require a non-root, least-privilege SQL account.
- Do not store SQL credentials in repository or settings.cfg; inject at runtime.
- Reject missing credentials at startup.
- Remove SQL debug logging of bound parameter values.
- Replace legacy plaintext game-account verification with a vetted password hashing scheme.
- Test login and schema against a disposable database before claiming a playable game server.

Security review remains in progress; this is documentation, not a completed fix.
