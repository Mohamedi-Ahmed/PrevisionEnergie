from _bootstrap import bootstrap_project_root

bootstrap_project_root()

import json
from pathlib import Path

from app.core.config import get_settings
from app.governance.lifecycle import get_retention_policy


BASE_DIR = Path(__file__).resolve().parents[1]
OUT_FILE = BASE_DIR / "docs" / "datalake_manifest.json"


def main() -> None:
    settings = get_settings()
    config = settings.load_yaml("datalake.yaml")
    zones = config.get("datalake", {}).get("zones", {})
    retention = get_retention_policy()

    manifest = {
        "project": config.get("datalake", {}).get("architecture", "medallion"),
        "catalog": config.get("datalake", {}).get("catalog", {}).get("selected", "atlas"),
        "zones": [],
    }

    for zone_name, zone_config in zones.items():
        physical_path = zone_config.get("physical_path", "")
        absolute_path = (BASE_DIR / physical_path.replace("./", "")).resolve()
        datasets = []
        if absolute_path.exists():
            datasets = sorted(
                str(path.relative_to(BASE_DIR)).replace("\\", "/")
                for path in absolute_path.rglob("*")
                if path.is_file() and ".gitkeep" not in path.name
            )

        manifest["zones"].append(
            {
                "zone": zone_name,
                "logical_layer": zone_config.get("logical_layer"),
                "physical_path": physical_path,
                "retention_years": retention.get(zone_name, {}).get("retention_years"),
                "owner_role": zone_config.get("owner_role"),
                "reader_roles": zone_config.get("reader_roles", []),
                "datasets": datasets,
            }
        )

    OUT_FILE.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Data Lake manifest exported to {OUT_FILE}")


if __name__ == "__main__":
    main()
