# SimpleEMRSystem Data Model and JSON Schemas

Source of truth is `resources/<study_id>/` plus the loaders. Django models on current `master` are a thin JSON-blob overlay of the same files. Fixtures and in-repo `docs/API.md` invent a different schema; ignore them.

## 1. Study directory layout

A study is a folder under `resources/` whose name conventionally contains `_study` (original `get_list_study_id` required that substring; current `get_study_ids` filesystem fallback lists **any** subdirectory, including stray folders).

```
resources/<study_id>/
  data_layout.json          # UI regions and group order
  variable_details.json     # per-observation metadata
  med_details.json          # per-medication catalog
  user_details.json         # participants and case assignments
  case_details.json         # per-case temporal epochs + task flags
  stored_results.txt        # append-only participant selections (JSONL)
  list_case_dicts.json      # synthea only: preprocessor catalog (not loaded by Django)
  stored_objects/           # synthea only: pickle intermediates
  cases_all/<case_id>/
    demographics.json
    observations.json
    medications.json
    note_panel_data.json
```

HTML/DOM ids cannot contain `-`. Observation and medication keys used as row ids must use underscores (e.g. LOINC `8310-5` → `8310_5`).

## 2. Study-level files

### 2.1 `data_layout.json`

Object of string arrays. Keys are **required** by the original viewer.

```json
{
  "title_bar": ["id", "age", "sex", "height", "weight", "bmi", "race"],
  "physio_panel_groups": ["Vitals", "Ventilator"],
  "med_panel_groups": ["IV", "By_Mouth", "subQ", "..."],
  "lab_panel_groups": ["Blood_Gases", "CBC", "Other", "..."],
  "note_panel_groups": ["Progress_Note", "HandP", "RAD", "ECHO", "EKG", "Micro", "..."]
}
```

| Key | Meaning |
|---|---|
| `title_bar` | Demographic field names, rendered left-to-right in the navbar. Must exist on `demographics.json`. |
| `physio_panel_groups` | Observation groups shown in the left physiological column. |
| `med_panel_groups` | Medication route buckets (must match `med_details[].med_route`). |
| `lab_panel_groups` | Observation groups shown in the lab column. `"UNASSIGNED"` is the Synthea default dump bucket. |
| `note_panel_groups` | Keys into `note_panel_data.json`. |

**demo_study** uses hospital-style routes and lab panels. **synthea_study** uses `physio_panel_groups: ["Physio","O2_Therapy"]`, a single `All_routes` med group, and note groups `Careplan/Condition/Device/Procedure/Allergies/Images/Immunizations`.

### 2.2 `variable_details.json`

Map of observation key → metadata. Keys are the same as in `observations.json`.

Inferred schema (from Synthea loader `loaddata_synthea.py` and demo file size ~156 KB):

```json
{
  "<obs_key>": {
    "display_group": "CBC",
    "original_name": "Hemoglobin [Mass/volume] in Blood",
    "display_name": "Hemoglobin",
    "units": "g/dL",
    "dflt_normal_ranges": ["", ""],
    "dflt_y_axis_ranges": [0, 0]
  }
}
```

| Field | Role |
|---|---|
| `display_group` | Must match a name in `physio_panel_groups` or `lab_panel_groups`. Loader writes `"UNASSIGNED"` when unknown. |
| `original_name` | Full source label (LOINC text, Cerner name). |
| `display_name` | Short label on the chart row. |
| `units` | Axis / tooltip units. |
| `dflt_normal_ranges` | `[low, high]` used to color Highcharts zones (blue below low, green in range, red above high). Empty string means that bound is unused. |
| `dflt_y_axis_ranges` | Fallback `[min, max]` when a case has no points. |

Researchers edit this file to regroup labs, rename, and set normal ranges. It is **not** currently stored except as `Study.variable_details` JSON; the 2024.2 viewer never reads it.

### 2.3 `med_details.json`

