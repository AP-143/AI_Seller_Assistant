"""Gemini API wrapper: text and image generation."""
import json
from concurrent.futures import ThreadPoolExecutor
import httpx
from google import genai
from google.genai import types
import config

_client = genai.Client(api_key=config.GEMINI_API_KEY)
MODEL = "gemini-3.6-flash"
IMAGE_MODEL = "gemini-3.1-flash-lite-image"


def generate(system: str, prompt: str, max_tokens: int = 1024) -> str:
    resp = _client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={"system_instruction": system, "max_output_tokens": max_tokens},
    )
    return resp.text


def generate_json(system: str, prompt: str, schema: dict, max_tokens: int = 1024) -> dict:
    """Structured output — schema-conformant dict, no manual text parsing."""
    resp = _client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "system_instruction": system,
            "max_output_tokens": max_tokens,
            "response_mime_type": "application/json",
            "response_schema": schema,
        },
    )
    if resp.candidates[0].finish_reason == types.FinishReason.MAX_TOKENS:
        raise RuntimeError(
            f"generate_json truncated by max_tokens={max_tokens} before finishing "
            "(model spent part of the budget on hidden reasoning tokens) — raise max_tokens"
        )
    return json.loads(resp.text)


PRODUCT_INFO_SCHEMA = {
    "type": "object",
    "properties": {
        "product_name": {
            "type": "string",
            "description": "The product name exactly as written in the caption (verbatim substring, don't shorten or rephrase it) — with only price and category words removed",
        },
        "category": {
            "type": "string",
            "description": "Product category in short Indonesian marketplace terms (e.g. 'gaming', 'tas wanita'), inferred if not stated explicitly",
        },
        "cost_price": {
            "type": "integer",
            "description": "Cost/modal price in plain Rupiah integer, no currency symbol or separators. 0 if not mentioned anywhere in the text.",
        },
    },
    "required": ["product_name", "category", "cost_price"],
}


def parse_product_caption(caption: str) -> dict:
    """Free-form caption -> {product_name, category, cost_price}, for callers
    whose caption doesn't match the fast literal 'Nama | Kategori | Harga' parse."""
    system = (
        "Extract product name, category, and cost price (harga modal, in Rupiah) "
        "from this Indonesian Telegram caption. The caption is free-form text, "
        "not a fixed format."
    )
    return generate_json(system, caption, PRODUCT_INFO_SCHEMA, max_tokens=1024)


def _generate_one_photo(image_bytes: bytes, prompt: str) -> bytes:
    resp = _client.models.generate_content(
        model=IMAGE_MODEL,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            prompt,
        ],
    )
    for part in resp.candidates[0].content.parts:
        if part.inline_data:
            return part.inline_data.data
    raise RuntimeError("Gemini image gen returned no image")


def generate_product_photos(image_url: str, product_name: str, category: str, n: int = 3) -> list[bytes]:
    """Send raw product photo, get back N studio-look photo variants (PNG bytes).

    Prompt gives the model a role and a goal, not a fixed visual checklist —
    background/lighting/angle choices are the model's own professional
    judgment, adapted to what this specific product category actually needs.
    See .claude/skills/gemini-prompting/SKILL.md for why.

    candidate_count isn't supported for this image model (API rejects it with
    "Multiple candidates is not enabled for this model"), so N separate calls
    run in parallel instead of one call with N candidates.
    """
    image_bytes = httpx.get(image_url).content
    prompt = (
        "You are a professional e-commerce product photo editor working for an "
        f"Indonesian UMKM seller. Attached is a raw, unedited photo of a "
        f"{product_name} (category: {category}) that needs to become an "
        "upload-ready photo for a Shopee/Tokopedia/TikTok Shop listing. "
        "Use your own professional judgment for background, lighting setup, "
        "camera angle, composition, and color grading — whatever a real "
        "product photographer would choose for this specific kind of product "
        "to make it look premium and sell well, not a generic one-size-fits-all "
        "treatment. The only hard constraint: the product itself must stay "
        "exactly as it is in the attached photo — same shape, color, material, "
        "texture, logo, and proportions, no redesign, no added or removed "
        "parts. Only the environment, lighting, and framing may change. No "
        "added text, watermark, or extra objects in frame."
    )
    with ThreadPoolExecutor(max_workers=n) as pool:
        return list(pool.map(lambda _: _generate_one_photo(image_bytes, prompt), range(n)))
