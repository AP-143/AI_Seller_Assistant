# AI Seller Assistant

Telegram bot for Indonesian UMKM sellers. Send a product photo + short info,
get back: studio-look photo, marketplace listing text, 3 promo captions,
and a suggested price range.

## Demo

Raw photo in, before any editing:

<img src="docs/before.jpg" width="300" alt="Raw product photo before enhancement">

Full bot output for the same product — 3 studio-look photo variants, listing
title/description/price, and promo captions:

![Bot output: photos, listing, price, captions](docs/demo.png)

The 3 generated studio-look variants:

<img src="docs/variant1.jpg" width="200" alt="Generated studio-look variant 1"> <img src="docs/variant2.jpg" width="200" alt="Generated studio-look variant 2"> <img src="docs/variant3.jpg" width="200" alt="Generated studio-look variant 3">

## Stack

Python, LangGraph, Gemini (text + image), Tavily (competitor price search),
Supabase, Railway.

## Structure

```
main.py                  entrypoint, runs the bot
config.py                env vars
bot/handlers.py          telegram handlers (photo in, results out)
graph/                   LangGraph state + nodes + workflow
services/gemini_client.py   Gemini API (text gen + image gen)
services/tavily_client.py   Tavily (competitor price search)
services/supabase_client.py Supabase client
tests/test_parsing.py    self-check for the Telegram caption format parser
```

## Flow

```
START ──> enhance_photo ────────┐
      └─> check_competitor_price┴──> generate_listing ──> generate_captions ──> END
```

## Run locally

```
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
python main.py
```

## User flow (Telegram)

Send a photo with caption: `Nama Produk | Kategori | Harga Modal`
Example: `Tas Rajut Mini | Tas Wanita | 45000`
