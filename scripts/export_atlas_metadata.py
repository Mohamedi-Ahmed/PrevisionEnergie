import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
ATLAS_DIR = BASE_DIR / "atlas"
OUT_FILE = BASE_DIR / "atlas" / "atlas_bundle.json"
REQUIRED_PATHS = [
    "glossary/prevision_energie_glossary.json",
    "entities/core_entities.json",
    "entities/datalake_entities.json",
    "processes/lineage_processes.json",
    "processes/datalake_processes.json",
]


def build_bundle() -> dict:
    bundle = {}
    for relative_path in REQUIRED_PATHS:
        path = ATLAS_DIR / relative_path
        if path.exists():
            bundle[relative_path] = json.loads(path.read_text(encoding="utf-8"))
    return bundle


def summarize_bundle(bundle: dict) -> dict[str, int]:
    return {
        "files": len(bundle),
        "lineage_process_files": sum(1 for path in bundle if "lineage" in path),
        "entity_files": sum(1 for path in bundle if path.startswith("entities/")),
        "glossary_files": sum(1 for path in bundle if path.startswith("glossary/")),
    }


def main() -> None:
    bundle = build_bundle()
    missing = [relative_path for relative_path in REQUIRED_PATHS if relative_path not in bundle]
    if missing:
        raise SystemExit(f"Missing Atlas source files: {missing}")
    OUT_FILE.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Atlas metadata bundle exported to {OUT_FILE}")
    print(f"Summary: {summarize_bundle(bundle)}")


if __name__ == "__main__":
    main()
