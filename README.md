# FulusVybe: The Snarkiest Solana Sidekick You’ll Ever Meet 🌟

Welcome to **FulusVybe**, the Telegram bot that’s equal parts savage, smart, and Solana-obsessed. Powered by Vybe’s cutting-edge API, this bot doesn’t just fetch blockchain data—it roasts your wallet, tracks tokens with attitude, and dishes out live trade updates like a pro. Built for the crypto-curious and the DeFi die-hards, FulusVybe turns the chaos of Solana into a vibe you can’t resist.

---

## Table of Contents

- What’s the Vibe?
- Features That Slap
- Setup (No Excuses)
- How to Use This Beast
- Metrics That Matter
- Examples to Prove It
- When Things Go Sideways
- Join the Vybe

---

## What’s the Vibe?

FulusVybe is your snarky guide to the Solana blockchain. Tired of boring bots spitting out dry stats? This one’s got personality. It’s here to:

- **Roast your wallet** with brutal honesty.
- **Track tokens** like a hawk with a sense of humor.
- **Serve live trades** from Solana’s wildest DEXs.
- **Make you laugh** while you learn the ropes.

Built with Vybe’s API, FulusVybe is fast, fierce, and fun. Whether you’re chasing gains or just vibing, this bot’s got your back.

---

## Features That Slap

FulusVybe doesn’t mess around. Here’s what it brings to the table:

- **💰 Wallet Roast**: Analyzes your holdings, NFTs, and portfolio—then drags you for it.
- **📈 Token Tracker**: Lists tokens, their 30-day price history, and holder stats.
- **⚡ Live Trades**: Real-time updates from DEXs like Orca, Raydium, and Pump.fun.
- **📉 Trade Insights**: Recent trades and program trends, no fluff.
- **🖱️ Easy Navigation**: Buttons for Home, Help, and everything in between.

Every feature’s wrapped in snark and served with a side of Solana swagger.

---

## Setup (No Excuses)

Getting FulusVybe running is easier than explaining NFTs to your grandma. Here’s the deal:

### What You Need

- **Python 3.9+**: Because we’re not stuck in 2015.
- **Telegram Bot Token**: Snag one from BotFather.
- **Vybe API Key**: Grab it from Vybe.
- **Groq API Key**: Optional, but it’s what fuels the snark (get it from Groq).

### Steps to Glory

1. **Clone the Repo**:

   ```bash
   git clone https://github.com/yourusername/fulusvybe.git
   cd fulusvybe
   ```

2. **Install the Goods**:

   ```bash
   pip install python-telegram-bot requests langchain-groq python-dotenv websocket-client tenacity
   ```

3. **Set Up Your Secrets**: Create a `.env` file in the root directory:

   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_token_here
   VYBE_API_KEY=your_vybe_api_key_here
   GROK_API_KEY=your_groq_api_key_here
   VYBE_API_URL=https://api.vybenetwork.xyz
   ```

4. **Launch the Beast**:

   ```bash
   python fulus.py
   ```

5. **Say Hi**:

   - Find your bot on Telegram and hit `/start`. Done.

---

## How to Use This Beast

FulusVybe is all about keeping it simple. Here’s how to vibe with it:

### Kick Things Off

- **/start**: Drops you into the main menu:

  ```
  Yo, what’s the vibe? Pick your poison:
  [💰 Wallet Roast] [📈 Token Tracker]
  [⚡ Live Trades] [📉 Trade Insights]
  [🏠 Home] [ℹ️ Help]
  ```

### Dig Into Features

- **💰 Wallet Roast**: Punch in a wallet address and brace yourself.
- **📈 Token Tracker**: Pick from token lists, price history, or holder stats.
- **⚡ Live Trades**: Choose a DEX and watch the action unfold.
- **📉 Trade Insights**: Get the latest trades or program trends.

### Stay on Track

- Every reply has **\[🏠 Home\]** and **\[ℹ️ Help\]** buttons. No getting lost here.

---

## Metrics That Matter

FulusVybe isn’t just talk—it delivers data that actually means something:

### Wallet Vibes

- **Holdings**: SOL, USDC, and meme coins, with USD values.
- **Portfolio Trends**: How your stash has grown (or tanked).
- **NFTs**: What digital flexes you’ve got.

### Token Talk

- **Token List**: Names, mints, and total supply.
- **Price History**: 30-day highs, lows, and drama.
- **Holders**: Who’s holding and how many.

### Trade Heat

- **Live Trades**: Token, amount, and timestamp from top DEXs.
- **Recent Trades**: What just went down.
- **Program Trends**: Who’s active and where.

This is Solana, unfiltered and ready to roll.

---

## Examples to Prove It

Seeing is believing. Here’s FulusVybe flexing its stuff:

### Wallet Roast

- **Command**: `/analyze 7xKXtf...`

- **Response**:

  ```
  **Wallet Roast: 7xKXtf...**
  SOL: 1.23 ($29.50) | USDC: 10 ($10) | ShibaSol: 5000 ($0.02)
  **Portfolio**: Up 2%—congrats, you’re not totally broke!
  **NFTs**: 1 sad pixel cat. Better luck next drop.
  **Vybe Take**: You’re holding ShibaSol? Bold or just clueless. Dig deeper at https://vybe.fyi.
  [🏠 Home] [ℹ️ Help]
  ```

### Live Trades

- **Command**: Select \[Orca\] from `/live`

- **Response**:

  ```
  **Orca Live Trades**
  - SOL/USDC | 0.5 SOL | From: 3kYv... | To: 6sQz... | 14:32:01
  - JUP/SOL | 2 JUP | From: 9pLm... | To: N/A | 14:32:02
  More action at https://vybe.fyi!
  [🔙 Back] [🏠 Home] [ℹ️ Help]
  ```

### Token Tracker

- **Command**: Click \[📈 Price History\] for “JACK”

- **Response**:

  ```
  **JACK Price History (30 Days)**
  - Day 1: $0.05 | Day 15: $0.07 | Today: $0.06
  **Trend**: Sideways like your trading skills.
  Check Vybe for more: https://vybe.fyi
  [🏠 Home] [ℹ️ Help]
  ```

---

## When Things Go Sideways

Even the best bots hiccup. Here’s how to fix it:

### No Trades Showing

- **Problem**: WebSocket’s napping.
- **Fix**: Check `trade_logs.txt` for clues. Retry with \[🔄 Retry\] or switch DEXs.

### API Errors

- **Problem**: Vybe’s API is moody.
- **Fix**: Test `curl https://api.vybenetwork.xyz`. If it’s down, chill and try later.

### Snark’s Missing

- **Problem**: Groq API key’s AWOL.
- **Fix**: Add it to `.env` or enjoy the silence.

Still stuck? Hit **\[ℹ️ Help\]** or bug the Vybe crew at https://vybe.fyi.

---

## Join the Vybe

FulusVybe is open-source and begging for your genius. Want in?

- **Fork It**: Grab the repo and go wild.
- **Tweak It**: Add features or squash bugs.
- **PR It**: Send a pull request and join the legend.

Let’s make this bot the MVP of Solana. You’re the key—don’t sleep on it!

---

**Ready to vibe harder? Check Vybe at https://vybe.fyi!**