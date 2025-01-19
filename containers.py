import logging


class Leg:
    def __init__(self, instrument_name, ratio) -> None:
        self.instrument_name = instrument_name
        self.ratio = ratio


class Legs:
    def __init__(self) -> None:
        self.legs = []

    def add_leg(self, instrument_name: str, ratio: int):
        self.legs.append(Leg(instrument_name, ratio))


class Hedge:
    def __init__(self, instrument_name, amount, price) -> None:
        self.instrument_name = instrument_name
        self.amount = amount
        self.price = price


class BlockRFQ:
    def __init__(
        self, rfq_id: int, name: str, legs: Legs, amount: float, hedge: Hedge
    ) -> None:
        self.id = rfq_id
        self.name = name
        self.legs = legs
        self.amount = amount
        self.hedge = hedge


class BlockRFQs:
    def __init__(self) -> None:
        self.block_rfq_dict = {}

    def update_block_rfq_list_from_websocket_event(self, ws, block_rfqs, reset=False):
        logging.debug(f"Received Block RFQ event: {block_rfqs}")
        if reset:
            self.block_rfq_dict = {}
        for rfq in block_rfqs:

            if rfq["role"] != "maker":
                logging.info(f"Not a maker, ignoring: {rfq}")
                continue

            if rfq["state"] != "open":
                if rfq["block_rfq_id"] in self.block_rfq_dict.keys():
                    logging.info(
                        f'RFQ no longer open, deleting: {self.block_rfq_dict[rfq["block_rfq_id"]]}'
                    )
                    del self.block_rfq_dict[rfq["block_rfq_id"]]

            else:
                legs = Legs()
                hedge = None
                for leg in rfq["legs"]:
                    legs.add_leg(
                        leg["instrument_name"],
                        (leg["ratio"] if leg["direction"] == "buy" else -leg["ratio"]),
                    )
                if "hedge" in rfq.keys():
                    hedge = Hedge(
                        rfq["hedge"]["instrument_name"],
                        (
                            rfq["hedge"]["amount"]
                            if rfq["hedge"]["direction"] == "buy"
                            else -rfq["hedge"]["amount"]
                        ),
                        rfq["hedge"]["price"],
                    )
                block_rfq = BlockRFQ(
                    rfq_id=rfq["block_rfq_id"],
                    name=rfq["combo_id"],
                    legs=legs,
                    amount=rfq["amount"],
                    hedge=hedge,
                )
                self.block_rfq_dict[block_rfq.id] = block_rfq
