import re
import configparser
import pandas as pd
import diskcache as dc

from progress.bar import IncrementalBar
from streetaddress import StreetAddressParser
from concurrent.futures import ThreadPoolExecutor
from geopy.geocoders import GoogleV3, Nominatim

from definitions import CREDENTIALS, API_CACHE
from data_geocoders.api import GeoAPIWrapper


class PandasGeocoder:

    def __init__(self):
        self.running = False
        self.data = None
        self.address_columns = []
        self.street_address_parser = StreetAddressParser()
        self.progress_bar = None

        try:
            config = configparser.ConfigParser()
            config.read(CREDENTIALS)
            self.geo_coder_apis = [GeoAPIWrapper(GoogleV3, user_agent="google_locator",
                                                 api_key=config["Google"]["api_token"]),
                                   GeoAPIWrapper(Nominatim, user_agent="nominatim_locator")]
        except Exception:
            self.geo_coder_apis = [GeoAPIWrapper(Nominatim, user_agent="nominatim_locator")]

        self.geocode_cache = {}
        self.processed_items, self.found = 0, 0

    def write_cache(self):
        disc_cache = dc.Cache(API_CACHE)
        for address, geo_data in self.geocode_cache.items():
            disc_cache[address] = geo_data

    def read_cache(self):
        disc_cache = dc.Cache(API_CACHE)
        for key in disc_cache.iterkeys():
            self.geocode_cache[key] = disc_cache[key]

    def run(self, data: pd.DataFrame, address_columns: list) -> pd.DataFrame:
        self.running = True
        self.data = data.fillna("")
        self.address_columns = address_columns
        self.processed_items, self.found = 0, 0
        if len(self.geocode_cache) == 0:
            self.read_cache()

        try:
            self.progress_bar = IncrementalBar(name="geocoding progress", max=len(self.data.index))
            with ThreadPoolExecutor() as pool:
                self.data['result'] = \
                    list(pool.map(self.get_coordinates_args, self.data.loc[:, self.address_columns].to_numpy(),
                                  chunksize=10))
        finally:
            self.progress_bar.finish()

            if len(self.geocode_cache) > 0:
                self.write_cache()
            self.running = False

        return self.data

    def is_running(self):
        return self.running

    def get_status(self):
        return {
            'in_progress': self.running,
            'processed_items': self.processed_items,
            'total_items': len(self.data.index) if self.data is not None else 'Unknown',
            'api_found_items': self.found,
        }

    def get_coordinates_args(self, address_row) -> [float, float]:
        arr = [str(addr_unit).strip().lower() for addr_unit in address_row if len(str(addr_unit)) > 0]
        address_string = re.sub(r'[@():{}]', "", ",".join(arr))
        result = self.street_address_parser.parse(address_string)
        search_address = result.get("street_name") or address_string
        longitude, latitude = None, None

        if address_string in self.geocode_cache or search_address in self.geocode_cache:
            longitude, latitude = self.geocode_cache.get(address_string) or self.geocode_cache.get(search_address)
        else:
            for geo_coder_api in self.geo_coder_apis:
                longitude, latitude = geo_coder_api.get_lon_lat(search_address, address_string)
                if longitude is not None and latitude is not None:
                    self.found += 1
                    break
            self.geocode_cache[search_address] = self.geocode_cache[address_string] = longitude, latitude

        self.progress_bar.next()
        self.processed_items += 1

        return longitude, latitude
