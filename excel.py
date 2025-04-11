import logging
import configparser
import json

import xlwings as xw
import pandas as pd


class ExcelConnector:
    def __init__(self) -> None:

        config = configparser.ConfigParser()
        config.read("config.ini")
        file_path = config.get("Excel", "file_path")
        sheet_name = config.get("Excel", "sheet_name")
        self.currency_filter = json.loads(config.get("Filters", "currencies"))

        self.sheet_conn = xw.Book(file_path).sheets[sheet_name]
        self.clean_sheet()
        self.set_headers()

    def set_sheet_to_df(self, coord: str, df: pd.DataFrame):
        self.sheet_conn.range(coord).value = df

    def clean_sheet(self):
        self.sheet_conn.clear_contents()

    def clean_range(self, range):
        self.sheet_conn.range(range).clear_contents()

    def set_headers(self):
        df = pd.DataFrame(
            columns=[
                "RFQID",
                "LongName",
                "RFQSize",
                "HedgeLeg",
                "HedgeLevel",
                "nHedgeLeg",
                "Leg1",
                "nLeg1",
            ]
        )
        self.set_sheet_to_df("A1", df)

    def update_sheet(self, block_rfq_dict):

        block_rfq_dict_list = []

        for block_rfq in block_rfq_dict.values():
            filtered = False
            entry = {
                "RfqID": block_rfq.id,
                "LongName": block_rfq.name,
                "RFQSize": block_rfq.amount,
                "HedgeLeg": None,
                "HedgeLevel": None,
                "nHedgeLeg": None,
            }
            i = 1
            for leg in block_rfq.legs.legs:
                if not leg.instrument_name.startswith(tuple(self.currency_filter)):
                    filtered = True
                entry[f"Leg{i}"] = leg.instrument_name
                entry[f"nLeg{i}"] = leg.ratio
                i += 1
            if block_rfq.hedge:
                entry["HedgeLeg"] = block_rfq.hedge.instrument_name
                entry["HedgeLevel"] = block_rfq.hedge.price
                entry["nHedgeLeg"] = block_rfq.hedge.amount

            if not filtered:
                block_rfq_dict_list.append(entry)

        df = pd.DataFrame(block_rfq_dict_list)
        if not df.empty:
            df.sort_values(by="RfqID", axis=0, ascending=False, inplace=True)
            self.clean_range("A2:Z1000")
            self.set_sheet_to_df("A1", df)
        else:
            self.clean_range("A2:Z1000")
            logging.debug("RFQ list empty, cleaning Excel file.")
