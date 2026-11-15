from config import ServerConfig
from pathlib import Path
from manager import ServerManager


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "server_config.json"

def main():
    config = ServerConfig.load_from_json(CONFIG_PATH)
    return ServerManager(config).run()


if __name__ == "__main__":
    main()