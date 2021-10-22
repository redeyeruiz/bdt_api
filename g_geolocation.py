import googlemaps
from datetime import datetime

gmaps = googlemaps.Client(key='AIzaSyD3M5wsiErV_l0bRONiWZrKS9XLEBnXAMY')

# Geocoding an address
geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# Look up an address with reverse geocoding
reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))


print(geocode_result)
#print(reverse_geocode_result)
