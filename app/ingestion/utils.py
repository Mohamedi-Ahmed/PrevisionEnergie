from datetime import datetime
from pathlib import Path


def build_raw_filename(source_name: str, extension: str, prefix: str | None = None) -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    base_name = prefix or source_name
    return f"{base_name}_{timestamp}.{extension.lstrip('.')}"


def infer_extension_from_path(path: str, default: str) -> str:
    suffix = Path(path).suffix.replace('.', '')
    return suffix or default
