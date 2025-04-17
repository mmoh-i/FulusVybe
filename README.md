FulusVybe: Your Snarky Solana Sidekick 🚀
Welcome to FulusVybe, a Telegram bot that dishes out Solana blockchain analytics with a side of sass! Powered by Vybe’s API, FulusVybe roasts wallets, tracks token prices, and streams live DEX trades, all wrapped in a sleek, menu-driven interface. Whether you’re a crypto newbie or a DeFi degenerate, this bot makes diving into Solana’s chaos fun, fast, and insightful. Built for a hackathon, FulusVybe showcases real-time blockchain data with a user experience that’s as smooth as a Raydium swap.
Motivation
Why settle for boring blockchain explorers when you can have a bot that roasts your wallet like a stand-up comedian? FulusVybe was born to make Solana analytics accessible and entertaining. Leveraging Vybe’s robust API, we aimed to create a Telegram bot that delivers:

Real-time insights: Live trades from DEXs like Orca, Raydium, and Meteora.
Humor-driven UX: Witty “wallet roasts” powered by Grok’s AI.
Ease of use: Intuitive menus and buttons for seamless navigation.
Hackathon swagger: A polished, scalable project to wow judges.

Features
FulusVybe is packed with features to keep you glued to your Telegram chat:

Wallet Roasts (/wallet → Analyze Wallet):

Fetches token balances, historical performance, and NFT holdings.
Generates hilarious insights using Grok’s AI (e.g., “Your Pigga tokens are just chilling, waiting for their big break!”).
Metrics: Token amounts, USD values, portfolio value changes, NFT counts.


Token Insights (/tokens):

List Tokens: Displays top Solana tokens with mint addresses and supply.
Token Price: Shows 30-day price history (latest price, max price).
Token Holders: Tracks holder counts and changes over time.
Metrics: Prices in USD, supply, holder counts, timestamps.


Trade Tracking (/trades):

Live Trades: Streams real-time trades from DEXs (Orca, Raydium, Meteora, Phoenix, Pump.fun) via WebSocket.
Recent Trades: Lists latest token trades with mint, SOL amount, and price.
Program Trends: Shows active user trends for DEX programs.
Metrics: Trade amounts, prices, timestamps, user counts.


Snarky UX:

Inline keyboard menus for easy navigation (e.g., [💼 Wallet Tools] [📊 Token Info]).
Persistent [🏠 Home] [ℹ️ Help] buttons.
Retry options for failed requests and links to https://vybe.fyi.


Robust Error Handling:

Retries API calls with exponential backoff.
Graceful fallback messages (e.g., “Vybe’s servers are playing hide and seek!”).
Detailed logging to websocket_messages.log for debugging.



Installation
Get FulusVybe up and running in minutes with these steps. We’ve made it as easy as buying a memecoin at its peak!
Prerequisites

Python 3.8+: Ensure Python is installed (python3 --version).
Telegram Account: Create a bot via BotFather to get a token.
API Keys:
Vybe API key (get from Vybe).
Grok API key (from xAI).



Steps

Clone the Repository:
git clone https://github.com/your-repo/fulusvybe.git
cd fulusvybe


Install Dependencies:
pip install python-telegram-bot requests langchain-groq python-dotenv websocket-client tenacity


Set Up Environment Variables:Create a .env file in the project root:
VYBE_API_KEY=your_vybe_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GROK_API_KEY=your_grok_api_key
VYBE_API_BASE_URL=https://api.vybenetwork.xyz

Replace your_vybe_api_key, etc., with your actual keys.

Run the Bot:
python3 fulus.py

The bot will connect to Telegram and Vybe’s WebSocket, logging to websocket_messages.log.

Interact:Open Telegram, find your bot (e.g., @FulusVybeBot), and type /start.


Troubleshooting Installation

Module Not Found:
Verify pip is for Python 3: pip3 install python-telegram-bot.
Check python-telegram-bot version (20.x): pip show python-telegram-bot.


API Key Errors:
Ensure .env is correctly formatted (no spaces around =).
Contact Vybe support for API key issues.


Network Issues:
Test connectivity: ping api.vybenetwork.xyz.
Use DNS 8.8.8.8 if needed.



Usage
FulusVybe is designed for effortless navigation. Start with /start and explore via buttons or commands.
Commands

