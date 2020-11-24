import os
import pandas as pd

from definitions import SAMPLE_CSV_RESULT
from data_geocoders import PandasGeocoder


if __name__ == '__main__':
    data = pd.read_csv('../NW6 Data.csv', delimiter=';')
    columns = ['address_1', 'address_2', 'address_3', 'postcode']
    pg = PandasGeocoder(data, columns)
    result = pg.run()
    result.to_csv(os.path.join(SAMPLE_CSV_RESULT))
