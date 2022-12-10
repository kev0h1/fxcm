class Data:
    def __init__(self, data) -> None:
        self.data = data

    def get_refined_data(self):
        """Refine the data that we get from FXCM"""
        data = self.data
        data.drop(
            ["bidopen", "bidclose", "bidhigh", "bidlow"], inplace=True, axis=1
        )
        data.rename(
            columns={
                "askopen": "open",
                "askclose": "close",
                "askhigh": "high",
                "asklow": "low",
                "tickqty": "volume",
            },
            inplace=True,
        )
        return data
