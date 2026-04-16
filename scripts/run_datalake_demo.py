from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from _bootstrap import bootstrap_project_root

BASE_DIR = bootstrap_project_root()


def run(script_name: str) -> None:
    script_path = BASE_DIR / "scripts" / script_name
    subprocess.run([sys.executable, str(script_path)], check=True, cwd=BASE_DIR)


def main() -> None:
    run("generate_datalake_manifest.py")
    run("export_atlas_metadata.py")

    manifest_path = BASE_DIR / "docs" / "datalake_manifest.json"
    atlas_path = BASE_DIR / "atlas" / "atlas_bundle.json"

    print("Data Lake local summary")
    print(f"manifest_exists: {manifest_path.exists()}")
    if manifest_path.exists():
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        print(f"zones: {', '.join(zone['zone'] for zone in payload.get('zones', []))}")

    print(f"atlas_bundle_exists: {atlas_path.exists()}")
    if atlas_path.exists():
        payload = json.loads(atlas_path.read_text(encoding="utf-8"))
        print(f"atlas_sections: {', '.join(payload.keys())}")

    print("reference_files:")
    for relative_path in [
        "docs/block4_datalake.md",
        "docs/block4_governance.md",
        "docs/block4_referential_mapping.md",
        "configs/datalake.yaml",
    ]:
        exists = (BASE_DIR / relative_path).exists()
        print(f"- {relative_path} | exists={exists}")


if __name__ == "__main__":
    main()
