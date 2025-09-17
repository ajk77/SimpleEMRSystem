"""
Service layer for the Simple EMR System.

This module encapsulates all file- and JSON-based data access used by the
SEMR interface views. It provides a thin, testable abstraction for reading
and writing study metadata, user assignments, and case-specific payloads
from the `resources` directory.

Conventions
- All paths are resolved from the current working directory at runtime
  (see `BASE_DIR`).
- Each study lives under `resources/<study_id>/` and contains JSON files
  referenced by the helpers below.

Functions in this module should avoid any framework (Django) concerns and
only perform I/O and in-memory transformations so they are easy to reuse and
unit test.
"""

import os
import json
import logging
from typing import Dict, List, Optional
try:
    from django.conf import settings  # type: ignore
except Exception:  # pragma: no cover - fallback for non-Django contexts
    class _SettingsFallback:
        BASE_DIR = os.getcwd()
    settings = _SettingsFallback()

logger = logging.getLogger(__name__)

BASE_DIR = getattr(settings, "BASE_DIR", os.getcwd())
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")

def load_json(file_path: str) -> Optional[Dict]:
    """Load and parse JSON from `file_path`.

    Parameters
    ----------
    file_path: str
        Absolute path to a JSON file on disk.

    Returns
    -------
    dict | None
        Parsed JSON object if the file exists, otherwise None.
    """
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            logger.warning("Failed to decode JSON at %s", file_path)
            return None
    return None

