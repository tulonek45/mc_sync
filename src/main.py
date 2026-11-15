from config import ServerConfig
from pathlib import Path

if __name__ == "__main__":
    config = ServerConfig.load_from_json(Path("server_config.json"))
    print(config)