import os
from dotenv import load_dotenv

load_dotenv()

# Dinodial Proxy API Configuration
DINODIAL_PROXY_BASE = "https://api-dinodial-proxy.cyces.co/api/proxy"
DINODIAL_PROXY_BEARER_TOKEN = os.getenv("DINODIAL_PROXY_BEARER_TOKEN", "")

# Restaurant Configuration
RESTAURANT_NAME = "Dino Restaurant"

