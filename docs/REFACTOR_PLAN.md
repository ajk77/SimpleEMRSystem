# SimpleEMRSystem Refactor Plan

Goal: a modern, installable Django app that **restores research-stable behavior** (`a2c35bf`) and is easy to run locally and in a small lab production setting. Current `master` is not a valid starting point for "keep the new UI"; it deleted the product. Treat `master` as the Git default and `a2c35bf` as the **behavioral spec plus source of deleted files**.

Do **not** rewrite the application in this documentation pass. The slices below are the suggested PR sequence after that.

## 0. Principles

- Restore before restyle. Pixel-stable 1920×1080 viewer first.
- Files under `resources/` remain the researcher authoring format. DB is a cache/index, not a new schema.
- Pin everything (Python, Django, JS libraries). No "latest from CDN."
- Secrets from the environment. Never rewrite `settings.py` from a wizard.
- Tests that load `demo_study` JSON, not invented fixtures.
- Small PRs that each leave `manage.py runserver` able to show a case.

## 1. What not to change yet

- Highcharts as the chart engine (study comparability).
- JSON shapes of `observations.json` / `medications.json` / `case_details.json` epochs.
- `selected_ids` string format (`rowBUN`, `rowmedidx1`).
- 1920×1080 non-responsive layout and `.taskbox` copy.
- Eye-tracking / EyeBrowserPy.
- Hospital unmanaged models / live Cerner DB connection.
- Participant password accounts (unless a later study asks).
- Postgres, Redis, ASGI, SPA frontend (React/Vue).
- Welcome gradient marketing page, tutorial.js, "responsive" claims.

## 2. Risks

| Risk | Why it matters | Mitigation |
|---|---|---|
| Restoring from `a2c35bf` onto `master` is a large diff | Easy to miss `emr_3.js` / template / URL regex | First PR: restore deleted files as `_legacy` or directly, with a smoke test |
| Dual sources of truth (JSON vs SQLite JSONFields) | Loader bugs already drop data | Phase 1: serve from files. Phase 2: optional cache |
| JSONField list RMW on `cases_completed` | Lost completions in multi-tab labs | Assignment table or `select_for_update` |
| Django 5.0 is EOL | Security | Move to Django 5.2 LTS once tests exist |
| Highcharts license | CDN "latest" may be commercial | Pin a version; document license for lab use |
| Auth added in 2024.2 | Blocks the demo | Make auth optional (`SEMR_REQUIRE_LOGIN=0` default) |
| Synthea pickle + dash-in-ids | Broken notes, broken DOM ids | Fix loader; underscore keys |
| PHI if real charts are loaded | CSRF-exempt + DEBUG | Refuse DEBUG in production; never CSRF-exempt writes |

## 3. Target layout

```
simpleemr/
  pyproject.toml
  README.md
  manage.py
  .env.example
  requirements/
    base.txt          # pinned
    dev.txt
  docker/             # optional, later
  semr_project/       # Django project (rename SEMRproject when convenient)
    settings/{base,local,production,test}.py
    urls.py
    wsgi.py
  semr_interface/     # Django app
    models.py         # keep Study/Case/User/Medication if used; or defer
    views/
    services/         # file I/O only in v1
    management/commands/{load_resources,setup_study}.py
    templates/
    static/           # vendored jquery, bootstrap, highcharts, emr.js
    tests/
  resources/demo_study/
  resources/synthea_study/
  tools/loaddata_synthea.py
```

Renaming packages (`SEMRproject` → `semr_project`) can wait until after the viewer works; it is cosmetic and breaks import paths.

## 4. Sequenced PR slices

### PR 0 — Safety rails (small)

- Add `.env.example`, stop committing `.idea/`.
- `SECRET_KEY` from env with a loud default only when `DEBUG`.
- Fix `wsgi.py` settings module (`SEMRproject.settings`).
- Set `DEFAULT_AUTO_FIELD`, drop `USE_L10N`.
- `LOGIN_URL` if login stays.
- Do not enable new features.

**Done when:** `runserver` still starts; `SECRET_KEY` placeholder cannot be used with `DEBUG=False`.

### PR 1 — Restore the research viewer from `a2c35bf`

Bring back onto `master` (or a `restore-viewer` branch):

