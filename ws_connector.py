import json
import configparser
import logging

import websocket


class WebsocketConnector:
    def __init__(self, initial_callback, event_callback) -> None:

        config = configparser.ConfigParser()
        config.read("config.ini")
        self.api_key = config.get("API", "key")
        self.api_secret = config.get("API", "secret")
        self.environment = config.get("API", "environment")

        print(self.environment)

        if self.environment == "test":
            url = "wss://test.deribit.com/ws/api/v2"
        else:
            url = "wss://www.deribit.com/ws/api/v2"

        self.wsapp = websocket.WebSocketApp(
            url=url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_pong=self.on_pong,
            on_close=self.on_close,
            on_error=self.on_error,
        )

        self.initial_callback = initial_callback
        self.event_callback = event_callback

    def on_open(self, wsapp):
        logging.debug("Connection established.")
        self.set_heartbeat()
        self.authenticate()

    def set_heartbeat(self):
        msg = {
            "method": "public/set_heartbeat",
            "params": {"interval": 60},
            "jsonrpc": "2.0",
            "id": 1,
        }
        logging.debug(f"Setting hearbeat: {msg}")
        self.wsapp.send(json.dumps(msg))

    def send_heartbeat(self):
        msg = {"method": "public/test", "params": {}, "jsonrpc": "2.0", "id": 3}
        logging.debug(f"Sending heartbeat: {msg}")
        self.wsapp.send(json.dumps(msg))

    def authenticate(self):
        msg = {
            "id": 2,
            "method": "public/auth",
            "params": {
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.api_secret,
            },
            "jsonrpc": "2.0",
        }
        logging.debug(f"Sending authentication msg: {msg}")
        self.wsapp.send(json.dumps(msg))

    def on_message(self, ws, message):
        message = json.loads(message)

        if message.get("method") == "heartbeat":
            self.send_heartbeat()
        elif message.get("result") == "ok":
            logging.debug(f"Heartbeat set: {message}")
        elif (
            isinstance(message.get("result"), dict)
            and message["result"].get("token_type") is not None
        ):
            logging.debug("Successfully authenticated: {message}")
            self.initial_callback(ws)
        elif message.get("error") is not None:
            logging.error(f"Server error: {message}")
        elif (
            isinstance(message.get("result"), dict)
            and message["result"].get("version") is not None
        ):
            pass  # this is a response to a heartbeat, we can safely ignore
        else:
            self.event_callback(ws, message)

    def on_pong(self, wsapp, message):
        logging.debug(f"Received pong: {message}")

    def on_close(self, wsapp, close_status_code, close_msg):
        logging.error(
            f"Connection closed, status: {close_status_code}, message: {close_msg}"
        )

    def on_error(self, wsapp, error):
        logging.error(f"Application error: {error}")
        raise Exception(f"{error}")

    def start(self):
        self.wsapp.run_forever()
