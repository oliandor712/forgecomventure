# Getting Started with Forge

Forge is an open-source Magic: The Gathering rules engine written in Java.
This guide gets you from a fresh clone to a running build.

## Prerequisites

- JDK 17 or later
- Maven
- Git
- Optional: Android SDK (Build-tools 35.0.0, API 35) for `forge-gui-android`

## Build

From the repo root:

```bash
mvn -U -B clean -P windows-linux install
```

Add `-DskipTests` for a faster build. The Maven settings file is picked up
automatically from `.mvn/maven.config` (`.mvn/local-settings.xml`).

## Run (desktop)

The desktop entry point is `forge.view.Main` in `forge-gui-desktop`.

```bash
cd forge-gui-desktop
mvn exec:java -Dexec.mainClass=forge.view.Main
```

Or run `forge.view.Main` from your IDE (IntelliJ is recommended; see the
[IntelliJ setup guide](https://github.com/Card-Forge/forge/wiki/IntelliJ-setup)).
The working directory should be `forge-gui-desktop` so it can find the
`forge-gui/res` resources.

To try a prebuilt copy instead, download the latest release or the daily
snapshot (`forge-gui-desktop` tarball) from
<https://github.com/Card-Forge/forge/releases>.

## Run (mobile UI on desktop)

`forge-gui-mobile-dev` is a libgdx/LWJGL launcher for developing the mobile UI
(`forge-gui-mobile`) on a desktop machine.

## Project layout

| Module | Purpose |
| --- | --- |
| `forge-core` | Core engine, card mechanics, base utilities |
| `forge-game` | Game session, rules, state and flow |
| `forge-ai` | Computer-opponent logic |
| `forge-gui` | Shared GUI code and resources (`forge-gui/res`: card scripts, decks, etc.) |
| `forge-gui-desktop` | Swing desktop front end |
| `forge-gui-mobile` | libgdx mobile front end logic (incl. Adventure mode) |
| `forge-gui-mobile-dev` | Desktop launcher for the mobile UI |
| `forge-gui-android` / `forge-gui-ios` | Platform packaging |
| `adventure-editor` | Editor for Adventure mode content |
| `forge-lda`, `forge-installer` | Tooling and installer |

## Common tasks

- **Add or fix a card:** card scripts live under `forge-gui/res/cardsfolder`.
  See the [Card scripting API](https://github.com/Card-Forge/forge/wiki/Card-scripting-API)
  and `docs/Creating-a-custom-Card.md`.
- **Edition/set data:** `forge-gui/res/editions`.
- **Docs:** the `docs/` folder (user guide, AI, networking, FAQ, Docker setup).
- **Code style:** checkstyle runs during the build (`checkstyle.xml`).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). If an AI agent substantially wrote a
contribution, credit it as a co-author or note it in the pull request body, and
avoid adding unnecessary new tests to the CI suite.

## Help

Join the community on [Discord](https://discord.gg/HcPJNyD66a) and read the
[User Guide](https://github.com/Card-Forge/forge/wiki/User-Guide).