- `templates/SEMRinterface/case_viewer.html`
- `study_selection_screen.html`, `user_selection_screen.html`, `case_selection_screen.html`
- `static/js/emr_3.js` (keep the name or rename to `emr.js` in one place)
- `urls.py` path routes for study/user/case/time_step, `selected_items`, `markcomplete`, `markcompleteurl`, `casereset`
- `views.py` functions that load JSON from `resources/` (the `a2c35bf` implementations)
- `utils.get_list_study_id`
- `loaddata_synthea.py` as `tools/`

Keep 2024.2 files (`case_viewer_new.html`, `auth_views.py`) unused, not deleted yet, so diffs stay bisectable.

Wire `SEMRproject/urls.py` so `/SEMRinterface/` is the research app. Root `/` can redirect there.

**Done when:** with **no** `load_resources` and an empty SQLite user table, demo_study is viewable end-to-end (the eight checks in FUNCTIONALITY.md).

This PR is allowed to look "old." That is the point.

### PR 2 — Tests for the restored flow

- `TestCase` using a stripped copy of `demo_study` under `tests/fixtures/resources/`.
- Client tests: select study → user → case → step 0 HTML contains a vital row id and instruction text → POST selected_ids → file or DB contains the line → mark complete.
- Parser tests for `data_layout` / `case_details` missing keys.
- Management command test **after** PR 3.

**Done when:** `python manage.py test` fails if the viewer template drops `dict_observations`.

### PR 3 — Loader that actually loads

Rewrite `load_resources` to **open files directly** (`os.listdir(resources)`), never `get_study_ids()`.

- `--reset` still deletes DB rows then reloads from disk.
- Idempotent upsert of layout/variables when the study exists.
- If `User` remains AbstractUser: set `username=f"{study_id}:{user_id}"`, unusable password, `user_id` **not globally unique** (unique_together with study). This requires a migration; `user_id` unique=True on master is wrong for multi-study.
- Prefer **not** requiring the DB for the viewer in this slice (PR 1 already files-first). Loader becomes optional cache.

**Done when:** empty DB + `load_resources` creates Study rows matching folder names; command is tested.

### PR 4 — Settings split, pinned deps, local DX

- `SEMRproject/settings/{base,local,production,test}.py`
- `pyproject.toml` or `requirements/base.txt` pinned; drop unused `requests`, `Pillow` unless restored loaders need them; add `python-dateutil` only for Synthea tool.
- Vendor jQuery 3.7.x, Bootstrap 3/4 (whatever original template uses — original was Bootstrap 3 glyphicons still in `static/fonts`), Highcharts pinned.
- `manage.py setup_study`: migrate + load + print URL.
- Replace `install.sh`/`install.bat` with thin wrappers or delete in favor of README.
- Delete or quarantine `setup_wizard.py` (it edits settings.py).
- Dockerfile: `python:3.12-slim`, entrypoint migrate+load+gunicorn later; optional in this PR.

**Done when:** README "four commands" works on a clean Linux/Mac/Windows venv; Docker is documented as optional.

### PR 5 — Results and concurrency

- Write `stored_results` as JSONL **and** `StoredResult` rows, same `selected_ids` key.
- `mark_complete` / `reset_case` update user JSON **or** (better) a `CaseAssignment` table: `(study, user_id, case_id, status, completed_at)`.
- Export command: `python manage.py export_results --study demo_study` → JSONL/CSV for analysis.

**Done when:** two overlapping complete requests cannot drop a case id; export matches demo `stored_results.txt` shape.

### PR 6 — Auth as an option, not a gate

- Default: no login (research-stable).
- `SEMR_REQUIRE_LOGIN=1` enables Django auth for shared servers.
- Loader can create a documented demo user `testUser1` / password from env for that mode.
- Gate `/admin/`, `/api/info/`, `/health/` details.
- Remove `@csrf_exempt`. Restore `@ensure_csrf_cookie` on the viewer.
- Object-level: a logged-in user may only open their study (when auth on).

**Done when:** default demo still has zero login; production settings cannot run with DEBUG and placeholder key.

### PR 7 — Synthea tool and data-quality

- Restore `tools/loaddata_synthea.py`; fix note_panel dump; replace pickle with JSON intermediates (or keep pickle behind a flag).
- Underscore keys; document HTML id rule.
- Do not commit `100k_synthea_covid19_csv/`.
- Schema checks: management command `validate_study study_id` that every `cases_all` id in `case_details`, every assigned case exists, every `display_group` is in `data_layout`, every med route is in `med_panel_groups`.

