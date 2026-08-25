# SimpleEMRSystem Deployment

How the project actually runs today, what is fragile, and what a modern Python/Django deploy needs. Code references are current `master` (`0c39275`) unless noted.

## 1. Current run / install path

### 1.1 Documented happy path (README)

```
python -m venv semr_env
source semr_env/bin/activate   # or semr_env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py load_resources
python manage.py runserver
# browser: http://127.0.0.1:8000/SEMRinterface/
```

`requirements.txt`:

```
Django==5.0.7
python_dateutil==2.9.0.post0
requests==2.31.0
Pillow==10.1.0
```

Django 5.0 requires **Python 3.10+**, not 3.8 as README/`install.sh` claim. `requests` and `Pillow` are unused by application code (no image uploads, no HTTP client in the app). `python-dateutil` is only needed by the deleted Synthea loader.

### 1.2 `install.sh` / `install.bat`

1. Require `python3` (sh) / `python` (bat). Version check in sh is `>=3.8`; bat does not check.
2. `python -m venv semr_env` in the repo root (venv is gitignored).
3. `pip install -r requirements.txt`
4. `python manage.py migrate`
5. `python manage.py load_resources`  ← likely no-ops; see §2
6. Optional `createsuperuser`
7. `python manage.py runserver` (foreground; install script never returns)

They create `resources/` only **after** `load_resources`, so a zip without `resources/` cannot be repaired by the script.

### 1.3 `setup_wizard.py`

Interactive. Writes `config.json` (gitignored), string-replaces `SECRET_KEY` **inside** `SEMRproject/settings.py`, pip-installs, migrates, calls `load_resources`, may create a bogus `resources/sample_study` whose JSON is not viewer-compatible, then optional `createsuperuser`. It `from django.core.management import execute_from_command_line` at import time — fails if Django is not already installed before the wizard's own pip step... actually `install_dependencies()` runs before `setup_database()`, but the top-level `from django.core.management import execute_from_command_line` runs at import, i.e. **before** `main()`. Fresh machines: `python setup_wizard.py` ImportError unless Django is already present.

### 1.4 Docker (present, not viable)

`Dockerfile`:

```
FROM python:3.6.8
...
pip install -r requirements.txt
```

Django 5.0.7 will not install on 3.6. Compose runs `python manage.py runserver 0.0.0.0:8000` with no migrate, no `load_resources`, no SECRET_KEY, compose file version `'3'` with odd indentation. Commit `a2c35bf` message said "Docker option removed"; files were reintroduced in the 2024.2 rewrite in a broken state.

### 1.5 What actually happens after a successful `runserver`

- Django dev server, `DEBUG=True`, SQLite file `db.sqlite3` in the repo root (gitignored as `db.*`).
- App is mounted at `/` **and** `/SEMRinterface/`.
- Unauthenticated GET `/` redirects to `/login/` (2024.2). Original flow had no login.
- Static files served by `runserver` via `AppDirectoriesFinder` from `SEMRinterface/static/`. `STATIC_ROOT` is empty; `collectstatic` has nowhere to go.
- jQuery and Highcharts load from public CDNs (needs network; lab machines often do not).
- WSGI module `SEMRproject/wsgi.py` sets `LEMRProject.settings` — Gunicorn/uWSGI would fail even if pointed at this file. `runserver` is fine because `manage.py` sets `SEMRproject.settings`.

## 2. What is fragile

