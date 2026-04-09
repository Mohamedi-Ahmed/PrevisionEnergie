from _bootstrap import bootstrap_project_root

bootstrap_project_root()

from app.core.logger import setup_logging
from app.db.loaders.gold_loader import SilverToGoldLoader


def main() -> None:
    setup_logging()
    loader = SilverToGoldLoader()
    result = loader.run()
    print(result)


if __name__ == "__main__":
    main()
