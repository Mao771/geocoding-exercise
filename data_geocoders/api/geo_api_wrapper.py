from typing import Type

from geopy.geocoders.base import Geocoder
from geopy.extra.rate_limiter import RateLimiter


class GeoAPIWrapper:

    def __init__(self, geo_coder: Type[Geocoder], **locator_kwargs):
        self.geo_locator = geo_coder(**locator_kwargs)

    def get_lon_lat(self, *queries):
        for query in queries:
            rate_limited = RateLimiter(self.geo_locator.geocode, min_delay_seconds=2)
            location = rate_limited(query=query)
            if location:
                return location.longitude, location.latitude
        return None, None
