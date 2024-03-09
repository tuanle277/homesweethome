"""## Get news by location API

"""
from utils import *

def getNewsFromGeo(latitude, longtitude):
  url = "https://api.worldnewsapi.com/search-news"
  api_key = "8aa45a431f3841e08757574fbf2e02bb"

  news = []

  # Define the headers including the API key
  headers = {
      "Content-Type": "application/json",
      "api-key": api_key
  }

  location = f"{latitude}, {longtitude}, 100"
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

    # Process and print the response data
    # Example: print the first news article title (modify as needed based on actual response structure)
    if data.get("articles"):
      first_article = data["articles"][0]
      print("First article title:", first_article.get("title"))
  else:
    print(f"Failed to retrieve data, status code: {response.status_code}")
