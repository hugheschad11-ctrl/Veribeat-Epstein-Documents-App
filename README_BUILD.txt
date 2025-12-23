Epstein JPT — No-Terminal Builds (Web-Click)

Goal
- End users: double-click EXE (Windows) or install APK (Android). No terminal.
- You (builder): click-build via GitHub Actions in the browser. No local toolchains required.

How to build (no terminal on your machine)
1) Create a GitHub repo (private or public).
2) Upload EVERYTHING from this zip to the repo (drag-drop in GitHub web UI).
3) In GitHub: Actions tab
   - Run workflow: "Build Desktop (Windows EXE)"
   - Run workflow: "Build Android (Debug APK for Sideload)"
4) When each finishes: Actions -> latest run -> Artifacts
   - Download EpsteinJPT_Windows (contains Epstein JPT.exe + docs folder + README)
   - Download EpsteinJPT_Android_DebugAPK (contains APK + README)

Then distribute those artifacts to users.

Docs
- The EXE does NOT include PDFs (keeps download small). Users place PDFs in the docs/ folder next to the EXE.
- Same for Android: user points the app at a docs folder on the phone.

Compliance
- No redaction bypass. The app indexes and searches only visible text.