1. **Placeholder secret and DEBUG on.** Health check even flags this. `setup_wizard` patches settings.py rather than reading env.
2. **`load_resources` does not load from disk when Django is importable.** First-run installs create an empty Study table; the selection page is empty. This is the primary "it installed but nothing shows up" failure.
3. **Auth vs resource users.** Login is required, but loaded users have unusable passwords. Researchers cannot reach `/select/` without a separately created superuser, and that superuser has `study=None` so study-access checks (in the unused first `unified_selection_view`) would 403 anyway.
4. **Missing research URLs and templates.** Continue, mark-complete, time-step, and selection-save 404. Original `case_viewer.html` / `emr_3.js` are gone. A "successful" deploy still cannot run a study.
5. **Dual URL mount + mixed JS prefixes.** `getCaseData` uses `/api/...`; save uses `/SEMRinterface/selected_items/...`; `getUsers` POSTs to the current path. Breaks if the app is mounted only at one prefix, or behind a path-stripping reverse proxy.
6. **`wsgi.py` wrong settings module** (`LEMRProject`). Historical rename leftover (LEMR → SEMR).
7. **Python version lie.** 3.8 advertised; Django 5.0 needs 3.10–3.12 (5.0 is already EOL; 5.1/5.2 would be the current LTS path).
8. **SQLite + JSON blobs.** Entire `observations.json` (tens to hundreds of KB per case; demo case 10000102 observations is 216 KB) stored in one column. Fine for N=3 demo cases; painful for concurrent lab sessions if moved to a network FS. No `ATOMIC_REQUESTS`, no `CONN_MAX_AGE`.
9. **Mutable source JSON.** Original `mark_complete` rewrote `user_details.json` in place. Two browsers completing cases race and can drop assignments. DB `JSONField` lists have the same RMW race (`append` then `save`).
10. **CDN JS.** Highcharts + jQuery from `code.jquery.com` / Highcharts CDN. Offline / air-gapped labs fail with a blank viewer. Original tree vendored bootstrap.js and used CDN Highcharts after the Django 5 upgrade ("JQuery and HighCharts now dynamically load most recent versions") — also fragile.
11. **No `collectstatic`, no WhiteNoise, no nginx recipe.**
12. **Committed `.idea/` and Bitnami comments in `manage.py`.** Windows Bitnami stack is gone; comments still tell users to open it.
13. **Health endpoints unauthenticated** and report filesystem paths, study ids, DEBUG, ALLOWED_HOSTS.
14. **`csrf_exempt` on `case_viewer` and `get_case_data`.** Combined with no object-level auth on case ids, any logged-in user can fetch any case JSON.
15. **Pickle files** in `resources/synthea_study/stored_objects/` (`encounter_observations.p` is ~797 KB). Do not load untrusted pickles. Not needed at runtime.
16. **`setup.py` / packaging.** `packages=['SEMRinterface','SEMRproject']` does not include `resources/`, templates via package data, or `manage.py`. `pip install .` is not a runnable app.

## 3. What a modern Python deploy needs

Split local vs production. Keep SQLite as the default local DB; do not require Postgres for a 3-case lab study.

### 3.1 Local (researcher laptop / lab PC)