**Done when:** `validate_study demo_study` and `validate_study synthea_study` pass; synthea notes are non-empty after a re-run.

### PR 8 — Cleanup of the 2024.2 shell

Once PR 1–2 are green:

- Remove `case_viewer_new.html`, `unified_selection_new.html` **or** rewrite them to call the same context as the original viewer (only if a study owner wants a wizard picker).
- Remove dead JS (`modules/charts.js` generic wrappers that never receive series).
- Keep `health_check` in slim form.
- Align `SEMRproject/__init__.py` version with README (2024.2 vs 2024.1.b).
- Trim in-repo `docs/` that contradict the code, or point them at the current-state docs in this directory once merged.

### PR 9 — Typing and layout polish (last)

- `mypy` on services/views (gradual).
- `ruff`/`format`.
- Type the JSON with `TypedDict` or pydantic models used by `validate_study` — do not require pydantic at runtime for the viewer if it hurts install simplicity.
- Package data so `pip install semr` can run demo (optional).

## 5. Suggested Django modeling after files-first works

Keep JSON blobs. Do not normalize observations into rows (thousands of points × cases × Highcharts series).

```
Study          study_id, data_layout, variable_details
Participant    FK study, user_id, last_accessed     unique(study, user_id)
Case           FK study, case_id, demographics, observations, notes, case_details
Medication     FK study, medidx, display_name, original_name, med_route
CaseMedication FK case, FK medication, med_data, y_axis_ranges
Assignment     FK participant, FK case, status {assigned, completed}
Selection      FK assignment, time_step, selected_ids JSON, created_at
```

Drop `AUTH_USER_MODEL` override if participants stay non-login. Use contrib User only for staff/admin.

## 6. Production deploy slice (can parallel PR 4)

- `gunicorn semr_project.wsgi:application`
- nginx TLS + `alias` for `/static/`
- `collectstatic`
- systemd unit with `EnvironmentFile=`
- daily copy of `db.sqlite3` and `resources/*/stored_results.txt`
- `DEBUG=False` checklist

Docker Compose: web + optional named volume. No extra services for v1.

## 7. Definition of done for the refactor program

- FUNCTIONALITY.md eight acceptance checks pass on demo_study and one synthea case.
- Fresh clone: Python 3.12 venv, pinned install, `setup_study`, browser at `/SEMRinterface/`.
- `DEBUG=False` deploy recipe works with env secret.
- Tests in CI.
- README matches the code (no Bitnami, no Python 3.8, no fake 25-case claim unless data is added).
- Deleted Synthea loader restored and notes fixed.
- 2024.2 marketing UI gone or clearly optional.

## 8. Effort sketch

| Slice | Relative size |
|---|---|
| PR 0 safety | XS |
| PR 1 restore viewer | L (largest; mostly copy from `a2c35bf`) |
| PR 2 tests | M |
| PR 3 loader | M |
| PR 4 settings/deps/DX | M |
| PR 5 results | S–M |
| PR 6 optional auth | S |
| PR 7 synthea/validate | M |
| PR 8 delete shell | S |
| PR 9 typing | S |

PR 1 unblocks everything. Do not start Docker or AbstractUser migrations before a case chart is visible.

---

## Phase 2 — incremental modernization (after restore)

Phase 1 (sections 0–8 above) restored the research-stable viewer from `a2c35bf`. Phase 2 modernizes incrementally **without** replacing the lab instrument. `docs/CURRENT_STATE.md` is stale: it still says `master` is a broken 2024.2 shell. The research viewer is restored. Live behavior is the restored `a2c35bf` flow plus later PRs; this file's Phase 2 section is the remaining work.

**Hosting note:** single-user local `manage.py runserver` is the intended free host for now. Shared/production hosting remains later Phase 2 / Phase 1 production-slice work.

### Principles

- Incremental PRs; `manage.py runserver` still shows a demo case after each.
- Picker screens (study/user/case) may be modernized and made responsive. They are facilitator UI, not the timed instrument.
- Case viewer: when `SEMR_EYE_TRACKING_MODE` is on, keep pixel-stable 1920×1080, Highcharts, cyan taskbox, row ids (`rowBUN`, `rowmedidx*`), `selected_ids` format, familiar/select copy, `time_step`. When off, a later PR may add a fluid/responsive viewer. Same Highcharts engine either way. Do not replace Highcharts.
- `resources/` JSON remains the authoring format.
- Tests before restyle.

