import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
ATLAS_DIR = BASE_DIR / "atlas"
OUT_FILE = BASE_DIR / "atlas" / "atlas_bundle.json"


def main() -> None:
    bundle = {}
    relative_paths = [
        "glossary/energy_forecast_glossary.json",
        "entities/core_entities.json",
        "entities/datalake_entities.json",
        "processes/lineage_processes.json",
        "processes/datalake_processes.json",
    ]
    for relative_path in relative_paths:
        path = ATLAS_DIR / relative_path
        if path.exists():
            bundle[relative_path] = json.loads(path.read_text(encoding="utf-8"))
    OUT_FILE.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Atlas metadata bundle exported to {OUT_FILE}")


if __name__ == "__main__":
    main()