def save_json(data: Dict, file_path: str) -> None:
    """Write `data` as pretty-printed JSON to `file_path`.

    Parameters
    ----------
    data: dict
        JSON-serializable mapping to persist.
    file_path: str
        Absolute path where the file will be written (created or replaced).
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def get_study_ids(resources_dir: str = RESOURCES_DIR) -> List[str]:
    """List available study identifiers.

    Parameters
    ----------
    resources_dir: str
        Root resources directory that contains per-study folders.

    Returns
    -------
    list[str]
        Directory names found in `resources_dir`.
    """
    if not os.path.exists(resources_dir):
        return []
    return [
        item for item in os.listdir(resources_dir)
        if os.path.isdir(os.path.join(resources_dir, item))
    ]

def get_user_details(study_id: str, resources_dir: str = RESOURCES_DIR) -> Optional[Dict]:
    """Load the `user_details.json` mapping for a study.

    Parameters
    ----------
    study_id: str
        Study identifier.
    resources_dir: str
        Root resources directory.

    Returns
    -------
    dict | None
        Mapping of user_id -> assignment details, if present.
    """
    user_details_path = os.path.join(resources_dir, study_id, 'user_details.json')
    logger.debug("Loading user details for study '%s' from %s", study_id, user_details_path)
    return load_json(user_details_path)

def get_case_assignments(study_id: str, user_id: str, resources_dir: str = RESOURCES_DIR) -> Optional[Dict]:
    """Return assignment details for `user_id` within `study_id`.

    Returns the structure stored under the user key in `user_details.json`,
    typically containing keys like `cases_assigned` and `cases_completed`.
    """
    user_details = get_user_details(study_id, resources_dir)
    if user_details and user_id in user_details:
        return user_details[user_id]
    return None

def update_case_assignments(study_id: str, user_id: str, new_details: Dict, resources_dir: str = RESOURCES_DIR) -> bool:
    """Merge `new_details` into a user's assignment record and persist.

    Returns True on success, False if the study or user does not exist.
    """
    user_details_path = os.path.join(resources_dir, study_id, 'user_details.json')
    user_details = load_json(user_details_path)
    if not user_details or user_id not in user_details:
        return False

    user_details[user_id].update(new_details)
    save_json(user_details, user_details_path)
    return True

def load_case_details(study_id: str, case_id: str, resources_dir: str = RESOURCES_DIR) -> Optional[Dict]:
    """Return the entry for `case_id` from `case_details.json`.

    Raises FileNotFoundError if the file or case entry is missing.
    """
    case_details_path = os.path.join(resources_dir, study_id, 'case_details.json')
    case_details = load_json(case_details_path)
    if not case_details:
        raise FileNotFoundError(f"case_details.json not found or unreadable at {case_details_path}")
    if case_id not in case_details:
        raise FileNotFoundError(f"case_id '{case_id}' not present in case_details.json")
    return case_details[case_id]

def save_case_selection(study_id: str, user_id: str, case_id: str, resources_dir: str = RESOURCES_DIR) -> bool:
    """Append `case_id` to the list of selections for `user_id` within a study.

    A flat line-delimited JSON log is written to `case_selections.json`.
    Returns True on success.
    """
    selection_path = os.path.join(resources_dir, study_id, 'case_selections.json')
    selections = load_json(selection_path) or {}

    if user_id not in selections:
        selections[user_id] = []

    if case_id not in selections[user_id]:
        selections[user_id].append(case_id)

    save_json(selections, selection_path)
    return True

def mark_case_complete(study_id: str, user_id: str, case_id: str, resources_dir: str = RESOURCES_DIR) -> bool:
    """Mark `case_id` as completed for the user, persisting updates.

    Returns True when the case was recorded as completed; False when the
    user or study mapping could not be found.
    """
    user_details_path = os.path.join(resources_dir, study_id, 'user_details.json')
    user_details = load_json(user_details_path)
    if not user_details or user_id not in user_details:
        return False

    user_record = user_details[user_id]
    completed = user_record.get('cases_completed')
    if completed is None:
        user_record['cases_completed'] = []
        completed = user_record['cases_completed']
    if case_id not in completed:
        completed.append(case_id)
    save_json(user_details, user_details_path)
    return True

def reset_case(study_id: str, user_id: str, case_id: str, resources_dir: str = RESOURCES_DIR) -> bool:
    """Remove `case_id` from the user's completed list if present.

    Returns True if a removal occurred; False otherwise.
    """
    user_details_path = os.path.join(resources_dir, study_id, 'user_details.json')
    user_details = load_json(user_details_path)
    if not user_details or user_id not in user_details:
        return False

    if case_id in user_details[user_id]['cases_completed']:
        user_details[user_id]['cases_completed'].remove(case_id)
        save_json(user_details, user_details_path)
        return True
    return False

def save_selected_items(study_id: str, user_id: str, case_id: str, selected_items: List[str], resources_dir: str = RESOURCES_DIR) -> bool:
    """Append a line with the user's selected items for a case to a log.

    The log file is `stored_results.txt`, one JSON object per line for
    easy downstream parsing.
    """
    stored_results_path = os.path.join(resources_dir, study_id, 'stored_results.txt')
    try:
        with open(stored_results_path, 'a') as file:
            file.write(json.dumps({
                "user_id": user_id,
                "case_id": case_id,
                "selected_items": selected_items
            }) + '\n')
        return True
    except IOError:
        return False

def get_case_files(study_id: str, case_id: str, resources_dir: str = RESOURCES_DIR) -> Optional[Dict]:
    """Load the core JSON files for a specific case.

    Returns a mapping with keys: `demographics`, `medications`, `notes`,
    and `observations`. Missing files yield None values for their entries.

    Returns
    -------
    dict | None
        Mapping of payloads if the case directory exists; otherwise None.
    """
    case_dir = os.path.join(resources_dir, study_id, 'cases_all', case_id)
    if not os.path.exists(case_dir):
        raise FileNotFoundError(f"Case directory not found at {case_dir}")

    return {
        "demographics": load_json(os.path.join(case_dir, 'demographics.json')),
        "medications": load_json(os.path.join(case_dir, 'medications.json')),
        "notes": load_json(os.path.join(case_dir, 'note_panel_data.json')),
        "observations": load_json(os.path.join(case_dir, 'observations.json')),
    }
