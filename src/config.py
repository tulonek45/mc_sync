import json
from dataclasses import dataclass, field, fields
from pathlib import Path
import os


def expand_path(value):
    s = os.path.expandvars(str(value))
    return Path(s).expanduser().resolve()


@dataclass
class ServerConfig:
    server_path: Path = Path("server")
    jar_name: str = "server.jar"
    world_name: str = "world"
    jre_path: Path | None = None

    min_ram: str = "2G"
    max_ram: str = "4G"
    jvm_args: list[str] = field(default_factory=list)
    server_args: list[str] = field(default_factory=lambda: ["nogui"])

    save_timeout_s: int = 120
    stop_timeout_s: int = 120


    def __post_init__(self):
        self.server_path = expand_path(self.server_path)
        if self.jre_path is not None:
            self.jre_path = expand_path(self.jre_path)


    @classmethod
    def load_from_json(cls, path):
        if not path.exists():
            cfg = cls()
            cfg.save(path)
            return cfg
        data = json.loads(path.read_text(encoding="utf-8"))
        known = {f.name for f in fields(cls)}
        data = {k: v for k, v in data.items() if k in known} 
        cfg = cls(**data)
        cfg.validate()
        return cfg



    def validate(self):
        pass
