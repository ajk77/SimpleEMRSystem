"""Lab runtime settings shown on the study selection (home) screen.

Resolution order for each key:
1. this browser session (set when the facilitator saves Lab settings)
2. semr_runtime.json in the project root (survives a server restart)
3. Django settings / environment (factory default)

SEMR_EYE_TRACKING_MODE defaults off. When on, the case viewer stays locked
at 1920x1080 for eye-tracking studies. The home-screen checkbox is the
intended control; the env var is only the factory default.
"""
import json
import logging
import os

from django.conf import settings as django_settings

logger = logging.getLogger(__name__)

RUNTIME_FILENAME = "semr_runtime.json"


def runtime_path():
    return os.path.join(django_settings.BASE_DIR, RUNTIME_FILENAME)


def load_runtime():
    path = runtime_path()
    if not os.path.isfile(path):
        return {}
    try:
        with open(path) as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _coerce_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("1", "true", "yes", "on")


def get_lab_setting(request, key, default=False):
    if key in request.session:
        return _coerce_bool(request.session.get(key), default)
    runtime = load_runtime()
    if key in runtime:
        return _coerce_bool(runtime.get(key), default)
    return bool(getattr(django_settings, key, default))


def get_eye_tracking_mode(request):
    return get_lab_setting(request, "SEMR_EYE_TRACKING_MODE", False)


def save_lab_settings(request, updates):
    runtime = load_runtime()
    for key, value in updates.items():
        coerced = bool(value)
        request.session[key] = coerced
        runtime[key] = coerced
    try:
        with open(runtime_path(), "w") as handle:
            json.dump(runtime, handle, indent=2)
            handle.write("\n")
    except OSError:
        logger.warning("Could not write lab settings to %s", runtime_path())
