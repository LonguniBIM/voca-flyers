# Rise Voca Flyers

An offline-capable, topic-based English word builder for phones, tablets, and computers. The source vocabulary, clues, original topic membership, stable IDs, first-correct scoring, and local history schema are preserved.

## Learn and resume
Choose topics and 5 / 10 / 15 / 20 / All, or a custom count. Listen, arrange letters, retry, use Hint or Skip. A new session avoids duplicate spellings. Save & pause and Resume keep the original session settings and progress. Pictures appear after the first correct answer, not as answer leaks.

## Illustration expansion
Open **Library & source > Review replacement illustrations**. Filter by Topic, Source, Review status, and word or Vietnamese meaning. The gallery uses 24-card pages. Select **Preview local picture**, then **Approve for lessons** or **Reject / stop using**. Image-loading failures disable approval. Review does not create sessions, attempts, or mastery.

The existing 170 user-approved OpenMoji mappings are unchanged. There are 469 attached candidates in total: the original two replacements and 467 additional word/sense mappings. These candidates are NOT automatically approved. The 263 remaining vocabulary meanings without a suitable candidate stay explicitly missing; 52 proper names are excluded from illustration coverage. See `docs/IMAGE_COVERAGE.md` and `data/image-coverage.json` for auditable counts.

OpenMoji remains primary. Explicit selected fallback images use Pictogrammers Material Design Icons, Mulberry Symbols by Steve Lee, and the original Streamline toothpaste illustration. These are separate libraries; Pictogrammers MDI is not Google Material Symbols. The two rejected ARASAAC references are never requested. New truck and Moon replacements require a fresh approval; their old rejected images cannot reappear.

New approvals are scoped to the word ID and exact file hash. Previously saved approval keys for the original toothpaste and House cupboard candidates remain compatible. A House cupboard approval does not automatically approve the separate School cupboard record. Decisions and their timestamps are stored on this device, never published or treated as learning history.

All 414 distinct local SVGs are downloaded, source-pinned, hash-checked, and bundled with the offline app. Meaning-level screening is separate from technical checks, and final suitability remains a parent decision. Previously approved remote OpenMoji pictures keep **Save pictures for offline** and **Check saved pictures**. Do not assume speech works offline merely because pictures do.

## JSON library and exports
`data/library.json` is the canonical content library: all 954 original records, including 902 vocabulary senses/forms and 52 proper names. `data/illustrations.json` is the image catalog. A deterministic build embeds identical copies in the HTML so runtime startup does not require a second fetch.

**Export library JSON** preserves the original library-only export. The review panel adds:

- **Export library + images (JSON)**: all content, source provenance, and image references; no private history or device approvals. Relative image files remain separate assets, not embedded binary data in the JSON.
- **Export all image reviews (JSON)**: all candidate records and the actual decisions and timestamps on this device, regardless of filters or page.
- **Export words still missing images (JSON)**: all unresolved vocabulary senses; proper names excluded.

These exports are not substitutes for a complete learning-history backup.

## Voice settings on Safari / iPadOS

Open **Library & source > Illustrations & audio > English voice**. The app now exposes a preferred English accent, the English voices currently reported by the device, speaking speed, **Refresh voices**, and **Test voice**. The in-session speed selector and the library speed selector stay synchronized.

A selected voice is stored in local app preferences by voice URI plus name/language fallback. If iPadOS removes or renames that voice after an OS update, the saved choice is retained but the app falls back to a usable English voice for the selected accent instead of blocking learning. If the voice list is initially empty on Safari, use **Refresh voices** or **Test voice** after the page is fully open.

Voice availability is controlled by the browser and operating system. A voice marked on-device is preferred for offline use when available, but PWA installation alone does not guarantee that every system voice can speak offline. Voice tests do not create sessions, attempts, listening events, or other learning-history evidence.

## Learning history and backups
Sessions, By topic, and By word views preserve date/time, selected versus actually studied topics, attempts, first-correct time, hints, listening requests, transcript support, skipped/unseen outcomes, estimated active time, and elapsed time. Session filters include dates, studied topic, and status. Reports preserve original question snapshots. No automatic last-50-session deletion is used.

Use **Back up all history (JSON)** and **Restore / merge backup** for progress. Full backups include unfinished sessions; identical data is ignored on import and conflicts are rejected rather than overwritten. Filtered CSV exports and single-session reports are different formats. History stays in this browser/app storage container and origin; there is no automatic cross-device sync. Private browsing, deletion, and storage eviction can remove it. A durable-storage request is not a backup.

## Receive updates
Use Save & pause, close all windows/tabs for the app, and reopen. Do not clear site data to update. Service-worker updates do not force activation in a running lesson or delete the history database. The offline status becomes ready only after all declared files are saved. Installation downloads run with bounded concurrency; a failed new cache is removed only after all workers settle.

## Maintenance and tests

```text
python scripts/sync-catalog.py
python scripts/build-coverage.py
python scripts/build-offline.py
python scripts/sync-catalog.py --check
python scripts/build-coverage.py --check
python scripts/build-offline.py --check
node --test tests/illustrations.test.cjs
python tests/browser_illustrations.py --report /temporary/path/browser-report.json
```

On Windows with installed Edge, add `--channel msedge` to the browser test. Tests use disposable profiles and never touch learner browser data. Physical iOS/Android installation and actual audible speech still require real-device checks.

Image mappings are explicit in `scripts/image-expansion-map.tsv`. `scripts/expand-illustrations.py --cache /temporary/download-cache` downloads those pinned sources; inspect actual rendered files before accepting any addition, then run synchronization, coverage, offline build, and tests. The old `apply-illustrations-v2.py` script is a one-time historical migration, not a normal build command. GitHub Actions validates changes with read-only repository permissions.

Preserve SVG bytes and hashes. `.gitattributes` normalizes source text to LF while preserving SVG, PNG, CSV, and license payloads. Keep unreviewed or unsuitable candidates out of lessons.

See `THIRD_PARTY.md` and the image manifest for credits. Do not publish learner backups, private review exports, credentials, or the original source PDF. The image licenses do not establish redistribution rights for the supplied word list.
