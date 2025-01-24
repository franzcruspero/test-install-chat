import json
import logging

from constance import config
from typing import Any

from django.conf import settings
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

def environment_callback(request):
    if settings.DEBUG:
        return [_("Development"), "info"]

    return [_("Production"), "warning"]


def get_constance_value(key: str) -> Any:
    constance_value = getattr(config, key)
    try:
        parsed_value = json.loads(constance_value)
        if isinstance(parsed_value, dict):
            return parsed_value
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"Error decoding JSON for key {key}: {e}")
        pass
    return constance_value


def lazy_constance_value(key: str) -> Any:
    return lazy(lambda: get_constance_value(key), str)
