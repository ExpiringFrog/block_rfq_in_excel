import time
import logging

from ws_connector import WebsocketConnector
from containers import *
from listener import BlockRFQListener

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)


if __name__ == "__main__":
    block_rfqs = BlockRFQs()

    rfq_listener = BlockRFQListener(block_rfqs)

    wsapp = WebsocketConnector(
        initial_callback=rfq_listener.initial_callback,
        event_callback=rfq_listener.event_callback,
    )

    while True:
        try:
            logging.warning("Starting application...")
            wsapp.start()
            logging.warning("Connection ended, waiting 5 seconds and restarting...")
            time.sleep(5)
        except KeyboardInterrupt:
            exit()