- Python 3.12 (or 3.11) + `venv`.
- `pip install -e .` or `pip install -r requirements/local.txt` with **pinned hashes** (`pip-tools` or `uv lock`).
- `.env` / environment variables: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=1`, `DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost`.
- Settings package: `SEMRproject/settings/{base,local,production}.py` selected by `DJANGO_SETTINGS_MODULE`.
- One command: `python manage.py setup_study` that **reads `resources/` from disk** (not via DB-preferring helpers), migrates, loads, and optionally prints demo credentials if auth stays.
- `python manage.py runserver` remains acceptable for lab use. Optionally wrap with `honcho`/`just`.
- Vendor jQuery, Bootstrap, Highcharts (or pin exact CDN versions with SRI) so the viewer works offline.
- Do not require Docker for local. If Docker is offered: Python 3.12-slim, `migrate && load_resources && runserver` (or gunicorn) as entrypoint, named volume for `db.sqlite3` and `resources/`.

### 3.2 Production (shared lab server / IRB-facing)

Minimum:

| Piece | Recommendation |
|---|---|
| Process | Gunicorn (or uvicorn+whitenoise if ASGI later) targeting `SEMRproject.wsgi:application` after fixing the settings module. |
| Reverse proxy | nginx: TLS, `client_max_body_size` small, static alias after `collectstatic`. |
| Static | `STATIC_ROOT=/var/www/semr/static`, WhiteNoise as a zero-nginx option for small deploys. |
| Secrets | env or systemd `EnvironmentFile`; never rewrite `settings.py`. |
| `DEBUG` | False. `ALLOWED_HOSTS` explicit. `CSRF_TRUSTED_ORIGINS` for the public URL. |
| DB | SQLite + backups is enough for single-server lab studies. Postgres only if multiple app workers write `cases_completed` concurrently — then also replace JSON list RMW with a real `CaseAssignment` table. |
| Auth | If the original no-login flow is restored, put the whole site behind lab SSO / IP allowlist / HTTP basic at nginx, **or** a simple shared study PIN. Do not force Django passwords onto `user_details.json` participants without a provisioning story. |
| Logging | stdout JSON or files; drop `mail_admins` unless `ADMINS` is set. |
| Health | `/health/` returns 200/503 without leaking paths; gate `/api/info/` on staff. |
| Backups | `db.sqlite3` + `resources/*/stored_results.txt` + `user_details.json` after each session. |
| TLS / PHI | Sample data is synthetic. If real records are ever loaded, this stack is not HIPAA-ready (DEBUG, CSRF-exempt, no audit log, SQLite on disk). Treat that as a hard product constraint, not a deploy checkbox. |

### 3.3 Settings split (concrete)

```
SEMRproject/
  settings/
    __init__.py          # import local by default
    base.py              # INSTALLED_APPS, AUTH_USER_MODEL, MIDDLEWARE, TEMPLATES
    local.py             # DEBUG=True, sqlite, console email
    production.py        # DEBUG=False, env SECRET_KEY, optionally Postgres
    test.py              # in-memory sqlite, faster hasher
```

Read `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL` from environment (`django-environ` or `os.environ`). Fail fast in production if `SECRET_KEY` is missing or still the placeholder.

`USE_TZ=True` is already set. Replace `USE_L10N` (removed in Django 5). Add `DEFAULT_AUTO_FIELD`. Set `LOGIN_URL`, `LOGIN_REDIRECT_URL` only if auth remains.

### 3.4 Static and WSGI

- Fix `wsgi.py` to `SEMRproject.settings`.
- Add `asgi.py` only if needed later.
- `collectstatic` in the Docker/production entrypoint.
- Pin frontend libs; stop "latest Highcharts from CDN".

### 3.5 Tests in CI

`python manage.py test` is not enough until tests match real schemas and cover:

- `load_resources` from a temp `resources/` tree
- study → user → case → time_step → save selected_ids → mark complete
- JSON schema fixtures copied from `demo_study`

GitHub Actions: Python 3.12, `migrate`, `load_resources`, `test`, a Playwright smoke of the demo case viewer.

## 4. Mapping install scripts → replacement

| Today | Replace with |
|---|---|
| `install.sh` / `install.bat` | `README` + `python -m venv` + `pip install -r requirements.txt` + `python manage.py setup_study`. Optional `powershell`/`make` wrappers. |
| `setup_wizard.py` | Drop, or rewrite as a management command that does **not** import Django at module level and does **not** edit `settings.py`. |
| `Dockerfile` + compose | New 3.12 image, entrypoint script, healthcheck hitting `/health/`. Not required for v1. |
| `setup.py` | `pyproject.toml` with `[project.scripts]` optional; include package-data for templates/static; ship `resources/demo_study` as package data or a separate download. |

## 5. Data location at runtime

Original: CWD/`resources` (process must be started from repo root). `services.BASE_DIR = settings.BASE_DIR` is the repo root, which is correct if `manage.py` lives there. Do not rely on `os.getcwd()`.

Recommendation: `SEMR_RESOURCES_DIR` env, default `BASE_DIR / "resources"`. Loaders and views use that path only.
