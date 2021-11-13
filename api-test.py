import json
import pprint
import websockets
import asyncio


uri = 'wss://testnet.binance.vision/ws'

def handle_kline(kline):
    pprint.pprint(kline['k'])

async def main():
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            'method': 'SUBSCRIBE',
            'params': ['btcusdt@kline_1m'],
            'id': 1
        }))

        while True:
            kline = await websocket.recv()
            if 'result' not in kline:
                handle_kline(json.loads(kline))

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())