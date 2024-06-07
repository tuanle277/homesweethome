import requests

class APIClient:
    def __init__(self, base_url, headers=None):
        """
        Initialize the API client with a base URL and optional headers.
        """
        self.base_url = base_url
        self.headers = headers or {}

    def set_headers(self, headers):
        """
        Set or update the headers for the API client.
        """
        self.headers.update(headers)

    def fetch(self, endpoint, params=None):
        """
        Fetch data from a specific endpoint using a GET request.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def post(self, endpoint, data=None):
        """
        Send data to a specific endpoint using a POST request.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def put(self, endpoint, data=None):
        """
        Send data to a specific endpoint using a PUT request.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def delete(self, endpoint):
        """
        Delete a resource at a specific endpoint using a DELETE request.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None

# Example usage:
if __name__ == "__main__":

    url = "https://crime-data-by-zipcode-api.p.rapidapi.com/crime_data"

    querystring = {"zip":"94109"}

    headers = {
        "X-RapidApi-Key": "97864f99e8mshc4d76b0890e4c8ap172bfejsn7261f7d688b8",
        "X-RapidApi-Host": "crime-data-by-zipcode-api.p.rapidapi.com"
    }

    # Initialize the API client
    api_client = APIClient(base_url=url, headers=headers)

    response = api_client.fetch("", params=querystring)
    print(response)
