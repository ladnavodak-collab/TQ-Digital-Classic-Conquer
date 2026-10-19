# Google Drive workflow

Direct Google Drive integration is not currently available in this ChatGPT environment. This package is therefore prepared locally for the user to upload.

Suggested Drive layout:
- `TQ Digital Classic Conquer/01 Project Docs/`
- `TQ Digital Classic Conquer/02 Source Archives/`
- `TQ Digital Classic Conquer/03 Database Migrations/`
- `TQ Digital Classic Conquer/04 Content Data/`
- `TQ Digital Classic Conquer/05 Builds and Releases/`
- `TQ Digital Classic Conquer/06 Backups/`

Recommended workflow:
1. Keep active source code in Git (local or a private repository).
2. Use Drive for milestone ZIPs, documentation, approved assets, SQL backups, and release artifacts.
3. Never store passwords, production keys, or database credentials in Drive folders shared broadly.
4. Name snapshots `YYYY-MM-DD_milestone-description.zip`.
5. Keep at least one backup separate from the active project.
6. Test restoring a backup; a backup that has never been restored is unverified.

Current integration status: unavailable/disabled by administrator. No files have been uploaded to Drive by this package.
