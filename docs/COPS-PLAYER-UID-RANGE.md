# COPS player UID invariant

COPS classifies entities as players only for UIDs in the range 1000000 through 1999999999. Disposable MariaDB character IDs must start at 1000000; otherwise GameMap::enterRoom does not unpack floor cells and a subsequent walk can dereference absent map data. This diagnostic map is not a retail client asset.
