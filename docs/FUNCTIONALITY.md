# SimpleEMRSystem Functionality (must preserve)

Two layers:

1. **Current `master` behavior** — what the running code actually does (mostly a broken shell).
2. **Research-stable behavior** (`a2c35bf`, July 2024) — what laboratory studies and the JAMIA Open 2021 paper require. **This is the preservation target.**

README, `docs/FRONTEND.md`, and `docs/VERSION_2024.2_SUMMARY.md` describe a product that is not implemented. Do not preserve 2024.2 welcome/tutorial/auth if they conflict with running a study.

## 1. Product purpose

Simple EMR is **not a clinical EMR**. It is a lab instrument:

- A researcher authors a *study* (JSON layout + synthetic or de-identified cases).
- A *participant* (clinician, student) is assigned cases.
- The participant reviews a **fixed 1920×1080** chart-like patient view, optionally over two time epochs (`familiar` then `select`).
- The system records which rows they clicked (`selected_ids`) for analysis (information-seeking, highlighting, ML CDS papers).
- Eye-tracking hooks existed historically (EyeBrowserPy) and are **off**. Do not re-enable in the first refactor.

Citation to keep in README: King et al., JAMIA Open 2021;4(3):ooab040.

## 2. Researcher-facing features (preserve)

### 2.1 Study-as-files

A researcher must be able to:

- Copy `resources/demo_study` to `resources/my_study`.
- Edit `data_layout.json`, `variable_details.json`, `med_details.json`, `user_details.json`, `case_details.json`.
- Drop case folders under `cases_all/<id>/` with the four JSON files.
- Restart (or reload) and see the new study in the study list. Originally, studies were discovered if the folder name contains `_study`. Preserve that convention **or** document the new rule and keep both demo names working.

No Django admin is required for study authoring. Admin was commented out in the stable tree; 2024.2 enabled it without `ModelAdmin` classes.

### 2.2 Sample studies

| Study | Must keep |
|---|---|
| `demo_study` | 3 synthetic Cerner-scrambled cases `10000101–103`, two epochs each, users `testUser1`/`testUser2`. |
| `synthea_study` | Assigned ICU cases in `case_details.json` / `user_details.json`. Extra unassigned UUID folders can stay as extras. |

README's "25 Synthea cases" is aspirational; committed data is 9 folders / 3 assigned.

### 2.3 Synthea (and custom) ingest

Preserve the **ability** to:

1. Drop Synthea CSVs under `resources/` (path currently `100k_synthea_covid19_csv/`, gitignored).
2. Run `loaddata_synthea.py` (restore this file from `a2c35bf`).
3. Inspect `list_case_dicts.json`.
4. Hand-pick cases into `case_details.json` and assign them in `user_details.json`.
5. Tweak groups/names/ranges in `variable_details.json` / `med_details.json` / `data_layout.json`.

Fix the note-panel write bug (`save_json_dumps(result, …)` → dump `note_panel_data`). Convert dashes in keys to underscores.

Custom ingest: a researcher writes another preprocessor that emits the same JSON; they should not need Django models of hospital tables. Keep unmanaged `a_*` models only as optional documentation of the original Cerner mapping, not as runtime.

### 2.4 Assignment and results

- Edit `user_details.json` to assign cases.
- After a session, read:
  - `cases_completed` on the user record
  - `stored_results.txt` JSONL with `user_id`, `case_id`, `selected_ids`
- Reset a completed case so it can be re-run (`casereset`).
- Completing a case must not destroy other users' assignment data (today's rewrite of the whole JSON file is racy; preserve the *feature*, not the race).

### 2.5 Display customization without code changes

Changing `data_layout.json` groups, `variable_details.display_group` / `display_name` / `units` / `dflt_normal_ranges`, and `med_details.med_route` / `display_name` must change the viewer. That is the "readily customizable" claim in the paper.

### 2.6 Lab operations

- Fullscreen on a **1920×1080** monitor. Non-responsive is a **feature** (eye-tracking and highlighting studies need a stable pixel layout). Do not "improve" this into a fluid Bootstrap grid in the first rewrite.
- Offline-capable static assets for air-gapped labs.
- One-command local start.
- Optional: a way to hide the study/user pickers and deep-link `/<study>/<user>/<case>/` for scripted sessions.

### 2.7 Eye-tracking (do not restore yet)

README: components are turned off; see EyeBrowserPy. `custom.css` still has a `vertical_curser.JPG` font asset. Preserve hooks as no-ops / comments. Do not spend refactor budget here.

## 3. Participant-facing features (preserve)

This is the original path-based flow. 2024.2 login/welcome is **not** required to preserve study validity.

### 3.1 Selection screens

1. **Study list** — every `*_study` folder.
2. **User list** — keys of `user_details.json` for that study.
3. **Case list** — `cases_assigned` vs `cases_completed`. Assigned cases are clickable; completed cases are visible but not (or reset-to-replay). Original `case_selection_screen.html` implemented this; 2024.2 unified dropdown is acceptable **if** it still shows both lists and links to the viewer with study/user/case identity.

No password. Participant identity is the `user_id` string chosen by the researcher (e.g. `testUser1`). If auth is added later, it must not block this lab workflow.

### 3.2 Case viewer (the actual EMR)

Must restore the four-region layout from `screenshots/` and `custom.css`:

