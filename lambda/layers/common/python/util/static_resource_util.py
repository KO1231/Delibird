import os
from pathlib import Path
from typing import Optional, Any

from jinja2 import Template

from util.logger_util import setup_logger

logger = setup_logger("static_resource_util")

_IS_DEV = (os.environ.get("DELIBIRD_ENV") == "dev")
_STATIC_RESOURCE_DIR = Path(os.environ.get("STATIC_RESOURCE_DIR", str(Path(__file__).parent.parent.parent.parent.parent / "static"))).resolve()


def load_static_html(relative_path: str, template_contexts: dict[str, Any] = None) -> Optional[str]:
    file_path = (_STATIC_RESOURCE_DIR / relative_path).resolve()
    if not os.path.commonprefix([str(_STATIC_RESOURCE_DIR), str(file_path)]) == str(_STATIC_RESOURCE_DIR):
        raise ValueError("Invalid relative path; attempts to access outside the static resource directory.")
    if not file_path.is_file():
        logger.warning(f"Static resource file not found at {file_path}")
        return None

    try:
        template = Template(file_path.read_text())
        result = template.render(template_contexts or {})
    except Exception as e:
        logger.warning("Unexpected error occurred while generating HTML body.", exc_info=e)
        return None

    return result