Main Menu:
/start: Shows the main menu with [💼 Wallet Tools] [📊 Token Info] [💸 Trades] [ℹ️ All Commands].


Wallet Tools:
/wallet: Opens wallet options ([🔍 Analyze Wallet]).
/analyze <wallet_address>: Roasts a wallet (e.g., /analyze 88QegP3WTisgqm8sfjcGqcFVYqXZ3wXnERGNHBMuTBJu).


Token Info:
/tokens: Shows token options ([🪙 List Tokens] [📈 Token Price] [👥 Token Holders]).
/price <token_mint>: Gets price history (e.g., /price So11111111111111111111111111111111111111112).
/token_holders <token_mint>: Shows holder stats.


Trades:
/trades: Opens trade options ([🔥 Live Trades] [📜 Recent Trades] [📉 Program Trends]).
/token_trades: Lists recent trades.
/program_trends <program_address>: Shows user trends (e.g., /program_trends 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8).
/live: Streams live DEX trades (select Orca, Raydium, etc.).



Navigation

Buttons:
[🏠 Home]: Returns to /start menu.
[ℹ️ Help]: Links to https://vybe.fyi.
[↩️ Back to DEXs]: Reopens DEX selection in /live.
[🔄 Retry]: Retries failed requests.


Text Input:
After clicking [🔍 Analyze Wallet], enter a wallet address directly (no /analyze needed).



Metrics and Examples
FulusVybe delivers a range of blockchain metrics, all spiced up with humor. Below are examples of outputs and the metrics provided.
1. Wallet Roast (/analyze)
Command: /wallet → [🔍 Analyze Wallet] → 88QegP3WTisgqm8sfjcGqcFVYqXZ3wXnERGNHBMuTBJuOutput:
**Wallet Roast for: 88QegP3WTisgqm8sfjcGqcFVYqXZ3wXnERGNHBMuTBJu**

**Current Token Holdings**
SOL: 2.3456 ($56.78)
USDC: 50.0000 ($50.00)
Pigga: 1000.0000 ($0.00)
Craving token analytics? Check Vybe: https://vybe.fyi

**Portfolio Value Change**
No history to spill—your wallet’s a blank slate!

**NFT Holdings**
No NFTs—guess you’re not into digital bling yet!

**Hot Takes**
Your wallet’s got SOL, USDC, and some Pigga—talk about a farm-to-table portfolio! That zero-value Pigga’s just chilling, waiting for its big break. Craving more wallet wisdom? Hit up Vybe at https://vybe.fyi!
[🏠 Home] [ℹ️ Help]

Metrics:

Token Balances: Token symbols, amounts, USD values.
Portfolio Change: Value change in USD (if historical data exists).
NFT Holdings: Count and total USD value.
Insights: AI-generated commentary.

2. Token Price (/price)
Command: /tokens → [📈 Token Price] → So11111111111111111111111111111111111111112Output:
**30-day Price History for So1111...**
Latest: $145.23
Max: $152.67
More on Vybe: https://vybe.fyi
[🏠 Home] [ℹ️ Help]

Metrics:

Latest Price: Current price in USD.
Max Price: Highest price in 30 days.

3. Live Trades (/live)
Command: /trades → [🔥 Live Trades] → [Raydium]Output (Success):
**Live Raydium Trades**
Token: EPjFWd..., Amount: 1.5000, From: 7xKXtf..., To: N/A, Time: 2025-04-17 14:30:45, Tx: 5fXj9k...
Token: JUPxZy..., Amount: 0.2500, From: 9pLmnq..., To: 3kYvab..., Time: 2025-04-17 14:30:46, Tx: 8gHm2p...
Token: So1111..., Amount: 10.0000, From: 4tRwvb..., To: 6sQzcd..., Time: 2025-04-17 14:30:47, Tx: 2kLn3m...
For more real-time action, visit Vybe: https://vybe.fyi
[↩️ Back to DEXs]
[🏠 Home] [ℹ️ Help]

Output (No Trades):
No live Raydium trades captured yet—try again soon!
Check https://docs.vybenetwork.com/docs/real-time-trades for details.
For more real-time updates, visit Vybe: https://vybe.fyi
[🔄 Retry] [↩️ Back to DEXs]
[🏠 Home] [ℹ️ Help]

