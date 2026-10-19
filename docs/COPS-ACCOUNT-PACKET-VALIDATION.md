# Login packet field validation (COPS)

The legacy COPS `MsgAccount` handler receives fixed-size arrays `Account`, `Password` and `Server`, then treats them as C strings. Before this patch, `setAccount` ran before validating that the incoming account field was NUL-terminated, potentially reading beyond the packet. The account name is now stored only after successful credential validation; the handler validates account and server fields before use, checks the decrypted password's terminator, and requires the initial unauthenticated state.

The patch is applied to the disposable upstream COPS checkout before compilation in the MariaDB smoke workflow. **This does not authenticate a 5065 client**. The upstream game server still trusts the client-provided account UID/token in `MsgConnect` without a server-verified, expiring transfer token. That remains a security-critical blocker before public access or any successful gameplay claim. Keep listeners bound to loopback.
