import time
from fastapi import FastAPI
import contextlib
import time
import threading
import uvicorn

probe_server = FastAPI()


class ProbeServer(uvicorn.Server):
    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started and thread.is_alive():
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()


def get_probe_server(port: int, log_level: str = "info") -> uvicorn.Server:
    config = uvicorn.Config(
        probe_server,
        port=port,
        log_level=log_level,
    )
    return ProbeServer(config)


@probe_server.get("/healthz")
async def healthiness() -> bool:
    return True


@probe_server.get("/readyz")
async def readiness() -> bool:
    return True
