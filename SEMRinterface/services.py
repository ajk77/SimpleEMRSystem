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
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

try:
    from django.conf import settings  # type: ignore
    from django.utils.dateparse import parse_datetime as django_parse_datetime
    from .models import Study, User, Case, Medication, CaseMedication, StoredResult, CaseSelection
    DJANGO_AVAILABLE = True
except Exception:  # pragma: no cover - fallback for non-Django contexts
    class _SettingsFallback:
        BASE_DIR = os.getcwd()
    settings = _SettingsFallback()
    Study = User = Case = Medication = CaseMedication = StoredResult = CaseSelection = None
    django_parse_datetime = None
    DJANGO_AVAILABLE = False

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
    """List available study identifiers from disk (files-first).

    Studies are `*_study` folders under `resources/`. Does not require
    `load_resources` or SQLite Study rows. An empty database table cannot
    hide sample studies.
    """
    if not os.path.exists(resources_dir):
        return []
    return [
        item for item in os.listdir(resources_dir)
        if os.path.isdir(os.path.join(resources_dir, item)) and '_study' in item
    ]
