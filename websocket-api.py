import json
import websockets

uri = 'wss://testnet.binance.vision/ws'

async def main():
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "method": "SUBSCRIBE",
            "params": ['bnbbtc@kline_1m'],
            "id": 1
        }))

        while True:
            response = await websocket.recv()
            print(response)

if __name__ == '__main__':
    import asyncio
    asyncio.get_event_loop().run_until_complete(main())