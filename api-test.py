import os
from dotenv import load_dotenv
from binance.client import Client

load_dotenv()

KEY = os.getenv('BINANCE_KEY')
SECRET = os.getenv('BINANCE_SECRET')
TESTNET = os.getenv('TESTNET')

client = Client(KEY, SECRET, testnet=TESTNET)
info = client.get_exchange_info()

print(info['symbols'])