Map of medication id → catalog row.

```json
{
  "medidx0": {
    "med_route": "IV",
    "display_name": "albumin human",
    "original_name": "albumin human 25% intravenous solution"
  }
}
```

Synthea uses RxNorm codes as keys (`"1807513"`) and typically `"med_route": "All_routes"`. Demo uses `medidxN`. `med_route` must appear in `data_layout.med_panel_groups` or the med will not render.

Loaded into `Medication(study, medidx, display_name, original_name, med_route)`.

### 2.4 `user_details.json`

Map of participant id → assignment record. **This is the original "user" concept: a study participant, not a Django login.**

```json
{
  "testUser1": {
    "last_accessed": null,
    "cases_assigned": ["10000101", "10000102", "10000103"],
    "cases_completed": []
  }
}
```

| Field | Type | Notes |
|---|---|---|
| `last_accessed` | `null`, ISO datetime, or epoch-ms number | Synthea `demo_234` uses `88` (invalid as a real timestamp; loader tries `/1000`). |
| `cases_assigned` | string[] | Case ids the participant may open. |
| `cases_completed` | string[] | Filled by `mark_complete` / `markcompleteurl`. Reset removes an id. |
| `name` | optional string | 2024.2 selection UI looks for `details.name`; demo_study does **not** include it, so the dropdown falls back to the id. |

Original system had **no passwords**. 2024.2 `load_resources._load_users` `get_or_create`s `User` with only assignment fields — no `set_password`, no `username` distinct from default `''`.

### 2.5 `case_details.json`

Map of case id → **ordered list of epochs** (time steps). This is the task protocol.

```json
{
  "10000101": [
    {"min_t": 1352687400000.0, "max_t": 1352946600000.0, "check_boxes": 0, "instruction_set": "familiar"},
    {"min_t": 1352687400000.0, "max_t": 1353033000000.0, "check_boxes": 1, "instruction_set": "select"}
  ]
}
```

| Field | Type | Meaning |
|---|---|---|
| `min_t` | number (JS epoch **milliseconds**) | Chart x-axis left / admit time. |
| `max_t` | number (ms) | Chart x-axis right / "now". Continue to the next epoch typically extends `max_t`. |
| `check_boxes` | 0 or 1 | 0 = review only; 1 = rows are selectable and saved. |
| `instruction_set` | `"familiar"` or `"select"` | Hardcoded copy in original `views.case_viewer`: familiar = "become familiar with this patient"; select = "select the information you used when preparing to present this case." |

`time_step` in the URL is the index into this list. After the last epoch, Continue hits `markcompleteurl`.

Loaded into `Case.case_details` as that list (or `[]` if the case exists on disk but not in this file).

### 2.6 `stored_results.txt`

JSON Lines, one object per Continue on a select-epoch. Original writer used key `selected_ids`; 2024.2 `save_selected_items` filesystem fallback uses `selected_items`. Preserve **`selected_ids`** for compatibility with existing analysis scripts.

```json
{"user_id": "testUser1", "case_id": "10000102", "selected_ids": ["rowBASEDA","rowPO2V","rowHCO3V","rowmedidx47","rowIO"]}
```

Id convention from demo results: `row` + observation key (`rowBUN`, `rowK`) or `row` + med key (`rowmedidx1`). These are DOM ids of `.chartrow` / `.medrow` elements.

On master, `StoredResult.selected_items` is the DB equivalent, but no view writes it.

## 3. Per-case files (`cases_all/<case_id>/`)

### 3.1 `demographics.json`

Flat object. Keys used by `title_bar`.

demo_study:

```json
{"weight": 105.0, "age": 64, "bmi": 32.3, "sex": "M", "race": "n/a **SYNTHETIC DATA**", "height": 180.3, "id": 10000101}
```

synthea_study:

```json
{"age": 82, "sex": "M", "race": "white", "ethnicity": "nonhispanic", "id": "<uuid>", "name": "Stanley702 Douglas31"}
```

