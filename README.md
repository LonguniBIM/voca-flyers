# Rise Voca Flyers: illustration repair

Open Library & source > Review replacement illustrations. Preview each local picture, then Approve for lessons or Reject / stop using. Approval is stored for the exact asset hash on this device, not in learning history. No image loads from ARASAAC, even with the previous opt-in saved.

OpenMoji remains first. Preferred sourcing order: OpenMoji, Google Material Symbols, Tabler, Phosphor. The two exact local exceptions are Streamline (toothpaste) and Pictogrammers MDI (cupboard). MDI is not Google Material Symbols. The SVGs are included in the offline app; remote OpenMoji pictures still require Save pictures for offline. Not all words have illustrations.

To receive this update, Save & pause, close ALL site/app windows, and reopen. Do NOT clear site data. Keep regular JSON history backups. Sessions, dates, topics, first-correct scoring, hints, skips, audio and resume remain unchanged. History and review preferences are device-local, with no cross-device sync.

The missing PWA icons are restored. The two local SVGs and image licenses are cached with the app. Actual iOS/Android installation and speech still require device testing.

## Maintenance
After editing cached files, run `python scripts/build-offline.py`; verify with `python scripts/build-offline.py --check` and `node --test tests/illustrations.test.cjs`. The apply-illustrations-v2 script is a one-time, guarded migration from the original preview, not a normal build command. Tests use isolated profiles only.

See THIRD_PARTY.md for credits. Never publish learner backups, private reviews, credentials or the original PDF.
