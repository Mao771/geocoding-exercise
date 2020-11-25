import pandas as pd
import uuid
import os
from definitions import CSV_DIRECTORY
from data_geocoders import PandasGeocoder


if __name__ == '__main__':
    data = pd.read_csv(os.path.join(CSV_DIRECTORY, 'filename.csv'), delimiter=';')
    columns = ['address_1', 'address_2', 'address_3', 'postcode']
    pg = PandasGeocoder()
    result = pg.run(data, columns)
    result.to_csv(os.path.join(CSV_DIRECTORY, f"{uuid.uuid4()}.csv"))
