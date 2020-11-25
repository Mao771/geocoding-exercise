import os
import uuid
import pandas as pd
from definitions import CSV_DIRECTORY
from data_geocoders import PandasGeocoder


class GeocodeTask:

    def __init__(self):
        self.pandas_geocoder = PandasGeocoder()
        self.results = {}

    def run(self, data: pd.DataFrame, address_columns: list, task_id):
        self.results[task_id] = {
            'geocoder': self.pandas_geocoder
        }
        result_df = self.pandas_geocoder.run(data, address_columns)
        result_path = os.path.join(CSV_DIRECTORY, f"{task_id}.csv")
        result_df.to_csv(result_path)
        self.results[task_id]['file_path'] = result_path

    def in_progress(self):
        for task_id in self.results:
            if self.results[task_id]['geocoder'].is_running():
                return True
        return False

    def task_status(self, task_id):
        if task_id in self.results:
            return {
                "geocoder_status": self.results[task_id]['geocoder'].get_status(),
                "filepath": self.results[task_id]['file_path']
            }
        else:
            return {
                'error': f"Task with id {task_id} is not found."
            }
