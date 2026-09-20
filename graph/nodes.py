from graph.state import SellerState
from services import gemini_client, tavily_client


def enhance_photo(state: SellerState) -> dict:
    photos = gemini_client.generate_product_photos(
        state["photo_url"], state["product_name"], state["category"]
    )
    return {"enhanced_photo_urls": photos}


def check_competitor_price(state: SellerState) -> dict:
    data = tavily_client.search_competitor_prices(state["product_name"], state["category"])
    return {"competitor_data": data}


LISTING_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Listing title, max 100 characters, SEO-friendly, Indonesian marketplace style",
        },
        "description": {
            "type": "string",
            "description": "Paste-ready product description: feature bullets, then a short paragraph",
        },
        "price_range": {
            "type": "string",
            "description": "Recommended sell price range in Rupiah, with a one-line reason based on cost price and competitor data",
        },
    },
    "required": ["title", "description", "price_range"],
}

CAPTIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "captions": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 3,
            "description": "3 distinct promo captions for Instagram/TikTok, max 150 words each, light emoji use, relevant hashtags",
        },
    },
    "required": ["captions"],
}


def generate_listing(state: SellerState) -> dict:
    system = "You are an Indonesian e-commerce copywriter for Shopee/Tokopedia/TikTok Shop."
    prompt = f"""Produk: {state['product_name']}
Kategori: {state['category']}
Harga modal: Rp{state['cost_price']:,}
Data kompetitor (mentah, hasil pencarian web):
{state['competitor_data']}"""
    result = gemini_client.generate_json(system, prompt, LISTING_SCHEMA, max_tokens=2048)
    return {
        "listing_title": result["title"],
        "listing_description": result["description"],
        "price_range": result["price_range"],
    }


def generate_captions(state: SellerState) -> dict:
    system = "You are a social media copywriter for Indonesian UMKM sellers."
    prompt = f"""Produk: {state['product_name']} ({state['category']})
Deskripsi: {state['listing_description']}"""
    result = gemini_client.generate_json(system, prompt, CAPTIONS_SCHEMA, max_tokens=2048)
    return {"captions": result["captions"]}
