import os

api_headers = {
    "Accept": "application/json",
    "Authorization": f"Basic {os.getenv('API_TOKEN')}",
}
