#! /usr/bin/env python3
import logging
from typing import Any, List

import uvicorn
from commonwealth.utils.apis import GenericErrorHandlingRoute, PrettyJSONResponse
from commonwealth.utils.logs import InterceptHandler, init_logger
from fastapi import FastAPI, status
from fastapi.responses import HTMLResponse
from fastapi_versioning import VersionedFastAPI, version
from loguru import logger

from bridget import BridgeSpec, Bridget

SERVICE_NAME = "bridget"

logging.basicConfig(handlers=[InterceptHandler()], level=0)
init_logger(SERVICE_NAME)

app = FastAPI(
    title="Bridget API",
    description="Bridget is a BlueOS service responsible for managing 'bridges' links.",
    default_response_class=PrettyJSONResponse,
)
app.router.route_class = GenericErrorHandlingRoute
logger.info("Starting Bridget!.")

controller = Bridget()


@app.get("/serial_ports", response_model=List[str])
@version(1, 0)
def get_serial_ports() -> Any:
    ports = controller.available_serial_ports()
    logger.debug(f"Available serial ports found: {ports}.")
    return ports


@app.get("/bridges", response_model=List[BridgeSpec])
@version(1, 0)
def get_bridges() -> Any:
    bridges = controller.get_bridges()
    logger.debug(bridges)
    return bridges


@app.post("/bridges", status_code=status.HTTP_201_CREATED)
@version(1, 0)
def add_bridge(bridge: BridgeSpec) -> Any:
    logger.debug(f"Adding bridge '{bridge}'.")
    controller.add_bridge(bridge)
    logger.debug(f"Bridge '{bridge}' added.")


@app.delete("/bridges", status_code=status.HTTP_200_OK)
@version(1, 0)
def remove_bridge(bridge: BridgeSpec) -> Any:
    logger.debug(f"Removing bridge '{bridge}'.")
    controller.remove_bridge(bridge)
    logger.debug(f"Bridge '{bridge}' removed.")


app = VersionedFastAPI(app, version="1.0.0", prefix_format="/v{major}.{minor}", enable_latest=True)


@app.get("/")
async def read_items() -> Any:
    html_content = """
    <html>
        <head>
            <title>Bridget</title>
        </head>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


if __name__ == "__main__":
    # Running uvicorn with log disabled so loguru can handle it
    uvicorn.run(app, host="0.0.0.0", port=27353, log_config=None)
