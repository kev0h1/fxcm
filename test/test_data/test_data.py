import os

file = os.path.abspath(os.curdir) + "/test/data.csv"
import mock
import pandas as pd
from src.data.data import Data


class TestData:
    def test_get_refined_data_columns(self):
        columns = ["open", "close", "high", "low", "volume"]
        data = pd.read_csv(file)
        data_obj = Data(data)
        refined_data = data_obj.get_refined_data()
        for col in columns:
            assert col in refined_data

    def test_get_refined_data_column_count(self):
        """test get the refined data"""
        data = pd.read_csv(file)
        data_obj = Data(data)
        refined_data = data_obj.get_refined_data()
        assert len(refined_data.columns) == 6
