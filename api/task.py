import os
import pandas as pd
from definitions import CSV_DIRECTORY
from data_geocoders import PandasGeocoder


class GeocodeTask:

    def __init__(self):
        self.pandas_geocoder = PandasGeocoder()
        self.results = {}
        self.current_task_id = None

    def run(self, data: pd.DataFrame, address_columns: list, task_id):
        self.current_task_id = str(task_id)
        self.results[self.current_task_id] = {
            'geocoder_status': self.pandas_geocoder.get_status()
        }
        result_df = self.pandas_geocoder.run(data, address_columns)
        result_path = os.path.join(CSV_DIRECTORY, f"{task_id}.csv")
        result_df.to_csv(result_path)
        self.results[self.current_task_id]['file_path'] = result_path
        self._update_current_status()

    def in_progress(self):
        return self.pandas_geocoder.is_running()

    def stats(self):
        self._update_current_status()
        return self.results

    def task_status(self, task_id):
        self._update_current_status()
        if task_id in self.results:
            return self.results[task_id]
        else:
            raise ValueError(f"Task with id {task_id} is not found.")

    def _update_current_status(self):
        if self.current_task_id in self.results:
            self.results[self.current_task_id]['geocoder_status'] = self.pandas_geocoder.get_status()
