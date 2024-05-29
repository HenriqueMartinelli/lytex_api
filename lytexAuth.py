import requests
import json

class LyTexAuth:
    def __init__(self):
        with open("config.json", "r") as f:
            self.config = json.load(f)
        self.client_id = self.config["clientId"]
        self.client_secret = self.config["clientSecret"]

    def obtain_token(self):
        auth_url = "https://auth-pay.lytex.com.br/v1/oauth/obtain_token"
        payload = {
            "grantType": "clientCredentials",
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        }

        response = requests.request("POST", auth_url, json=payload)
        response.raise_for_status()
        response_data = response.json()
        response_data.update({"clientSecret":self.client_secret, "clientId": self.client_id })
        return response_data

    def update_config(self, new_config):
        with open("config.json", "w") as f:
            json.dump(new_config, f, indent=4)

if __name__ == "__main__":
    auth = LyTexAuth()
    new_config = auth.obtain_token()
    auth.update_config(new_config)