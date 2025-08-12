import requests

class clickmassa_handler:
  def __init__(self):
    self.url = "https://enterprise-47api.clickmassa.com.br/v1/"

  def load(self, token: str, id: str):
    self.headers = {
        "Authorization": f"Bearer {token}"
    }
    self.token = token
    self.id = id

  def fetch_users(self):
    url = f"{self.url}users/{self.id}/?token={self.token}"
    response = requests.get(url, headers=self.headers)
    return response.json()

    
  

handler = clickmassa_handler()