Metrics:

Trade Details: Token mint, amount, sender/receiver, timestamp, transaction ID.

4. Token List (/tokens → [🪙 List Tokens])
Output:
**Token List**
1. Pigga (Black Pig): 2JJNLqbJ... - Supply: 1,000,000,000
2. Deepseek (Deepseek AI Kit): 5Rkq44zz... - Supply: 1,000,000,000
3. JACK (Official Jack Dorsey): 4xkex6B1... - Supply: 1,000,000,000
4. Atomic (Atomic AI): 9PRUXbLT... - Supply: 999,996,423.345256
5. HUBERT (Hubert Skeletrix): DHcFZj31... - Supply: 1,000,000,000
See more tokens on Vybe: https://vybe.fyi
[🏠 Home] [ℹ️ Help]

Metrics:

Token Info: Symbol, name, mint address, current supply.

5. Token Holders (/token_holders)
Command: /tokens → [👥 Token Holders] → So11111111111111111111111111111111111111112Output:
**Token Holders for So1111...**
Latest (2025-04-17): 123456 holders
Change: +789 holders
More holder stats on Vybe: https://vybe.fyi
[🏠 Home] [ℹ️ Help]

Metrics:

Holder Count: Number of holders.
Change: Difference from previous period.

Technical Details

Language: Python 3.8+.
Libraries:
python-telegram-bot: Telegram bot framework.
requests, websocket-client: For Vybe API and WebSocket.
langchain-groq: Grok AI for insights.
python-dotenv: Environment variable management.
tenacity: API retry logic.


APIs:
Vybe API (https://api.vybenetwork.xyz): Wallet data, token info, trades.
WebSocket (wss://api.vybenetwork.xyz/live): Live trades.
Grok API: Humorous insights.


DEX Support:
Orca: 9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP
Raydium: 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8
Meteora: Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB
Phoenix: PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY
Pump.fun: 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P



Debugging
If things go sideways, here’s how to troubleshoot like a pro:
/live Shows “No live trades captured yet”

Check Logs:

Open websocket_messages.log.
Verify:
Sent configuration for raydium: {...} with correct programId.
Raw WebSocket message: {...} with signature, mintAddress, or txId.


Share 2–3 raw messages with Vybe support.


Test WebSocket:
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
            "trades": [
                {
                    "programId": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
                    "marketId": ""
                }
            ],
            "transfers": [],
            "oraclePrices": []
        }
    }
    ws.send(json.dumps(config))
    print(f"Sent: {config}")

ws = websocket.WebSocketApp(
    "wss://api.vybenetwork.xyz/live",
    header={"x-api-key": "your_vybe_api_key"},
    on_open=on_open,
    on_message=on_message,
    on_error=on_error
)
ws.run_forever()


Run: python3 test_ws.py
Check for trade messages.


Contact Vybe:

Provide: API key, websocket_messages.log, endpoint (wss://api.vybenetwork.xyz/live).
Request: Sample trade message, endpoint status.



Other Issues

API Errors:
Add logging in fetch_wallet_data:logger.info(f"Token balances for {wallet_address}: {response.json()}")


Check .env for correct keys.


Bot Not Responding:
Verify Telegram token with BotFather.
Restart: python3 fulus.py.


Pylance Errors:
Ensure python-telegram-bot version 20.x: pip install python-telegram-bot --upgrade.
Select correct Python interpreter in VS Code.



Future Enhancements
FulusVybe is just the beginning. Here’s what’s on the horizon:

Portfolio Tracking: Monitor wallet changes with alerts.
Advanced Analytics: Token volume trends, whale activity.
Multi-Chain Support: Expand to Ethereum, Polygon.
Voice Mode: Integrate Grok’s voice mode for audio roasts.
Custom Alerts: Notify users of price spikes or trade events.

Contributing
Want to make FulusVybe even sassier? Fork the repo, submit a PR, or open an issue! Check CONTRIBUTING.md for guidelines. Join the fun at https://vybe.fyi!
License
MIT License. See LICENSE for details.
Acknowledgments

Vybe: For their stellar API and real-time data.
xAI: For Grok’s witty AI.
Hackathon judges: For inspiring us to build something epic!


Craving more blockchain banter? Hit up Vybe at https://vybe.fyi and vibe with FulusVybe! 😎
