# AI Seller Assistant

Telegram bot for Indonesian UMKM sellers. Send a product photo + short info,
get back: studio-look photo, marketplace listing text, 3 promo captions,
and a suggested price range.

![Demo](docs/demo.png)

## Structure

```
main.py                  entrypoint, runs the bot
config.py                env vars
bot/handlers.py          telegram handlers (photo in, results out)
graph/state.py           LangGraph state schema
graph/nodes.py           4 nodes: enhance_photo, check_competitor_price,
                          generate_listing, generate_captions
graph/workflow.py        wires nodes into a graph, exposes run()
services/gemini_client.py     Gemini API (text gen + Nano Banana image gen)
services/tavily_client.py     Tavily (competitor price search)
services/supabase_client.py   Supabase — NOT wired into the flow yet
tests/test_parsing.py    self-check for the Telegram caption format parser
```

## Flow

```
START ──> enhance_photo ────────┐
      └─> check_competitor_price┴──> generate_listing ──> generate_captions ──> END
```

Photo enhance and price check run independently, both feed into listing
generation (needs price data), which feeds captions (needs listing text).

## Run locally

```
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
python main.py
```

## User flow (Telegram)

Send a photo with caption: `Nama Produk | Kategori | Harga Modal`
Example: `Tas Rajut Mini | Tas Wanita | 45000`

## Text generation

`generate_listing` and `generate_captions` use Gemini structured JSON output
(`gemini_client.generate_json`, `response_schema` in `graph/nodes.py`) instead
of parsing marker text (`JUDUL:`/`DESKRIPSI:`/...) or a `---` splitter — the
model returns schema-conformant JSON directly, no manual parsing to break.

## Known gaps (MVP, by design)

- Image gen uses `gemini-2.5-flash-image` (Nano Banana), same Gemini key as text.
  ~$0.039/image. Best product-fidelity/price tradeoff of the models tried
  (gemini-3.1-flash-image and gemini-3-pro-image both altered product details
  more than this one, despite costing more). DEPRECATED 2026-10-02 — Google
  will force-migrate this model off; watch for a replacement announcement and
  re-test before that date. Free tier quota is 0 — billing must be enabled on
  the Google Cloud project tied to the key, or every enhance_photo call 429s.
  Returns 3 PNG variants (raw bytes, no image hosting needed), sent to Telegram
  as an album. `candidate_count` isn't supported for this model, so the 3
  variants are 3 parallel API calls — ~$0.117/request, not $0.039.
- No Supabase persistence wired in — add `log_request()` call in
  `graph/nodes.py` once you need request history or credit tracking.
- No retry/backoff on API calls — add if flaky in practice.
- Deploy to Railway: `Procfile` not needed, Railway auto-detects
  `python main.py` as a worker; set env vars in Railway dashboard.
