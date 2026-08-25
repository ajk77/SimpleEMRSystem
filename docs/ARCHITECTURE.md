# SimpleEMRSystem Architecture

Analyzed from public GitHub repo `ajk77/SimpleEMRSystem`, default branch `master` at commit `0c39275` (2025-12-08). Compared against the last research-stable tree `a2c35bf` (2024-07-10, "Upgrade to Django 5").

**Important:** current `master` is not a working research EMR. The September 2025 "2024.2" rewrite deleted the original case viewer, URL scheme, and Highcharts JS, then replaced them with an incomplete skeleton. A refactor must restore research-stable behavior from `a2c35bf` while keeping useful 2024.2 pieces (SQLite models, `load_resources`, health checks) only after they actually serve that UI.

## 1. Project layout (current master)

```
SimpleEMRSystem/
├── manage.py                 # DJANGO_SETTINGS_MODULE=SEMRproject.settings
├── requirements.txt          # Django==5.0.7, dateutil, requests, Pillow
├── setup.py                  # setuptools wrapper; version from SEMRproject.__init__
├── setup_wizard.py           # Interactive installer; mutates settings.py in place
├── install.sh / install.bat  # venv + migrate + load_resources + runserver
├── Dockerfile                # python:3.6.8 (incompatible with Django 5)
├── docker-compose.yml        # runserver 0.0.0.0:8000, no migrate/load
├── SEMRproject/              # Django project package
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py               # still points at LEMRProject.settings (dead)
│   └── __init__.py           # version 2024.1.b (not 2024.2)
├── SEMRinterface/            # Sole Django app
│   ├── models.py             # Study, User(AbstractUser), Case, Medication, ...
│   ├── views.py              # welcome, unified_selection, case_viewer, get_case_data
│   ├── auth_views.py         # login/logout/profile/change_password
│   ├── services.py           # DB-first I/O with filesystem fallback
│   ├── urls.py
│   ├── health_check.py
│   ├── management/commands/load_resources.py
│   ├── migrations/0001_initial.py
│   ├── templatetags/custom_tags.py   # leftover from original viewer
│   ├── templates/SEMRinterface/
│   ├── static/{css,js,fonts}
│   ├── tests/{test_models,test_services}.py
│   └── fixtures/test_data.json
├── resources/{demo_study,synthea_study}/
├── docs/                     # 2024.2 narrative docs (often inaccurate vs code)
└── screenshots/              # Original 1920x1080 research UI
```

**Missing from master (present at `a2c35bf`):**

- `SEMRinterface/loaddata_synthea.py` (44 KB Synthea CSV preprocessor)
- `SEMRinterface/loaddata.py` (Cerner/hospital preprocessor)
- `SEMRinterface/utils.py` (`get_list_study_id`)
- `SEMRinterface/templates/SEMRinterface/case_viewer.html` and the three selection screens
- `SEMRinterface/static/js/emr_3.js` (the actual Highcharts EMR client)
- Original models mapping hospital tables (`a_ClinicalEvents`, `a_Medication`, …)

Django apps: **one** (`SEMRinterface`) plus contrib (`auth`, `admin`, `sessions`, `staticfiles`, `sites`, `messages`, `admindocs`). No `asgi.py`. No `LOGIN_URL` / `LOGIN_REDIRECT_URL`.

## 2. Modules and responsibilities

### 2.1 Django project (`SEMRproject`)

| File | Role | Notes |
|---|---|---|
| `settings.py` | SQLite, `AUTH_USER_MODEL=SEMRinterface.User`, `DEBUG=True`, placeholder `SECRET_KEY` | Duplicate `BASE_DIR`. `STATIC_ROOT=''`. `TEMPLATES['DIRS']` points at a non-existent project-level `templates/`. `USE_L10N` still set (removed in Django 5). Comments still cite Django 1.4. |
| `urls.py` | Mounts the app **twice**: `""` and `"SEMRinterface/"` | Dual mount is how README's `/SEMRinterface/` still "works", but JS hardcodes mixed prefixes. |
| `wsgi.py` | WSGI entry | `DJANGO_SETTINGS_MODULE = "LEMRProject.settings"` — production WSGI is broken. `runserver` uses `manage.py` so local dev still starts. |