### 3.2 `observations.json`

Map of observation key → Highcharts-ready payload (already preprocessed, not raw labs).

Schema produced by `process_observation_type` in `loaddata_synthea.py`:

```json
{
  "<obs_key>": {
    "display_text": "string",
    "numeric_lab_data": [
      {
        "name": "numeric_values",
        "zones": [{"value": low, "color": "#00CCFF"}, {"value": high, "color": "#33CC33"}, {"color": "#BF0B23"}],
        "data": [[t_ms, y], ...],
        "marker": {"symbol": "circle"}
      }
    ],
    "discrete_lab_data": [
      {
        "name": "discrete_values",
        "color": "#000000",
        "data": [[t_ms, yIndex], ...],
        "marker": {"symbol": "square"}
      }
    ],
    "discrete_nominal_to_yIndex": ["nominal value 0", "..."],
    "y_axis_ranges": [min, max]
  }
}
```

Empty series are `[]`. Points with `t > time_cut` (usually discharge / epoch `max_t`) are dropped at preprocess time; the viewer still also sets Highcharts extremes to the current epoch.

Loaded wholesale into `Case.observations`.

### 3.3 `medications.json`

Map of med key → series payload.

```json
{
  "1807513": {
    "display_text": "vancomycin 1000 MG Injection",
    "med_data": [{
      "name": "medication_data",
      "color": "#000000",
      "data": [[1583298000000.0, 263.49]],
      "marker": {"symbol": "circle"},
      "med_reason_tooltips": ["Septic shock (disorder)"]
    }],
    "y_axis_ranges": [263.49, 263.49]
  }
}
```

`load_resources` splits this: looks up `Medication` by `medidx`, stores `med_data` and `y_axis_ranges` on `CaseMedication`. `get_case_files` reconstitutes `{medidx: {display_text, med_data, y_axis_ranges}}` using `Medication.display_name` as `display_text`. If a case med is missing from `med_details.json`, that row is skipped with a warning.

### 3.4 `note_panel_data.json`

Map of group name → list of notes, newest-first via `upk` (rank).

```json
{
  "Progress_Note": [
    {"date": "11/14", "text": "REPORT TEXT HERE", "js_time": 1352865600000.0, "upk": 0, "type": "Progress Note"}
  ],
  "ECHO": [
    {"date": "11/11", "text": "REPORT TEXT HERE", "js_time": 1352692800000.0, "upk": 0, "type": "ECHO"}
  ]
}
```

| Field | Meaning |
|---|---|
| `date` | Display date `MM/DD`. |
| `text` | Body. Demo data is placeholder `"REPORT TEXT HERE"`. |
| `js_time` | Epoch ms for filtering vs current `max_t`. |
| `upk` | Sort index (0 = most recent in that group). |
| `type` | Optional subtype label. |

**Synthea bug:** `loaddata_synthea.py` builds `note_panel_data` then writes `save_json_dumps(result, ... note_panel_data.json)` — `result` is the last group processed (`Device`), so most synthea `note_panel_data.json` files are `[]` (2 bytes). Restore the loader to dump `note_panel_data`, not `result`.

## 4. Loaders

### 4.1 `python manage.py load_resources` (master)

Intended path: walk `resources/`, upsert Study/User/Medication/Case/CaseMedication.

Actual bugs:

1. `get_study_ids()` returns `Study.objects.values_list(...)` whenever Django is importable, so a fresh DB yields `[]` and the command exits with "No studies found". `--reset` makes this worse (deletes studies first).
2. `_load_users` calls `get_user_details()`, which also hits the DB first, so users are not created from JSON on first load even if studies somehow exist.
3. Users are created without passwords / usable `username`.
4. `get_or_create` will not refresh JSON if the study already exists (`data_layout`/`variable_details` stay stale).
5. Case meds whose `medidx` is absent from `med_details.json` are dropped.

