"""## Get news by location API

"""
from utils import *

def getNewsFromGeo(latitude, longitude):
  url = "https://api.worldnewsapi.com/search-news"
  api_key = "5f71a7bdf2b3400bb1cf5fccb0eff920"

  news = []

  # Define the headers including the API key
  headers = {
      "Content-Type": "application/json",
      "x-api-key": api_key
  }

  print(f"Latitude {latitude}, longitude {longitude}")
  location = f"{latitude}, {longitude}, 10"
  params = {
      "location-filter": location
  }

  response = requests.get(url, headers=headers, params=params)

  # Check if the request was successful
  if response.status_code == 200:
    # Parse the JSON response
    data = response.json()

    # Print the number of points left today from headers
    print("API Quota Left:", response.headers.get('X-API-Quota-Left', 'Unknown'))

    if type(data["news"]) == list:
      print(f"There are {len(data["news"])} news")
    # Process and print the response data
    # Example: print the first news article title (modify as needed based on actual response structure)
    if data.get("news"):
      first_article = data["news"][0]
      print(first_article.keys())
      print("First article title:", first_article.get("title"))
      # print("First article text:", first_article.get("text"))
  else:
    print(f"Failed to retrieve data, status code: {response.status_code}")

import requests

url = "https://jgentes-crime-data-v1.p.rapidapi.com/crime"

querystring = {"startdate":"9/19/2023","enddate":"9/25/2023","long":"-122.5076392","lat":"37.757815"}

headers = {
	"X-RapidAPI-Key": "8d1cc6a7femshfdb11fea2f24219p11bce0jsn4f7e403da7f9",
	"X-RapidAPI-Host": "jgentes-Crime-Data-v1.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)
print(response)
print("Test response", response.json())
