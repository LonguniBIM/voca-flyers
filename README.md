# Rise Voca Flyers PWA - mobile preview

## Delivery status

This is a buildable, hostable PWA preview, not a live website, installed native app, or app-store release. It preserves the existing topic-based word builder and local learning-history format. No learner sessions or synthetic test records are bundled.

Use `index.html` through a stable HTTPS address on a phone or tablet. Opening the ZIP or a downloaded HTML file directly does not install a PWA. The ZIP contains an offline-capable application shell, manifest, app icons, and service worker. Provider pictures are downloaded separately on the learner's device. English audio uses available device/browser voices; offline speech is not guaranteed.

## First installation

1. Extract the PWA ZIP. Upload the CONTENTS of this folder to a dedicated HTTPS site or fixed subfolder, retaining relative paths. Serve `sw.js` as JavaScript; avoid long-lived HTTP caching of `sw.js`, `index.html` and the manifest. `_headers` is an optional hosting-provider hint, not a universal configuration.
2. Open the HTTPS address on the target device. Wait for `App and vocabulary ready offline`. This only checks application files, not images or speech.
3. Android: use the browser menu's Install app / Add to Home screen action. A custom Install app button appears only when the browser supports the install-prompt event. iPhone/iPad: open Safari, Share, Add to Home Screen, enable Open as Web App when offered, then Add. Browser/OS wording can vary.
4. Open the installed icon and run the device acceptance check below. Do not assume the browser tab and installed app share storage on every platform; import the backup inside the installed app when needed.

For computer-only development, a local server is sufficient:

```bash
python -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/index.html` on THAT computer. A phone's localhost is the phone itself. Plain HTTP to a computer's LAN IP is not a substitute for HTTPS PWA deployment.

Choose a fixed site/origin before regular learning. Confirm your right to publish the supplied vocabulary before public hosting; this build does not establish redistribution permission for the source PDF. Private HTTPS hosting is an alternative.

## Preserve existing history

In the old app, use Learning history > Back up all history (JSON). Save the file outside the browser. In the installed PWA, use Restore / merge backup. Identical records are ignored; conflicting versions are rejected without overwriting.

History remains local to the browser/app storage container and origin. Installing a PWA does not add cross-device synchronization. Separate devices or profiles do not automatically share sessions. Clearing site data, removing an app, private browsing, or storage eviction can remove data. Request durable storage is best-effort, not a backup. Keep JSON backups, especially before changing the hosting address.

## Pictures

OpenMoji is the primary provider. The supplied review approves 170 word/sense mappings using 164 distinct image URLs. `truck` and `Moon` were marked unclear and are held back. Approved OpenMoji pictures are not replaced by ARASAAC.

In Library & source, enable Allow online picture loading, or select Save pictures for offline to download the approved images. This action contacts image providers but does not send learning history. The screen reports how many DISTINCT image files are saved and any failures. Check the actual saved count before relying on offline pictures. Image files are not already included in this ZIP.

Two initial ARASAAC candidates are available for `toothpaste` and the House sense of `cupboard`. Use Preview ARASAAC candidates before enabling Try 2 unreviewed ARASAAC candidates in practice. These are not user-approved, and their live PNG responses and visual suitability could not be confirmed in the build environment. Many vocabulary items still have no image. Failure or missing coverage does not stop the quiz.

OpenMoji artwork is CC BY-SA 4.0. ARASAAC pictograms are CC BY-NC-SA 4.0; the candidate opt-in is for non-commercial use only. See THIRD_PARTY.md. No font files are included.

## Audio and touch

All learning actions work through touch buttons; a physical keyboard is optional. Phone letter targets are at least 44 CSS pixels. Original keyboard shortcuts remain on computers.

Tap Listen if automatic speech is blocked. The app prefers an available local English voice; when offline, it avoids known remote-only voices. A local voice still needs a real-device test. If audio fails, the written-clue fallback remains available and is tracked as transcript support. No prerecorded full-library audio pack is included.

## Updates

New app versions wait rather than force-refresh a lesson. When the update message appears, use Save & pause, close ALL windows/tabs for the site, and reopen. The worker does not delete learning-history IndexedDB. Back up history before updates anyway. Keep old hashed `pwa-*.js` files during a deployment transition, or use an atomic static-site deployment.

## Required device acceptance check

- Open a two-word session, enter some letters, Save & pause, close and reopen the SAME installed app, then Resume. Verify the words, count, letters and history are preserved.
- Save pictures, note the successful count, enable airplane mode, reopen the installed app and finish a short quiz. Verify app content, stored images, and actual audible English separately.
- Export a JSON backup, import it again, and verify no duplicate session appears.
- Test portrait and landscape, long answers, Hint, Skip, and Learning history on the actual phone/tablet.

## Validation performed / not performed

38 existing domain/data tests passed. 31 existing DOM/UI checks passed. 18 image-policy/service-worker unit tests passed using mocked cache/worker APIs. 24 additional touch/mobile/tablet DOM checks passed at 360, 390, 768 and 1024 CSS pixels.

The environment blocks real browser navigation to localhost (`ERR_BLOCKED_BY_ADMINISTRATOR`). That restriction was not bypassed. Therefore native service-worker installation, actual IndexedDB reload/close/reopen, physical-device speech, real provider image downloads, and OS install prompts are NOT verified here. The shell/cache unit tests are not a substitute for this device test. No cloud deployment was performed.

## Maintainer build

In the updated skill directory:

```bash
python scripts/build_pwa.py --output /path/to/pwa
node --test tests/core.test.js
FLYERS_PWA_DIR=/path/to/pwa node --test tests/pwa-unit.test.js
python tests/browser_smoke.py --html preview/Rise_Voca_Flyers.html --screenshots /tmp/flyers-ui
python tests/mobile_layout.py --html preview/Rise_Voca_Flyers.html --screenshots /tmp/flyers-mobile --report /tmp/flyers-mobile.json
python tests/pwa_smoke.py --directory /path/to/pwa --screenshots /tmp/flyers-pwa --report /tmp/flyers-pwa.json
```

The last command requires an environment that permits normal localhost navigation; it did not pass in this restricted environment. On Windows PowerShell set `$env:FLYERS_PWA_DIR` before invoking Node instead of using the POSIX inline environment assignment.

## Technical references

- MDN installability/HTTPS/manifest: https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable
- Apple Add to Home Screen: https://support.apple.com/en-mo/guide/ipad/ipad8f1f7a29/ipados
- MDN voice localService: https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisVoice/localService
- MDN storage quotas and eviction: https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria
