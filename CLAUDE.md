# BuildNotify

A system tray app (Python 3, PyQt5 today, PySide6 after Phase 4) that polls cctray.xml CI feeds
and shows build status and notifications. Library code lives in `buildnotifylib/`, and tests
live in `test/`.

The work is tracked in Backlog.md (`backlog/`, local only and gitignored). The full review behind the plan is
`docs/modernization-review.html`. It is local only and gitignored, so don't commit it.

## Commands

```sh
uv sync --locked                                    # app + dev group from uv.lock
QT_QPA_PLATFORM=offscreen uv run --locked pytest -q # full suite
uv build                                            # sdist + wheel into dist/
```

Once TASK-19 adds the justfile, use `just test`, `just lint`, `just types` and `just build`.
Always run Qt tests with `QT_QPA_PLATFORM=offscreen`.

## Backlog workflow

1. Find the next task with `backlog task list -s "To Do" --plain`. Take the lowest task number
   whose milestone is the earliest unfinished one.
2. Read the task with `backlog task <id> --plain`. Set it to In Progress with
   `backlog task edit <id> -s "In Progress"`.
3. Implement it, and tick each AC with `--check-ac <n>` as it is met.
4. Close the task with `backlog task edit <id> -s Done --final-summary "<2-4 lines>"`.
   `backlog/` is gitignored and local only, so never `git add` or commit anything under it.
5. If you can't finish a task, add a note with `--append-notes` saying what is blocked and why.
   Leave the task In Progress and move on only if the next task doesn't depend on it.
   Things that need the user go in `backlog/docs/user-actions.md`.

## Rules

1. **Small commits on `main`.** Use short imperative subjects that match the history
   ("Fix ...", "Add ...", "Remove ..."). One behaviour per commit. Tests go in the same commit
   as the fix. Every commit must leave the suite green.
2. **Never push, tag, publish, or write to GitHub.** That includes PRs, issues, comments and
   workflow enable/disable. Record these steps in `backlog/docs/user-actions.md` instead.
3. **Tests must be hermetic.** They never touch the real keychain or the user's QSettings
   (`test/conftest.py` handles this once TASK-2 is done). Until TASK-2 is done, deselect
   `test/integration/config_test.py`.
4. **Fix bugs test first.** Write a failing regression test, then the fix. Bug IDs (H1, M3,
   L7, ...) refer to the report. Put them in the commit body.
5. **Don't widen scope.** If you spot a new bug, create a backlog task for it. Don't fix it
   inside an unrelated commit.
6. **Leave these alone:** `docs/rust-gpui-rewrite-analysis.md` (untracked, the user's draft)
   and the HTML report.
7. Match the surrounding style. Keep comments sparse, and keep functions small (flake8 had
   `max-complexity=5`, so keep that spirit).

## Decisions (defaults chosen; the user can override)

1. Stay on Python. A Rust rewrite stays possible after Phase 3.
2. `requires-python >= 3.11`. CI matrix 3.11-3.14.
3. Build with hatchling, manage environments and the lockfile with uv. ruff for lint and
   format, mypy for types.
4. Qt binding: PySide6. The UI modules are generated with `pyside6-uic` through `just ui` and
   committed. CI checks that they are up to date. Icons are package data loaded with
   `importlib.resources`.
5. Custom script: provide the `BUILDNOTIFY_STATUS` and `BUILDNOTIFY_PROJECTS` env vars. The
   legacy `#status#`/`#projects#` substitution stays, but with `shlex.quote`.
6. Distribution: PyPI (trusted publishing) and Flathub. Retire the snap, PPA, OBS, stdeb and
   the Vagrantfile.
7. Keep the package name `buildnotifylib`. The target layout is:
   - `core/`: pure Python; no Qt, requests or keyring.
   - `adapters/`: http, credentials, settings_store, hooks.
   - `ui/`: poller, tray, menu, icons, dialogs.
   - `__main__.py`: the composition root.