### Sequenced slices (Phase 2)

#### 2.0 Characterization tests

`FUNCTIONALITY.md` checks on a **temp copy** of `demo_study` (never write the committed study). Client tests cover study/user/case pickers, familiar/select viewer HTML, CSRF POST of `selected_ids` → JSONL, mark-complete and reset.

#### 2.0a Lab settings on the home screen (merged)

- Default `SEMR_EYE_TRACKING_MODE` off.
- Study selection screen has a Lab settings panel. Saving writes the session and `semr_runtime.json` (gitignored). `SEMR_EYE_TRACKING_MODE=1` in the environment remains the factory default before any UI save.

#### 2.1 Hygiene (merged, PR 14)

- Relative `{% url %}` links on study/user/case pickers (no more hardcoded `http://127.0.0.1:8000/SEMRinterface/...`).
- Pin jQuery 3.6.4 on pickers (same pin as the viewer).
- 2024.2 shell removed: welcome, login, profile, `unified_selection_new`, `case_viewer_new`, `components/`, `static/js/core/`, `modules/`, `tutorial.js`, unused `custom.css`, `auth_views`, leaky `/api/info/` and `/api/quickstart/`.
- Slim `/health/` and `/api/health/` remain (JSON ok/unhealthy, db ping, resources exists + study count; no study names, DEBUG, SECRET_KEY, disk, memory, or paths).
- Keep Bootstrap 3 + `emr_3.js` + `bs_3.css` on the viewer.
- Viewer still uses jsDelivr `bootstrap.min.js` pin of `a2c35bf` (local stub deleted).

#### 2.2 Dynamic content (merged, PR 17; init hotfix PR 18)

Replace `{% autoescape off %}` JSON dumps in `case_viewer.html` with Django `json_script` + `JSON.parse` in `emr_3.js`. Preserve row ids (`rowBUN`, `rowmedidx*`). CSRF on `selected_items` (already not exempt on research `save_selected_items`). No layout/visual change; time-slider JS is not touched.

PR 15's time-slider patch was reverted (PR 16). The second-drag issue is deferred; do not reintroduce `ordinal:false`, `liveRedraw:false`, `setExtremes` redraw flags, or dropping `reflow`.

#### 2.3 Modern picker screens (merged, PR 19)

Shared `picker_base.html` + `static/css/picker.css` (not `bs_3.css`). Readable system type, max-width ~44rem, study cards, user/case tables, no F11 nag, no jQuery on pickers. Lab settings stay on home with the same field names (`eye_tracking_mode`, `save_settings`). Keep three-step path URLs and `id="select{{ case_id }}"`. Assigned vs completed cases visually distinct. Reset / Mark Complete use vanilla DOM (`getElementById` / `style.display`).

These screens are facilitator UI. The case viewer remains the lab instrument (Highcharts, `selected_ids`, row ids, time slider, `json_script`). Do not collapse pickers to the 2024.2 dropdown wizard (`welcome` / `login` / `unified_selection_new`).

#### 2.4 Viewer JS fetch-at-install (merged, PR 21)

Pinned JS is fetched at install (`install.sh` / `install.bat` run `tools/fetch_frontend.py`) and gitignored (not vendored in git). The case viewer loads local `/static/js` paths. Layout was unchanged in that PR. Highcharts 8.2.2 is still commercial; a license is required for non-eval use.

#### 2.4b Optional fluid layout when eye-tracking off (THIS PR)

When `SEMR_EYE_TRACKING_MODE` is off (the default), the case viewer uses a small overlay stylesheet (`viewer_fluid.css`) so panels can flex on narrower windows. Body gets `eye-tracking-off` / `eye-tracking-on` from the existing `eye_tracking_mode` context. When Lab settings turns eye-tracking on, keep the locked ~1920px instrument (min-width + overflow-x). Same Highcharts, `selected_ids` / row ids, `json_script`, and time-slider JS. Do **not** fix the time-slider second-drag bug here. Resize reflows `chartsContainers` only in fluid mode.

Next is **2.5**.

#### 2.5 Backend leftovers from original plan

Env secrets, `load_resources` walking `resources/`, `CaseAssignment` so two tabs cannot clobber `cases_completed`, restore `tools/loaddata_synthea.py`.
