import pandas as pd
import diskcache as dc
import re
import configparser

from progress.bar import IncrementalBar
from streetaddress import StreetAddressParser
from address_parser import Parser
from concurrent.futures import ThreadPoolExecutor
from geopy.geocoders import GoogleV3, Nominatim

from definitions import CREDENTIALS, API_CACHE
from data_geocoders.api import GeoAPIWrapper


class PandasGeocoder:

    def __init__(self, data: pd.DataFrame, address_columns: list):
        config = configparser.ConfigParser()
        config.read(CREDENTIALS)

        self.data = data
        self.address_columns = address_columns
        self.address_parser = Parser()
        self.street_address_parser = StreetAddressParser()
        self.progress_bar = IncrementalBar('PandasGeocoder', max=len(self.data.index))
        self.geo_coder_apis = [GeoAPIWrapper(GoogleV3, user_agent="google_locator",
                                             api_key=config["Google"]["api_token"])]

        self.geocode_cache = {}
        self.processed_items, self.found, self.not_found = 0, 0, 0

    def reset(self):
        self.geocode_cache = {}
        self.processed_items, self.found, self.not_found = 0, 0, 0

    def save_cache(self):
        disc_cache = dc.Cache(API_CACHE)
        for address, geo_data in self.geocode_cache.items():
            disc_cache[address] = geo_data

    def read_cache(self):
        disc_cache = dc.Cache(API_CACHE)
        for key in disc_cache.iterkeys():
            self.geocode_cache[key] = disc_cache[key]

    def run(self) -> pd.DataFrame:
        if len(self.geocode_cache) == 0:
            self.read_cache()

        with ThreadPoolExecutor() as pool:
            self.data['result'] = \
                list(pool.map(self.get_coordinates_args, self.data.fillna("").loc[:, self.address_columns].to_numpy(),
                              chunksize=10))

        self.progress_bar.finish()
        if len(self.geocode_cache) > 0:
            self.save_cache()

        return self.data

    def get_status(self):
        return {
            'processed_items': self.processed_items,
            'total_items': len(self.data.index),
            'found_items': self.found,
            'not_found_items': self.not_found
        }

    def get_coordinates_args(self, address_row) -> [float, float]:
        arr = [str(addr_unit).strip().lower() for addr_unit in address_row if len(str(addr_unit)) > 0]
        address_string = re.sub(r'[@():{\}]', "", ",".join(arr))
        result = self.street_address_parser.parse(address_string)
        search_address = result["street_name"] or address_string
        longitude, latitude = None, None

        if address_string in self.geocode_cache or search_address in self.geocode_cache:
            longitude, latitude = self.geocode_cache.get(address_string) or self.geocode_cache.get(search_address)
        else:
            for geo_coder_api in self.geo_coder_apis:
                longitude, latitude = geo_coder_api.get_lon_lat(search_address, address_string)
                if longitude is not None and latitude is not None:
                    break
            self.geocode_cache[search_address] = self.geocode_cache[address_string] = longitude, latitude
        self.progress_bar.next()
        return longitude, latitude