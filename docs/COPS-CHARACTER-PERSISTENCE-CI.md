# Character persistence SQL contract — disposable CI only

The upstream COPS `Player::SQLDATA_*` enum assumes a 28-column **positional** `SELECT * FROM user WHERE account_id = :account_id` result. The new `db/ci_character_schema.sql` defines that exact column order in a disposable MariaDB database with one character per account, a zero-CP database check and a maximum of one rebirth. These are intentionally *test-only* tables and are **not** the final 5065 production database design.

In CI, the schema is installed **after** the existing synthetic-world COPS startup tests, so it cannot mask startup preconditions. The database test creates a disposable account and character, performs the same SQL shape as COPS `createPlayer` and `savePlayer`, retrieves the row to verify persisted stats and map 1002 coordinates, then confirms that the SQL engine rejects both nonzero CP balances and second rebirth.

**Scope:** This verifies a real MariaDB schema and SQL persistence contract, **not** COPS `Database::createPlayer` or `savePlayer` being invoked from an authenticated client. It does not prove that a 5065 executable can log in, render the world or save a player's inventory. A fully authenticated COPS client and end-to-end save/relog integration test remain necessary. Keep the private development server loopback-only.
