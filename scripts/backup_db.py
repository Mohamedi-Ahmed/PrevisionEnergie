"""
Script de backup planifié pour PrevisionEnergie.

Stratégie :
- Backup partiel (quotidien) : copie de la base SQLite
- Backup complet (hebdomadaire) : base + données + configs
- Rétention configurable (7 jours partiel, 30 jours complet)

Usage :
    python scripts/backup_db.py                # backup partiel
    python scripts/backup_db.py --full          # backup complet
    python scripts/backup_db.py --cleanup       # nettoyage des anciens backups

Compétence couverte : C16 (tâches planifiées de backup partiel et complet).
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app.core.config import get_settings
from app.governance.monitoring import emit_alert

BACKUP_DIR = BASE_DIR / "backups"
DB_FILE = BASE_DIR / "prevision_energie.db"


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def backup_partial() -> Path:
    """Backup partiel : copie de la base SQLite uniquement."""
    dest_dir = BACKUP_DIR / "partial"
    dest_dir.mkdir(parents=True, exist_ok=True)

    if not DB_FILE.exists():
        emit_alert("BACKUP", "ERROR", f"Base introuvable : {DB_FILE}")
        print(f"ERREUR : {DB_FILE} introuvable")
        sys.exit(1)

    dest = dest_dir / f"prevision_energie_{_timestamp()}.db"
    shutil.copy2(DB_FILE, dest)

    emit_alert("BACKUP", "INFO", f"Backup partiel créé : {dest.name}",
               {"size_bytes": dest.stat().st_size})
    print(f"Backup partiel : {dest}")
    return dest


def backup_full() -> Path:
    """Backup complet : base + data/ + configs/ dans une archive zip."""
    dest_dir = BACKUP_DIR / "full"
    dest_dir.mkdir(parents=True, exist_ok=True)

    archive_name = f"prevision_energie_full_{_timestamp()}"
    targets = []

    if DB_FILE.exists():
        targets.append(str(DB_FILE))

    data_dir = BASE_DIR / "data"
    configs_dir = BASE_DIR / "configs"

    # Créer un dossier temporaire avec les éléments à archiver
    tmp_dir = dest_dir / archive_name
    tmp_dir.mkdir(exist_ok=True)

    if DB_FILE.exists():
        shutil.copy2(DB_FILE, tmp_dir / DB_FILE.name)

    if configs_dir.exists():
        shutil.copytree(configs_dir, tmp_dir / "configs", dirs_exist_ok=True)

    if data_dir.exists():
        # Copier uniquement les fichiers de métadonnées et rapports (pas les gros CSV)
        for subdir in ["silver", "gold", "monitoring"]:
            src = data_dir / subdir
            if src.exists():
                shutil.copytree(src, tmp_dir / "data" / subdir, dirs_exist_ok=True)

    archive_path = shutil.make_archive(str(dest_dir / archive_name), "zip", tmp_dir)
    shutil.rmtree(tmp_dir)

    emit_alert("BACKUP", "INFO", f"Backup complet créé : {Path(archive_path).name}",
               {"size_bytes": Path(archive_path).stat().st_size})
    print(f"Backup complet : {archive_path}")
    return Path(archive_path)


def cleanup_old_backups() -> None:
    """Supprime les backups dépassant la rétention configurée."""
    now = datetime.now()

    partial_dir = BACKUP_DIR / "partial"
    full_dir = BACKUP_DIR / "full"

    removed = 0
    for directory, max_days in [(partial_dir, 7), (full_dir, 30)]:
        if not directory.exists():
            continue
        for f in directory.iterdir():
            if f.is_file():
                age = now - datetime.fromtimestamp(f.stat().st_mtime)
                if age > timedelta(days=max_days):
                    f.unlink()
                    removed += 1
                    print(f"  Supprimé (>{max_days}j) : {f.name}")

    emit_alert("BACKUP", "INFO", f"Nettoyage terminé : {removed} fichier(s) supprimé(s)")
    print(f"Nettoyage : {removed} ancien(s) backup(s) supprimé(s)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Backup PrevisionEnergie")
    parser.add_argument("--full", action="store_true", help="Backup complet (base + data + configs)")
    parser.add_argument("--cleanup", action="store_true", help="Nettoyer les anciens backups")
    args = parser.parse_args()

    if args.cleanup:
        cleanup_old_backups()
    elif args.full:
        backup_full()
    else:
        backup_partial()


if __name__ == "__main__":
    main()
