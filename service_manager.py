import requests

class MCPClient:
    def __init__(self, url, creds):
        self.url = url
        self.auth = creds

    def send_message(self, to, text):
        response = requests.post(f"{self.url}/send", headers=self.auth, json={"to": to, "message": text})
        return response.json()

    def search_files(self, query):
        response = requests.get(f"{self.url}/search", headers=self.auth, params={"q": query})
        return response.json()

    def create_calendar_event(self, details):
        response = requests.post(f"{self.url}/calendar", headers=self.auth, json=details)
        return response.json()

    def send_email(self, to, subject, body):
        response = requests.post(f"{self.url}/email", headers=self.auth, json={"to": to, "subject": subject, "body": body})
        return response.json()

class MCPManager:
    def __init__(self):
        self.servers = {}

    def connect_server(self, name, url, auth):
        try:
            self.servers[name] = MCPClient(url, auth)
            return True
        except:
            return False

    def get_server(self, name):
        return self.servers.get(name)