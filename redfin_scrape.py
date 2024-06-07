# -*- coding: utf-8 -*-
"""RedFin scrape.py

Original file is located at
    https://colab.research.google.com/drive/1o0YcEZLkJqr95ijxWjwM5gzRNbY8snpH
"""

# !pip install gspread oauth2client requests transformers google
import requests

def api_call_from_place(place):
  url = "https://redfin-com-data.p.rapidapi.com/property/search"

  querystring = {"location": place, "search_by":"places"}

  headers = {
    "X-RapidAPI-Key": "8d1cc6a7femshfdb11fea2f24219p11bce0jsn4f7e403da7f9",
    "X-RapidAPI-Host": "redfin-com-data.p.rapidapi.com"
  }

  response = requests.get(url, headers=headers, params=querystring)

  return response.json()


"""## Retrieving more location information from address"""

def get_location_details(address, api_key):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"

    params = {
        "address": address,
        "key": api_key
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            results = data['results'][0]
            location_details = {}
            for component in results['address_components']:
                types = component['types']
                if 'locality' in types:
                    location_details['city'] = component['long_name']
                elif 'administrative_area_level_1' in types:
                    location_details['state'] = component['long_name']
                elif 'neighborhood' in types:
                    location_details['neighborhood'] = component['long_name']

            return location_details
        else:
            return {"error": "No results found"}
    else:
        return {"error": "Failed to connect to the API"}
