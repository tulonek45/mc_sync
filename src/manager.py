from minecraft import MinecraftServer

class ServerManager:
    def __init__(self, config):
        self.config = config
        self.minecraft = MinecraftServer(self.config)

    def run(self):
        try:
            self.minecraft.start()
            if self.minecraft.process:
                self.minecraft.process.wait()       
        finally:
            process = self.minecraft.process
            if process is not None and process.poll() is None:
                self.minecraft.stop()

        returncode = 0 if self.minecraft.process and self.minecraft.process.returncode == 0 else 1  
        
        return returncode