# Backup hardening handoff — 7 October 2026

Prepared locally for root integration. This subtask has not changed the VPS.

`omnisense_ops.py` retains the existing Fernet key and archive layout. Existing authenticated snapshots within the new cap remain readable; no key rotation or production restore occurs.

The operational limit is **64 MiB of total database and rate-key contents**, and 64 MiB per member. Archive headers have a separate 1 MiB allowance, and the manifest has a 64 KiB limit. Fernet encrypts/decrypts a whole message and therefore still has several bounded allocations; this is not an unlimited-size backup system. Database snapshots, tar creation and database verification stream through private temporary files instead of accumulating all database bytes in memory. Source sizes are checked before snapshot work; SQLite page counts and final snapshot sizes also enforce the cap, including WAL growth.

An OS lock prevents overlapping backups and releases automatically on process exit. Atomic publication uses unique private pending files, fsync and cleanup; an old `.pending` file cannot block later writes. Snapshot filenames include UUIDs so runs within the same second cannot overwrite each other. Verification finishes before the latest-success report is published and before old snapshots are pruned. Seven snapshots are retained. Failed verification removes only the new invalid snapshot and leaves prior successful snapshots/report intact.

Restore tests authenticate ciphertext, bound file size before decrypting, bound decompressed tar data and reject duplicate, missing, unlisted, traversal, symlink, sparse and oversized members. The manifest must have version 1 and exactly match all content hashes. SQLite `quick_check` uses explicit validation instead of an optimization-sensitive `assert`. Restore tests never write into production data directories.

Monitoring now reports backup worker failure, unavailable worker state, inactive timer, a missing/changed latest snapshot, and stale/missing success reports. A failure exceeding the 64 MiB cap is visible through the backup unit result at the next monitoring run, even if the previous successful backup is less than 30 hours old.

Windows local verification: `python -m unittest test_backup_hardening test_review_health -v` ran 34 tests, 33 passed and 1 POSIX concurrency test was skipped. Run the same tests on Linux before deployment, plus existing `test_ops` as root because its original key fixture validates root ownership. All new fixtures are synthetic and remain under the workspace.

Backup files remain on the same VPS. Nothing here configures an offsite destination or publishes client data/secrets to Git.
