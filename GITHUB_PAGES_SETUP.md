# Rise Voca Flyers - GitHub Pages setup

## Status and scope

This is the existing PWA preview prepared for GitHub Pages. It has not been published. No quiz logic, vocabulary, image approvals, or learning-history schema has been changed. The GitHub connection identified the account LongDangK; the repository name below is a proposal, not an existing deployment.

Suggested repository: `LongDangK/rise-voca-flyers`
Expected project-site URL after a successful deployment, without a custom domain:
`https://longdangk.github.io/rise-voca-flyers/`

## Before publication

A public repository and a normal GitHub Pages website are publicly accessible. Private repository visibility by itself does not make a Pages website private. Confirm permission to publish the supplied vocabulary and translations: they are embedded in index.html, even though the original PDF is not bundled. Preserve THIRD_PARTY.md and the in-app image credits.

Do not upload the skill archive, original PDF, illustration-review export, learner-history JSON backups, CSV reports, credentials, or personal files. This ZIP contains application files and documentation only. The included .gitignore is a convenience for Git users, not a privacy barrier and not protection against manual browser uploads.

## 1. Create a dedicated repository

On GitHub, select + > New repository.

- Owner: LongDangK (or the intended personal account).
- Repository name: rise-voca-flyers.
- Description: Topic-based English vocabulary PWA with local learning history.
- Visibility: Public for the GitHub Free route. GitHub Pro and other eligible plans support Pages from private repositories, but the normal Pages website is still public.
- Add README: On, to initialize a branch. Use main as the branch for this guide; select the actual initialized branch if it has another name.
- Create repository.

Do not reuse an unrelated project repository or change an existing repository's visibility just for this app.

## 2. Upload the extracted application, not the ZIP

Extract Rise_Voca_Flyers_GitHub_Pages.zip on the computer. In the repository, select Add file > Upload files. Drag the CONTENTS of the extracted folder, including the icons folder, onto the upload area. Confirm that index.html is at the repository root, not in an extra nested folder.

Commit the upload to main with the message: Publish Rise Voca Flyers PWA preview.

Required files include:

```text
.nojekyll
index.html
Rise_Voca_Flyers.html
manifest.webmanifest
sw.js
pwa-5a5460da10.js
icons/
  apple-touch-icon.png
  icon-192.png
  icon-512.png
THIRD_PARTY.md
```

Keep the additional documentation/build-information files and the older hashed pwa script included in this release. Verify that .nojekyll was uploaded. This marker disables the default Jekyll processing for the already-built static files. The provider-specific _headers file from the generic PWA ZIP is omitted; it is not a GitHub Pages configuration.

## 3. Enable Pages

Open Settings > Pages > Build and deployment.

- Source: Deploy from a branch.
- Branch: main (or the actual initialized branch).
- Folder: /(root).
- Save.
- Leave Custom domain empty for the first deployment.
- Enable Enforce HTTPS when available; a github.io site is served over HTTPS automatically.

This route does not require authoring a custom Actions workflow. GitHub still uses a managed Actions run to deploy it. Inspect the Actions tab for the Pages deployment result. Return to Settings > Pages and use Visit site. Publishing can take up to 10 minutes after a push; wait for the deployment result before troubleshooting a transient 404.

## 4. First-run checks

Open the published HTTPS URL in a normal browser. Do not use an Incognito/private window for regular learning. Confirm that the learning screen loads and that the PWA status eventually says App and vocabulary ready offline.

Start a two-word session, enter some letters, select Save & pause, reopen the SAME browser/app context, and Resume. Check the selected words, letter state, and history. A successful page deployment is not a substitute for this test.

In Library & source, use Save pictures for offline. Confirm the successful file count before relying on offline pictures. Pictures are NOT bundled in this release. English speech still depends on the device/browser voices and needs its own offline test.

## 5. Install on a mobile device

Android: open the HTTPS site in a compatible browser and use Install app or Add to Home screen.
iPhone/iPad: open the site in Safari, use Share > Add to Home Screen, enable Open as Web App when offered, and select Add. Wording may vary with the OS/browser.

Launch from the new icon, then repeat the pause/resume test in that installed app. Save images there as needed. Test airplane mode separately for application files, saved illustrations, and audible English. Browser and installed-app storage should not be assumed identical on every platform.

## 6. Move existing learning history

In the previous app, choose Learning history > Back up all history (JSON).
Transfer the JSON privately to the target device, open the installed PWA, and use Restore / merge backup.
Never upload the backup to the public repository.

This version stores history locally; Pages is not a history-sync service. A phone and tablet do not automatically share progress. Keep backups outside the browser and keep the hosting address stable. A different browser, app container, account domain, or custom domain can expose a different storage area.

## 7. Updates and troubleshooting

For future updates, back up history and replace the complete application release. Preserve the repository URL, source folder, relative paths, and image credits. Keep old hashed pwa scripts during a transition. When the app reports an update, Save & pause, close all app windows and site tabs, and reopen. Do not clear site data as a first troubleshooting step: it can remove history.

- No main branch in the Pages selector: initialize/commit the repository first, then refresh Settings > Pages.
- 404 after the Pages run finishes: check the publishing branch, /(root), and root-level index.html. Use the URL shown in Settings > Pages rather than a repository blob URL.
- Screen loads but offline setup fails: check that manifest.webmanifest, sw.js, the active pwa script, and icons exist at the exact relative paths. Inspect the deployment result and browser errors.
- App still shows an old version: close all windows for this site, reopen online, and follow the update message. Do not delete learner data.
- Pages unavailable for a private repository: check the account plan and organization policy; do not automatically make an existing private project public.

## Validation of this preparation

All seven offline-shell paths exist in the archive. The manifest start_url/scope and service-worker registration use relative paths compatible with a project subdirectory. The application's HTML, manifest, service worker, active script, and icons are byte-for-byte unchanged from the supplied PWA ZIP. .nojekyll, .gitignore, and this guide were added; the optional provider-specific _headers file was omitted.

This is a static packaging check, not a live GitHub deployment, real service-worker installation, or physical-device acceptance test. The original PWA remains a preview. See README.md for its existing test boundaries.

## Official references

- GitHub Pages overview: https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages
- Creating a Pages site, visibility, entry file and .nojekyll: https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site
- Publishing source: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- HTTPS: https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https

Prepared 2026-10-04. GitHub UI and platform availability can change; follow the current repository settings and official documentation.