Filesystem fallback in `services.py` is the original, working I/O. A refactor should either (a) keep files as source of truth at request time, or (b) make the command read files directly and never call the DB-preferring helpers.

### 4.2 `loaddata_synthea.py` (missing on master; live at `a2c35bf`)

Offline ETL, not a management command. `__main__` parameters:

| Parameter | Default in repo | Meaning |
|---|---|---|
| `source_file_dir` | `../resources/100k_synthea_covid19_csv/...` | Synthea CSV dump (gitignored). |
| `base_dir` | `../resources/synthea_study` | Output study. |
| `load_source_files` | `False` | If true, parse CSVs into `stored_objects/*.p` pickles. |
| `replace_files` | `True` | Wipe `cases_all/` and rewrite JSON. |
| `encounter_codes_to_keep` | `['305351004']` | SNOMED ICU admission. |
| `number_of_encounters_to_load` | 25 | Cap. |
| `min_observation_fields` | 15 | Skip sparse encounters. |
| `min_medication_types` | 3 | Skip sparse encounters. |

Pipeline:

1. Parse Synthea CSVs (encounters, patients, observations, medications, procedures, conditions, careplans, imaging, immunizations, devices, allergies) into pickles plus code→text maps (SNOMED, LOINC, RxNorm, CVX).
2. For each kept encounter, write the four case JSON files; auto-extend `variable_details.json` / `med_details.json` for unseen codes.
3. Write `list_case_dicts.json` (catalog with LOS, counts, admit reason). Researchers then **manually** copy chosen ids into `case_details.json` and `user_details.json`.

Pickle usage is a Py2/Py3 and security liability; replace with JSON in a later slice, but keep the CSV column mapping.

### 4.3 `loaddata.py` (missing on master)

Hospital/Cerner preprocessor. Original `models.py` at `a2c35bf` was unmanaged mappings to tables `a_ClinicalEvents`, `a_demographics`, `a_Medication`, `a_Micro`, `lab_739`, etc. Those models were **not** used by the runtime viewer; the runtime always read JSON. Keep as an optional import path, not as Django's `AUTH`/runtime schema.

## 5. Django overlay (master)

| JSON | Model field |
|---|---|
| study folder name | `Study.study_id` |
| `data_layout.json` | `Study.data_layout` |
| `variable_details.json` | `Study.variable_details` |
| `med_details.json` rows | `Medication` |
| `user_details.json` | `User.cases_assigned/completed/last_accessed` |
| `case_details.json[case]` | `Case.case_details` |
| `demographics.json` | `Case.demographics` |
| `observations.json` | `Case.observations` |
| `note_panel_data.json` | `Case.note_panel_data` |
| `medications.json` | split across `Medication` + `CaseMedication` |
| `stored_results.txt` lines | `StoredResult` (never written by current views) |

`med_details` is **not** stored on Study, only as Medication rows. `data_layout` is stored but unused by current views/templates.

## 6. What is not a schema

- `SEMRinterface/fixtures/test_data.json` uses `data_layout.panels`, `gender`, ISO observation lists — none of that exists in `resources/`.
- `docs/API.md` `case_data.medications.active/discontinued` is fictional.
- `setup_wizard.py` `create_sample_data()` writes a `sample_study` whose JSON would not render in the original viewer.

## 7. Sample studies on master

| Study | Cases on disk | Cases in `case_details.json` | Users |
|---|---|---|---|
| `demo_study` | 3 (`10000101`–`103`) | 3, two epochs each | `testUser1`, `testUser2` (all three cases assigned) |
| `synthea_study` | 9 UUID folders | 3 UUIDs | `demo_234`, `demo2` (those three cases) |

README claims "25 ICU encounters"; `loaddata_synthea.py` default is 25 but the committed tree has 9 case folders and only 3 assigned. Extra folders are unassigned leftover ETL output.