### 2.2 App (`SEMRinterface`)

**Models** (`models.py`): JSON-blob store, not a normalized EMR schema.

- `Study(study_id unique, data_layout JSON, variable_details JSON)`
- `User(AbstractUser)` with `USERNAME_FIELD='user_id'`, `study` FK, `cases_assigned`/`cases_completed` JSON lists. `user_id` is **globally unique**, despite comments about per-study uniqueness. `username` is also unique with default `''`.
- `Case(study, case_id)` unique together; blobs: `demographics`, `observations`, `note_panel_data`, `case_details`.
- `Medication(study, medidx)` catalog from `med_details.json`.
- `CaseMedication(case, medication, med_data, y_axis_ranges)`.
- `StoredResult(study, user_id, case_id, selected_items)` — append-only, no unique constraint (matches original `stored_results.txt` lines).
- `CaseSelection(study, user_id, case_id)` unique together — unused by views.

**Services** (`services.py`): intended as a framework-free I/O layer. In practice it imports Django models inside a try/except and **prefers the DB whenever Django is importable**. That makes `load_resources` (which calls `get_study_ids` / `get_user_details`) read an empty DB instead of `resources/` on first load.

Functions: `load_json`/`save_json`, `get_study_ids`, `get_user_details`, `get_case_assignments`, `update_case_assignments`, `load_case_details`, `save_case_selection`, `mark_case_complete`, `reset_case`, `save_selected_items`, `get_case_files`.

**Views** (`views.py`):

- `welcome_view` — login gate, then `welcome.html`.
- `unified_selection_view` — GET renders study dropdown; POST `type=fetch_users|fetch_cases` returns JSON. **The function is defined twice.** The second definition overwrites the first and **drops the study-access 403 check**.
- `get_case_data` — `@csrf_exempt` JSON of `get_case_files()`.
- `case_viewer` — `@csrf_exempt`, requires `study_id`/`user_id`/`case_id` query params, renders `case_viewer_new.html`. Does **not** pass `data_layout`, `variable_details`, observations, medications, notes, instructions, or `show_checkboxes`.

**Auth** (`auth_views.py`): study+user_id+password login. `load_resources` never sets passwords, so resource users cannot authenticate. `study_selection_view` renders a template that does not exist (`study_selection.html`). Login template JS focuses `#username` but the input is `user_id`.

**Management command** `load_resources`: `--reset` deletes all `Study` rows (cascade). Then calls `get_study_ids(RESOURCES_DIR)` which, with Django available, **queries the now-empty DB**. Chicken-and-egg: first install loads zero studies unless the filesystem fallback is forced.

**Health** (`health_check.py`): `/health/`, `/api/health/`, `/api/info/`, `/api/quickstart/`. Unauthenticated. `system_info` uses `sys` and `settings.DJANGO_VERSION` without importing `sys`; `psutil` is optional and not in `requirements.txt`. Health is not `@staff_member_required`, so it leaks host paths, studies, and DEBUG.

**Template tags** (`custom_tags.py`): `date_line`, `get_labnames`, `get_meds`, `full_gender`, `short_id`, `keyvalue`, etc. These exist only to support the **deleted** `case_viewer.html`. Current templates barely use them.

### 2.3 Frontend (current master)

Loaded from `base.html`: jQuery 3.7.1 and Highcharts from CDNs, plus:

- `static/js/core/utils.js` — cookies, DOM show/hide, validation, error log
- `static/js/core/api.js` — `SEMRApiClient`
- `static/js/modules/emr-core.js`, `charts.js`, `tasks.js`
- `static/js/tutorial.js`