| Region | Content | Interaction |
|---|---|---|
| **Title / demographics bar** | Fields listed in `data_layout.title_bar` from `demographics.json`. | Display only. |
| **Temporal header** | `date_line`: admit date, current date, ICU day from epoch `min_t`/`max_t`. | Display only. |
| **Physiological column** | Groups in `physio_panel_groups`; each matching observation is a Highcharts row (vitals, ventilator, I/O). | Click row to toggle selection when `check_boxes=1`. Highlight class. |
| **Medications column** | Groups in `med_panel_groups` (routes). Highcharts dose/time; tooltip can show `med_reason_tooltips`. | Same click-to-select (`rowmedidx*` / RxNorm ids). |
| **Labs column** | Groups in `lab_panel_groups`. Numeric series with normal-range color zones; discrete/nominal series as squares. | Same click-to-select (`rowBUN`, etc.). |
| **Notes column** | Tabs or stacked groups from `note_panel_groups`. Each note: `date`, `type`, `text`. Filter/hide notes with `js_time > max_t` if the original JS did so. | Typically not in `selected_ids` unless a row id exists. |
| **Instruction / task region** | Cyan `.taskbox`. Copy from `instruction_set` (`familiar` vs `select`). **Continue** button. | Continue saves selections (if any) and advances epoch or completes. |

Visual constraints from CSS (preserve unless a study owner asks otherwise):

- `body` padding-top 50px for the navbar
- `.labbox` / `.medbox` / `.vitmedbox` ≈ 88vh scroll
- `.taskbox` height 25vh, background `rgba(81, 245, 235, 0.8)`
- `.chartrow` ~22% float; vital/med rows ~90%
- Highlight: `.highlight` / grey row background `#dfdfdf`

Highcharts: shared x-axis window `[min_t, max_t]`; optional vertical plot line ("now"); loading overlay `#loading_new_patient` while charts initialize.

### 3.3 Temporal epochs

Demo cases have two steps:

1. `check_boxes: 0`, `instruction_set: "familiar"` — shorter `max_t`. Participant reads. Continue does not need to POST selections.
2. `check_boxes: 1`, `instruction_set: "select"` — later `max_t`. Participant clicks rows used in their case presentation. Continue POSTs `selected_ids` then `markcompleteurl`.

URL originally: `/SEMRinterface/<study>/<user>/<case>/` and `/.../<case>/<time_step>/`. Preserve time_step semantics even if the path is redesigned.

### 3.4 Continue / complete / reset

- Continue on non-final epoch → next time_step (same case).
- Continue on final epoch → append `case_id` to `cases_completed`, return to case list.
- Reset → remove from `cases_completed` so the case is assigned again.
- Save selections even if the list is empty? Original JS saved only when `selectedItems.size > 0`. Preserve that.

### 3.5 What participants must **not** see

- Django admin, health JSON, system paths, other studies' data, raw JSON files.
- "Version 2024.1" footer / GitHub link during a timed study (optional hide). Original screens were sparse on purpose.

## 4. Instruction copy (preserve verbatim unless studies override)

From original `views.case_viewer`:

- `familiar`: "Please use the available information to become familiar with this patient."
- `select`: "Please select the information you used when preparing to present this case."

A later enhancement can move this into `case_details.json`; default must stay.

## 5. Current master vs preservation target

| Feature | Research-stable | Current master |
|---|---|---|
| Study/user/case pickers | Three screens, path URLs | Unified dropdown + login |
| Auth | None | Login required; resource users cannot log in |
| Case viewer | Server-rendered Highcharts EMR | Empty Bootstrap panels; wrong JSON keys |
| Time steps | URL `time_step` | Hardcoded `0`; next URL 404s |
| Checkboxes / highlight | `check_boxes` + `emr_3.js` | CSS class exists; no rows |
| Save `selected_ids` | POST `selected_items` view → txt | Client calls missing URL |
| Mark complete / reset | GET views rewrite JSON | Service functions exist, no routes |
| 1920×1080 layout | `custom.css` + original template | "Responsive" welcome; viewer unused CSS |
| Synthea loader | `loaddata_synthea.py` | File deleted |
| Eye-tracking | Off | Still off |
| Welcome / tutorial | N/A | New; optional, not study-critical |
| Health endpoints | N/A | Present; leaky |
| Django User / admin | Unused unmanaged hospital models | Custom AbstractUser + admin enabled |

**Preserve column 2's files (JSON, CSS, template tags, screenshots, sample studies). Restore column 2's behavior from `a2c35bf`. Treat column 3 extras as optional later slices.**

## 6. Out of scope for "must preserve"

- Mobile / responsive redesign (contradicts lab protocol).
- Real-time collaboration, ML dashboard, i18n, PWA (VERSION_2024.2_SUMMARY roadmap).
- Replacing Highcharts in v1 (would change pixel-level highlighting studies).
- Password-based participant accounts (unless a study explicitly needs them).
- Postgres, Redis, celery.

## 7. Acceptance checks for a refactor

A build preserves behavior if a researcher can:

1. `migrate` + load `demo_study` from `resources/` (not empty DB).
2. Open study `demo_study`, user `testUser1`, case `10000101` without a password (or with a documented demo login that is created by the loader).
3. See demographics, vitals, meds, labs, notes, cyan instruction box, ICU day line.
4. Continue from familiar → select epoch; charts' x-max extends.
5. Click several lab/med rows, see highlight, Continue; a new line appears in `stored_results.txt` (or equivalent export) with `selected_ids` like `rowBUN`.
6. Land on the case list with `10000101` completed; reset brings it back.
7. Repeat for a synthea UUID case assigned to `demo2`.
8. Change `data_layout.json` lab group order, reload, see the new order.

Until those eight pass, do not ship welcome-page, Docker, or auth work as the "refactor."
