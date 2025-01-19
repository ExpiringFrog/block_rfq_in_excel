import configparser
import logging

import requests


def send_message(text):
    config = configparser.ConfigParser()
    config.read("config.ini")
    bot_token = config.get("Telegram", "bot_token")
    chat_id = config.get("Telegram", "chat_id")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    try:
        resp = requests.post(url, params=params, timeout=5)
    except Exception as e:
        logging.warning(
            f"Received error {e}, could not send message to Telegram: {text}"
        )


def send_block_rfq_event(rfq):
    message = f"RFQ ID: {rfq['block_rfq_id']}\nStrategy: {rfq['combo_id']}\nQuantity: {rfq['amount']}x\n\nRole: {rfq['role']}\nRating: {rfq['taker_rating']if 'taker_rating' in rfq.keys() else 'N.A.'}\n\nState: {rfq['state']}"
    send_message(message)


if __name__ == "__main__":
    message = """
    RFQ ID: 1234\nStrategy: BTC-ICOND-20JAN25-101500_103000_105000_107500\nQuantity: 45x\n\nRole: Maker\nRating: 0.12\n\nState: Open
    """
    send_message(message)