`custom.css` still encodes the original 1920×1080 layout (`.labbox` 88vh, `.taskbox` cyan 25vh, `.chartrow` 22% float) but `case_viewer_new.html` does not use those classes.

**API client mismatches (code-backed):**

| Client method | URL it hits | Server route that exists |
|---|---|---|
| `getCaseData` | `/api/get_case_data/?…` | exists at both `/api/…` and `/SEMRinterface/api/…` because of dual mount |
| `getUsers` / `getCases` | POST to `''` (current page) | only works if the page is `/select/` |
| `saveSelectedItems` | `/SEMRinterface/selected_items/{study}/{user}/{case}/` | **no such URL on master** |
| `markCaseComplete` | `/SEMRinterface/markcompleteurl/{study}/{user}/{case}/` | **no such URL on master** |

`emr-core.js` still navigates to those missing mark-complete / next-step URLs.

`case_viewer_new.html` expects `caseData.physio_data`, `med_data`, `lab_data`, `instructions`. `get_case_files` returns `demographics`, `medications`, `notes`, `observations`. The viewer therefore renders empty panels even when the API succeeds.

## 3. Request / data flow

### 3.1 Current master (as implemented)

```
Browser
  GET / or /SEMRinterface/
    -> welcome_view
         unauthenticated -> redirect login
         authenticated   -> welcome.html
  GET /login/  -> study dropdown + user_id + password
                  authenticate(username=user_id)
                  require user.study.study_id == posted study
  GET /select/ -> unified_selection_new.html (studies from Study.objects)
  POST /select/ type=fetch_users  -> User rows for that study
  POST /select/ type=fetch_cases  -> cases_assigned / cases_completed JSON lists
  GET /case_viewer/?study_id=&user_id=&case_id=
    -> load_case_details (Case.case_details JSON)
    -> case_viewer_new.html
    -> JS GET /api/get_case_data/
         -> get_case_files (Case + CaseMedication)
         -> populatePanels looks for keys that are not in the payload
  Continue button
    -> emrCore.advanceToNextStep()
    -> POST /SEMRinterface/selected_items/...  (404)
    -> navigate /SEMRinterface/.../time_step+1/ or markcompleteurl (404)
```

No view writes `StoredResult` or updates `cases_completed` on master because the endpoints were never wired.

### 3.2 Research-stable flow (`a2c35bf` — this is the behavior to preserve)

No authentication. Studies discovered by walking `resources/` for directories whose names contain `_study`. All state is JSON files.

```
GET  /SEMRinterface/                                      select_study
GET  /SEMRinterface/{study_id}/                           select_user
GET  /SEMRinterface/{study_id}/{user_id}/                 select_case
GET  /SEMRinterface/{study_id}/{user_id}/{case_id}/       case_viewer time_step=0
GET  /SEMRinterface/{study_id}/{user_id}/{case_id}/{n}/   case_viewer time_step=n
GET  /SEMRinterface/casereset/?study_id&user_id&case_id   remove from cases_completed
GET  /SEMRinterface/markcomplete/?…                       append cases_completed
GET  /SEMRinterface/markcompleteurl/{s}/{u}/{c}/          append + redirect to case list
POST /SEMRinterface/selected_items/{s}/{u}/{c}/           append line to stored_results.txt
```

`case_viewer` server-renders **all** of:

- `dict_data_layout`, `dict_variable_2_details`, `dict_med_2_details`
- `dict_demographics`, `dict_observations`, `dict_medications`, `dict_notes`
- `dict_case_details[case_id]` (list of epochs)
- `show_checkboxes`, `instructions` for the current `time_step`
- `min_t` / `max_t` used by `date_line` and Highcharts x-axis extremes

`emr_3.js` (deleted on master) then draws Highcharts series from the JSON already in the page, toggles row highlight/`selected_ids`, and POSTs them before navigating to the next epoch or `markcompleteurl`.

