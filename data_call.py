from setup import *

# get response from api, parse it, then input into excel
def parse_response(place):
  response = api_call_from_place(place)
  home_data = []

  print(response.keys())
  # Check if 'data' and 'homes' keys exist in the data
  if 'data' in response and response["data"] != None and 'homes' in response['data']:
      homes = response['data']['homes']
      home_data = []
      for home in homes:
        home_details = {
              'MLS ID': home.get('mlsId', {}).get('value', 'N/A'),
              'Address': home.get('streetLine', {}).get('value', 'No address provided'),
              'City': home.get('city', 'No city provided'),
              'Postal Code': home.get('postalCode', {}).get('value', 'No postal code provided'),
              'Price': home.get('price', {}).get('value', 'No price provided'),
              'Beds': home.get('beds', 'No beds info'),
              'Baths': home.get('baths', 'No baths info'),
              'Square Feet': home.get('sqFt', {}).get('value', 'No sq ft provided'),
              'Has 3D Tour': home.get('has3DTour', 'N/A'),
              'Has Video Tour': home.get('hasVideoTour', 'N/A'),
              'Is New Construction': home.get('isNewConstruction', 'N/A'),
              'HOA Fee': home.get('hoa', {}).get('value', 'No HOA fee'),
              'Year Built':home.get('yearBuilt', {}).get('value', 'Year built not provided'),
              'url':'https://www.redfin.com' + home.get('url', 'URL not provided'),
              'Open House Event Name': home.get('openHouseEventName', 'N/A'),
              'Open House Start': home.get('openHouseStartFormatted', 'N/A'),
              'Original Time on Redfin': home.get('originalTimeOnRedfin', {}).get('value', 'N/A'),
              'Partial Baths': home.get('partialBaths', 'N/A'),
              'Listing Agent': home.get('listingAgent', {}).get('name', 'N/A'),
              'Listing Remarks': home.get('listingRemarks', 'N/A'),
              'Location': home.get('location', {}).get('value', 'N/A'),
              'latitude': home.get('latLong', {}).get('value', {}).get('latitude', 'N/A'),
              'longitude': home.get('latLong', {}).get('value', {}).get('longitude', 'N/A')
          }

        home_data.append(home_details)
        # Now print the information from the dictionary
        print("Listing Information:")
        for key, value in home_details.items():
            print(f"{key}: {value}")
        print("-" * 60)  # Separator for readability

      # for i in range(len(home_data)):
      #   row = [home_data[i].get(header, 'N/A') for header in headers]
      input_report_to_sheet(home_data, place)
      for home in home_data[:1]:
        getNewsFromGeo(home["latitude"], home["longitude"])
  else:
      print("No homes data found")

# place = input("Input the name of a place (country, county,...): ")
# parse_response(place)
places = ["Tracy", "Austin", "San Jose", "Livermore", "San Lorenzo", "San Francisco", "Greencastle"]
for place in places:
  parse_response(place)
