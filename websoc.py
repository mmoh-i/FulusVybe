import websocket
import json

def on_message(ws, message):
    print(f"Received: {message}")
    try:
        data = json.loads(message)
        print(f"Parsed: {json.dumps(data, indent=2)}")
    except json.JSONDecodeError:
        print("Invalid JSON")

def on_error(ws, error):
    print(f"Error: {error}")

def on_open(ws):
    print("Connected")
    config = {
        "type": "configure",
        "filters": {
            "trades": True,
            "transfers": True
        }
    }
    ws.send(json.dumps(config))
    print(f"Sent: {config}")

ws = websocket.WebSocketApp(
    "wss://api.vybenetwork.xyz/live",
    header={"x-api-key": "snCvzWk4C9f7Wfim8zwqhMvPLSXGbvwXbHQefLpagiKcsX8E"},
    on_open=on_open,
    on_message=on_message,
    on_error=on_error
)
ws.run_forever()