import requests


# proxies = {"https": "https://140.131.6.132:80", "https": "https://45.131.6.132:80"}

try:
    response = requests.get("https://ipinfo.io/json")
    print(response.text)
except requests.exceptions.ProxyError:
    print("Proxy Error: Could not connect to proxy.")
except requests.exceptions.SSLError:
    print("SSL Error: An SSL error occurred.")
except requests.exceptions.RequestException as e:
    print(f"Request Error: {e}")
