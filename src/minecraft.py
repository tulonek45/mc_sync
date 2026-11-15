import os
import subprocess
import sys
import threading

from errors import ConfigurationError


class MinecraftServer:
    def __init__(self, config):
        self.config = config
        self.java = str(self.config.jre_path)
        self.process = None
        self.input_lock = threading.Lock()
        self.saved_event = threading.Event()


    def start(self):
        jar = self.config.server_path / self.config.jar_name
        if not jar.is_file():
            raise ConfigurationError("Server jar file not found.")

        command = [
            self.java, 
            f"-Xms{self.config.min_ram}", 
            f"-Xmx{self.config.max_ram}",
            *self.config.jvm_args,
            "-jar",
            self.config.jar_name,
            *self.config.server_args
        ]

        environment = os.environ.copy()

        self.process = subprocess.Popen(
            command,
            cwd=self.config.server_path,
            env=environment,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )

        threading.Thread(target=self._read_output, daemon=True).start()
        threading.Thread(target=self._forward_console_input, daemon=True).start()
        print("Minecraft server started.")


    def _read_output(self):
        for line in self.process.stdout:
            print(line, end="")
            lowered_line = line.lower()
            if "saved the game" in lowered_line or "changes to the world were saved" in lowered_line:
                self.saved_event.set()


    def _forward_console_input(self):
        for line in sys.stdin:
            if self.process and self.process.poll() is None:
                command = line.rstrip("\r\n")
                self.send_console(command)


    def send_console(self, command):
        if not self.process or self.process.poll() is not None:
            return
        with self.input_lock:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()


    def flush_world(self):
        if not self.process or self.process.poll() is not None:
            raise RuntimeError("Cannot flush the world because Minecraft is not running.")
        self.saved_event.clear()
        self.send_console("save-all flush")
        if not self.saved_event.wait(timeout=self.config.save_timeout_s):
            raise RuntimeError("Timed out waiting for Minecraft to flush the world save.")


    def stop(self):
        if not self.process or self.process.poll() is not None:
            return True
        self.flush_world()
        self.send_console("stop")
        while self.process.poll() is None:
            try:
                self.process.wait(timeout=self.config.stop_timeout_s)
            except subprocess.TimeoutExpired:
                print("WARNING: Minecraft did not stop gracefully; terminating it.", file=sys.stderr)
                self.process.terminate()

        return self.process.poll() is not None
