# SimpleEMRSystem current state

These documents describe **actual** current behavior of `master` at `0c39275` (December 2025) and the research-stable tree at `a2c35bf` (July 2024). They supersede `VERSION_2024.2_SUMMARY.md`, `FRONTEND.md`, and `API.md` as a description of what the running code does. Those older files remain in the tree as a record of the 2024.2 rewrite narrative; they do not match the product that exists on `master`.

Current `master` is a broken 2024.2 shell: the original case viewer, URL scheme, and Highcharts client were deleted and replaced with an incomplete skeleton. The behavioral spec for a working research EMR is commit `a2c35bf`. This documentation pass makes no code changes.

Use the files below as the source of truth for architecture, data, deployment, required functionality, and the restore-first refactor sequence. The next code PR should restore the research viewer from `a2c35bf` rather than continuing the 2024.2 UI.

## Documents in this set

- [ARCHITECTURE.md](ARCHITECTURE.md) — project layout, modules, request flow, and how the original UI is assembled
- [DATA.md](DATA.md) — study JSON schemas, loaders, and Django overlay
- [DEPLOYMENT.md](DEPLOYMENT.md) — install paths, fragility, and a modern local/production recipe
- [FUNCTIONALITY.md](FUNCTIONALITY.md) — researcher and participant features that must be preserved, plus acceptance checks
- [REFACTOR_PLAN.md](REFACTOR_PLAN.md) — sequenced PRs: restore viewer first, then tests, loader, settings, and cleanup