## 4. How the UI is assembled (research-stable)

This is the layout in `screenshots/` and `custom.css`, driven by `data_layout.json`.

```
┌───────────────────────────────────────────────────────────────────────────┐
│ Navbar / title_bar: id, age, sex, height, weight, bmi, race  (demo)     │
│               or id, name, age, sex, race, ethnicity          (synthea) │
│ ICU timeline: "Admitted … | Current date … | Current ICU day …"          │
├───────────────┼─────────────────────────┼───────────────────────────────┤
│ Physiological │ Medications             │ Clinical notes (tabs)          │
│ (vitals, vent)│ grouped by med_route    │ Progress_Note, HandP, RAD, …   │
│ Highcharts    │ Highcharts dose/time    │ date + free text               │
│ rows          │                         │                                │
├───────────────┴─────────────────────────┤ Task / instruction region      │
│ Laboratory results grouped by           │ familiar | select              │
│ lab_panel_groups (CBC, chem, …)         │ Continue -> next time_step     │
│ sparkline / chart rows, click-to-select │ or mark complete               │
└────────────────────────────────────────┴───────────────────────────────┘
```

Assembly algorithm (original `case_viewer.html` + `custom_tags` + `emr_3.js`):

1. For each name in `data_layout.physio_panel_groups` / `lab_panel_groups`, find observation keys whose `variable_details[key].display_group` matches.
2. For each name in `data_layout.med_panel_groups`, find medications whose `med_details[medidx].med_route` matches.
3. For each name in `data_layout.note_panel_groups`, render `note_panel_data[group]` as dated notes.
4. Each observation/med row is a Highcharts instance with `numeric_lab_data` / `discrete_lab_data` / `med_data` series. X is JS epoch ms. `y_axis_ranges` and `dflt_normal_ranges` color-zone the series (blue low / green normal / red high).
5. `case_details[case_id][time_step].min_t/max_t` clip the visible window. Continue increments `time_step`.
6. If `check_boxes==1`, rows are selectable (`row{VAR}` / `rowmedidxN` ids). Selected ids are appended to `stored_results.txt`.

HTML ids cannot contain dashes (commit `4099786`): Synthea LOINC keys must use underscores (`8310-5` → `8310_5`).

Current `case_viewer_new.html` does none of this. It builds empty collapsible Bootstrap panels and calls `populatePanels('#physio-content', caseData.physio_data || [])`.

## 5. Tests

`SEMRinterface/tests/test_models.py` and `test_services.py`. Model tests create `User` without `username`/`password` (will fail uniqueness on `username=''` after the first user). `test_services.py` has a duplicated `except ImportError` block. No view, URL, template, or loader tests. Fixture `test_data.json` uses invented schemas (`panels`, `gender`, ISO timestamps) that do not match `resources/` or the models' real payloads.

## 6. Settings / secrets

- `SECRET_KEY = '$$$$$ENTER SECRET KEY$$$$$'` committed.
- `DEBUG = True` committed.
- `ALLOWED_HOSTS = ['localhost', '127.0.0.1', '::1']`.
- Config-from-JSON is commented out in `settings.py`. `setup_wizard.py` writes `config.json` (gitignored) **and also string-replaces SECRET_KEY in settings.py**.
- `.idea/` IDE files are committed. `SEMRproject/.idea/workspace.xml` is committed.
- Health and `system_info` are public.

## 7. Branches and history to use during refactor

| Ref | What it is |
|---|---|
| `master` @ `0c39275` | Current public default. 2024.2 skeleton + README. |
| `a2c35bf` (2024-07-10) | Last research-stable: Django 5, JSON files, `emr_3.js`, `case_viewer.html`, Synthea loader. |
| `dev1` @ `c611243` | Continuation of the incomplete rewrite, not a better UI. |

Do not treat in-repo `docs/*.md` as source of truth. They describe endpoints, templates, and "no breaking changes" that the code does not implement.
