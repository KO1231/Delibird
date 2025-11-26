import json
import os
from typing import Any

_ENV_VAR: dict[str, Any] = json.loads(os.environ["ENV_VAR"])


def get_env_var(key: str, default: Any = None) -> Any:
    return _ENV_VAR.get(key, default)
