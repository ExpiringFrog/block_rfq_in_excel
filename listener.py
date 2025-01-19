import json
import logging
import configparser

from containers import BlockRFQs
from excel import ExcelConnector
from telegram import send_block_rfq_event


class BlockRFQListener:
    def __init__(self, block_rfqs: BlockRFQs) -> None:

        self.block_rfqs = block_rfqs

        self.snapshot = False
        self.buffer = []

        config = configparser.ConfigParser()
        config.read("config.ini")
        self.excel_state = config.get("Excel", "state")
        if self.excel_state == "on":
            self.excel_connector = ExcelConnector()

        self.tg_state = config.get("Telegram", "state")

    def get_block_rfq_snapshot_request(self):
        msg = {
            "method": "private/get_block_rfqs",
            "params": {},
            "jsonrpc": "2.0",
            "id": 1,
        }
        return json.dumps(msg)

    def initial_callback(self, ws):
        msg = {
            "jsonrpc": "2.0",
            "method": "private/subscribe",
            "id": 111,
            "params": {"channels": ["block_rfq.maker.any"]},
        }
        ws.send(json.dumps(msg))

    def event_callback(self, ws, event):
        if event.get("id") == 111:
            ws.send(self.get_block_rfq_snapshot_request())
        if event.get("method") == "subscription" and event["params"].get(
            "channel"
        ).startswith("block_rfq.maker"):
            if not self.snapshot:
                self.buffer.append(event["params"]["data"])
                logging.info(f"Received RFQ event, no snapshot yet, buffering: {event}")
            else:
                self.block_rfqs.update_block_rfq_list_from_websocket_event(
                    ws, [event["params"]["data"]], reset=False
                )

                if self.excel_state == "on":
                    self.excel_connector.update_sheet(self.block_rfqs.block_rfq_dict)

                if self.tg_state == "on":
                    send_block_rfq_event(event["params"]["data"])

                logging.info(f"Received RFQ event: {event}")
        elif (
            isinstance(event.get("result"), dict)
            and event["result"].get("block_rfqs") is not None
        ):
            logging.info(f"Received RFQ snapshot: {event}")
            self.snapshot = True
            self.block_rfqs.update_block_rfq_list_from_websocket_event(
                ws, event["result"]["block_rfqs"], reset=True
            )
            if self.buffer:
                logging.debug(
                    f"Received RFQ snapshot, processing buffer: {self.buffer}"
                )
                self.block_rfqs.update_block_rfq_list_from_websocket_event(
                    ws, self.buffer, reset=False
                )
            if self.excel_state == "on":
                self.excel_connector.update_sheet(self.block_rfqs.block_rfq_dict)
        elif event.get("id") == 111:
            pass  # subscription ack
        else:
            logging.warning(f"Unhandled websocket msg: {event}")
