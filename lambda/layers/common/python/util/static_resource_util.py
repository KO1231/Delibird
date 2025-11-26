import html
import os
from pathlib import Path
from typing import Optional

from util.environment_util import get_env_var
from util.logger_util import setup_logger

logger = setup_logger("static_resource_util")

_IS_DEV = (os.environ.get("DELIBIRD_ENV") == "dev")
_STATIC_RESOURCE_DIR = Path(os.environ.get("STATIC_RESOURCE_DIR", str(Path(__file__).parent.parent.parent.parent.parent / "static"))).resolve()
_STATIC_FOOTER: Optional[str] = html.escape(get_env_var("STATIC_FOOTER", ""))


def load_static_html(relative_path: str) -> Optional[str]:
    file_path = (_STATIC_RESOURCE_DIR / relative_path).resolve()
    if not os.path.commonprefix([str(_STATIC_RESOURCE_DIR), str(file_path)]) == str(_STATIC_RESOURCE_DIR):
        raise ValueError("Invalid relative path; attempts to access outside the static resource directory.")
    if not file_path.is_file():
        logger.warning(f"Static resource file not found at {file_path}")
        return None

    result = file_path.read_text()
    if _IS_DEV and _STATIC_FOOTER:
        result = result.replace("{{STATIC_FOOTER}}", f"<div class=\"env-info\"><p>{_STATIC_FOOTER}</p></div>")
    else:
        result = result.replace("{{STATIC_FOOTER}}", "")

    return result
